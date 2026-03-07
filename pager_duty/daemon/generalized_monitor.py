#!/usr/bin/env python3
import os, sys, time, socket, psutil, urllib.request, subprocess, re, binascii, logging, smtplib, secrets, ssl, json, datetime, platform, shutil
import concurrent.futures
from email.message import EmailMessage

try:
    import psycopg2
except ImportError:
    psycopg2 = None
try:
    import yaml
except ImportError:
    print("[!] PyYAML required for generalized monitor.")
    sys.exit(1)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hams_config import get_odoo_client

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger("generalized_monitor")


def parse_env(val):
    if isinstance(val, str) and val.startswith("ENV:"):
        return os.environ.get(val[4:], "")
    return val


def ensure_executable(cmd_name):
    path = shutil.which(cmd_name)
    if path:
        return path, ""
    return None, f"Missing dependency: '{cmd_name}'. Startup verification failed."


def verify_and_install_dependencies(client, checks):
    type_to_cmd = {
        "dns": "dig",
        "snmp": "snmpget",
        "pg_dump": "pg_dump",
        "nginx": "nginx",
        "certbot": "certbot",
        "logrotate": "logrotate",
        "http3": "curl",
        "icmp": "ping",
        "docker": "docker",
        "systemd": "systemctl",
        "cloudflared": "cloudflared"
    }

    required_cmds = set()
    for check in checks:
        ctype = check.get("type")
        if ctype in type_to_cmd:
            required_cmds.add(type_to_cmd[ctype])

    for cmd in required_cmds:
        if not shutil.which(cmd):
            logger.info(f"Dependency '{cmd}' missing. Polling Odoo...")
            success = False
            for attempt in range(12):
                try:
                    res = client.execute("pager.check", "rpc_ensure_executable", cmd)
                    if res and res.get("status") == "ok":
                        bin_path = res.get("path")
                        logger.info(f"Provisioned {cmd} at {bin_path}")
                        bin_dir = os.path.dirname(bin_path)
                        if bin_dir not in os.environ["PATH"]:
                            os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
                        success = True
                        break
                    else:
                        err_msg = res.get("message")
                        logger.warning(f"Provision failed: {err_msg}")
                except Exception as e:
                    logger.warning(f"RPC unavailable, waiting... ({e})")
                time.sleep(10)  # audit-ignore-sleep

            if not success:
                msg = f"FATAL: Missing dependency '{cmd}'. Halting."
                logger.critical(msg)
                fallback_notify("Daemon Boot", msg, "critical")
                try:
                    client.execute(
                        "pager.incident",
                        "report_incident",
                        {
                            "source": "Daemon Boot",
                            "severity": "critical",
                            "description": msg,
                        },
                    )
                except Exception:
                    pass
                sys.exit(1)


THREAD_HEARTBEATS = {}
THREAD_TIMEOUTS = {}
FAILING_CHECKS = set()


def is_in_maintenance(check):
    maint_start_str = check.get("maint_start")
    maint_end_str = check.get("maint_end")
    if maint_start_str and maint_end_str:
        try:
            start = datetime.datetime.strptime(maint_start_str, "%Y-%m-%d %H:%M:%S")
            end = datetime.datetime.strptime(maint_end_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.utcnow()
            if start <= now <= end:
                return True
        except Exception:
            pass
    return False


def fallback_notify(source, msg, severity):
    fallback_email = os.environ.get("PAGER_FALLBACK_EMAIL")
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    from_email = os.environ.get("SMTP_FROM", "pager-daemon@hams.com")

    if not fallback_email or not smtp_host:
        logger.critical(
            f"SMTP Fallback not configured! Incident lost: {source} - {msg}"
        )
        return

    try:
        em = EmailMessage()
        em.set_content(
            f"CRITICAL INCIDENT: {source}\nSeverity: {severity}\nDetails: {msg}\n\n(Sent via Daemon SMTP Fallback because Odoo RPC failed.)"
        )
        em["Subject"] = f"[Hams.com PAGER] {source} Alert"
        em["From"] = from_email
        em["To"] = fallback_email

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if smtp_port in (587, 465):
                server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(em)
        logger.info("Successfully dispatched SMTP fallback email.")
    except Exception as e:
        logger.critical(f"SMTP Fallback completely failed: {e}")


def report(client, source, msg, severity="high"):
    webhook_url = os.environ.get("PAGER_WEBHOOK_URL")
    if webhook_url:
        try:
            payload = {
                "content": f"🚨 **[Hams.com ALERT]**\n**Source:** {source}\n**Severity:** {severity}\n**Details:** {msg}"
            }
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5):
                pass
        except Exception:
            pass

    try:
        payload = {"source": source, "description": msg, "severity": severity}
        client.execute("ham.pager.incident", "report_incident", payload)
        logger.error(f"Incident reported [{source}]: {msg}")
    except Exception as e:
        logger.error(
            f"Failed to report incident via RPC: {e}. Triggering SMTP fallback."
        )
        fallback_notify(source, msg, severity)


def auto_resolve(client, source):
    try:
        client.execute("ham.pager.incident", "auto_resolve_incidents", source)
        logger.info(f"[{source}] System stable. Auto-resolved open incidents.")
    except Exception as e:
        logger.error(f"Failed to auto-resolve incidents for {source}: {e}")


def execute_check(check, client=None):
    ctype = check.get("type")
    target = parse_env(check.get("target", ""))

    if ctype == "system":
        if target == "disk":
            part = parse_env(check.get("partition", "/"))
            try:
                pct = psutil.disk_usage(part).percent
                if pct > check.get("critical", 90):
                    return False, f"Disk space at {pct}% on {part}"
            except Exception as e:
                return False, f"Disk check failed for {part}: {e}"
        elif target == "memory":
            pct = psutil.virtual_memory().percent
            if pct > check.get("critical", 90):
                return False, f"Memory usage at {pct}%"
        elif target == "cpu":
            pct = psutil.cpu_percent(interval=1)
            if pct > check.get("critical", 90):
                return False, f"CPU usage at {pct}%"
        elif target == "iowait":
            pct = getattr(psutil.cpu_times_percent(interval=1), "iowait", 0)
            if pct > check.get("critical", 90):
                return False, f"CPU IO Wait at {pct}%"
        elif target == "steal":
            pct = getattr(psutil.cpu_times_percent(interval=1), "steal", 0)
            if pct > check.get("critical", 90):
                return False, f"CPU Steal at {pct}%"
        return True, "OK"

    elif ctype == "load":
        try:
            load1, load5, load15 = os.getloadavg()
            crit = check.get("critical", 0)
            if crit > 0 and load1 > crit:
                return False, f"Load average {load1:.2f} exceeds {crit}"
            return True, f"OK (Load: {load1:.2f})"
        except Exception as e:
            return False, f"Load check failed: {e}"

    elif ctype == "ftp":
        import ftplib
        port = int(parse_env(check.get("port", 21)))
        user = parse_env(check.get("user", ""))
        password = parse_env(check.get("password", ""))
        try:
            with ftplib.FTP() as ftp:
                ftp.connect(target, port, timeout=5)
                if user and password:
                    ftp.login(user, password)
                else:
                    ftp.login()
            return True, "OK"
        except Exception as e:
            return False, f"FTP check failed: {e}"

    elif ctype == "imap":
        import imaplib
        port = int(parse_env(check.get("port", 143)))
        user = parse_env(check.get("user", ""))
        password = parse_env(check.get("password", ""))
        try:
            if port == 993:
                imap = imaplib.IMAP4_SSL(target, port, timeout=5)
            else:
                imap = imaplib.IMAP4(target, port, timeout=5)
            if user and password:
                imap.login(user, password)
            imap.logout()
            return True, "OK"
        except Exception as e:
            return False, f"IMAP check failed: {e}"

    elif ctype == "pop3":
        import poplib
        port = int(parse_env(check.get("port", 110)))
        user = parse_env(check.get("user", ""))
        password = parse_env(check.get("password", ""))
        try:
            if port == 995:
                pop = poplib.POP3_SSL(target, port, timeout=5)
            else:
                pop = poplib.POP3(target, port, timeout=5)
            if user and password:
                pop.user(user)
                pop.pass_(password)
            pop.quit()
            return True, "OK"
        except Exception as e:
            return False, f"POP3 check failed: {e}"

    elif ctype == "mysql":
        port = int(parse_env(check.get("port", 3306)))
        user = parse_env(check.get("user", ""))
        password = parse_env(check.get("password", ""))
        dbname = parse_env(check.get("dbname", ""))
        try:
            import pymysql
            conn = pymysql.connect(
                host=target, port=port, user=user, password=password, database=dbname, connect_timeout=5
            )
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    cur.fetchone()
            finally:
                conn.close()
            return True, "OK"
        except ImportError:
            try:
                with socket.create_connection((target, port), timeout=5) as s:
                    res = s.recv(1024)
                    if len(res) < 5:
                        return False, "Invalid MySQL/MariaDB greeting"
                return True, "OK (Socket fallback)"
            except Exception as e:
                return False, f"MySQL/MariaDB socket fallback failed: {e}"
        except Exception as e:
            return False, f"MySQL/MariaDB check failed: {e}"

    elif ctype == "ldap":
        port = int(parse_env(check.get("port", 389)))
        try:
            import ldap3
            server = ldap3.Server(target, port=port, get_info=ldap3.ALL, connect_timeout=5)
            conn = ldap3.Connection(server, auto_bind=True, receive_timeout=5)
            conn.unbind()
            return True, "OK"
        except ImportError:
            try:
                with socket.create_connection((target, port), timeout=5):
                    pass
                return True, "OK (Socket fallback)"
            except Exception as e:
                return False, f"LDAP socket fallback failed: {e}"
        except Exception as e:
            return False, f"LDAP check failed: {e}"

    elif ctype == "ntp":
        port = int(parse_env(check.get("port", 123)))
        try:
            import ntplib
            client = ntplib.NTPClient()
            response = client.request(target, version=3, timeout=5)
            return True, f"OK (Offset: {response.offset:.4f}s)"
        except ImportError:
            # SNTP v4 client request packet
            req = b'\x1b' + 47 * b'\0'
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(5)
                    s.sendto(req, (target, port))
                    data, _ = s.recvfrom(1024)
                    if len(data) < 48:
                        return False, "Invalid NTP response length"
                return True, "OK (UDP fallback)"
            except Exception as e:
                return False, f"NTP UDP fallback failed: {e}"
        except Exception as e:
            return False, f"NTP check failed: {e}"

    elif ctype == "snmp":
        community = parse_env(check.get("snmp_community", "public"))
        oid = parse_env(check.get("snmp_oid", ""))
        exe, err = ensure_executable("snmpget")
        if not exe:
            return False, err
        try:
            res = subprocess.run(
                [exe, "-v2c", "-c", community, target, oid],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode != 0:
                return False, f"SNMP failed: {res.stderr.strip() or res.stdout.strip()[:100]}"
            expect = parse_env(check.get("expect"))
            if expect and expect not in res.stdout:
                return False, "SNMP payload mismatch"
            return True, "OK"
        except Exception as e:
            return False, f"SNMP check error: {e}"

    elif ctype == "dns":
        domain = target
        exe, _ = ensure_executable("dig")
        try:
            if exe:
                result = subprocess.run(
                    [exe, "+trace", domain], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and domain in result.stdout:
                    return True, "OK"
            socket.gethostbyname(domain)
            return True, "OK"
        except Exception as e:
            return False, f"DNS resolution failed: {e}"

    elif ctype == "http":
        try:
            headers = {"User-Agent": "HamMonitor/1.0"}
            req = urllib.request.Request(target, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    body = response.read().decode("utf-8")
                    expect = parse_env(check.get("expect"))
                    if expect and expect not in body:
                        return False, "HTTP body mismatch"
                    return True, "OK"
                return False, f"HTTP status {response.status}"
        except Exception as e:
            return False, f"HTTP check failed: {e}"

    elif ctype == "http3":
        expect = parse_env(check.get("expect"))
        exe, err = ensure_executable("curl")
        if not exe:
            return False, err
        try:
            res = subprocess.run(
                [exe, "-s", "--http3", target],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if res.returncode != 0:
                return False, f"HTTP/3 Curl failed: {res.stderr[:100]}"
            if expect and expect not in res.stdout:
                return False, "HTTP/3 body mismatch"
            return True, "OK"
        except Exception as e:
            return False, f"HTTP/3 check failed: {e}"

    elif ctype == "tcp":
        port = int(parse_env(check.get("port", 80)))
        send_payload = parse_env(check.get("send"))
        send_hex = parse_env(check.get("send_hex"))
        expect = parse_env(check.get("expect"))
        try:
            with socket.create_connection((target, port), timeout=2) as s:
                if send_hex:
                    s.sendall(binascii.unhexlify(send_hex))
                elif send_payload:
                    s.sendall(
                        send_payload.encode("utf-8")
                        .decode("unicode_escape")
                        .encode("utf-8")
                    )

                if expect:
                    response = s.recv(1024)
                    if expect.encode("utf-8") not in response:
                        return False, "TCP payload mismatch"
            return True, "OK"
        except Exception as e:
            return False, f"TCP connection failed: {e}"

    elif ctype == "udp":
        port = int(parse_env(check.get("port", 80)))
        send_payload = parse_env(check.get("send"))
        send_hex = parse_env(check.get("send_hex"))
        expect = parse_env(check.get("expect"))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(2)
                if send_hex:
                    s.sendto(binascii.unhexlify(send_hex), (target, port))
                elif send_payload:
                    s.sendto(
                        send_payload.encode("utf-8")
                        .decode("unicode_escape")
                        .encode("utf-8"),
                        (target, port),
                    )
                else:
                    return False, "UDP check requires a payload to send"

                if expect:
                    response, _ = s.recvfrom(4096)
                    if expect.encode("utf-8") not in response:
                        return False, "UDP payload mismatch"
            return True, "OK"
        except Exception as e:
            return False, f"UDP connection failed: {e}"

    elif ctype == "redis":
        port = int(parse_env(check.get("port", 6379)))
        password = parse_env(check.get("password", ""))
        try:
            import redis as redis_lib

            r = redis_lib.Redis(
                host=target, port=port, password=password or None, socket_timeout=2
            )
            if r.ping():
                return True, "OK"
            return False, "Redis PING returned False"
        except ImportError:
            try:
                with socket.create_connection((target, port), timeout=2) as s:
                    if password:
                        s.sendall(f"AUTH {password}\r\n".encode("utf-8"))
                        s.recv(1024)
                    s.sendall(b"PING\r\n")
                    res = s.recv(1024)
                    if b"+PONG" not in res:
                        return False, "Redis socket PING failed"
                return True, "OK"
            except Exception as e:
                return False, f"Redis socket fallback failed: {e}"
        except Exception as e:
            return False, f"Redis connection failed: {e}"

    elif ctype == "rabbitmq":
        port = int(parse_env(check.get("port", 5672)))
        try:
            with socket.create_connection((target, port), timeout=2) as s:
                s.sendall(b"AMQP\x00\x00\x09\x01")
                res = s.recv(1024)
                if len(res) > 0:
                    return True, "OK"
                return False, "RabbitMQ handshake mismatch"
        except Exception as e:
            return False, f"RabbitMQ connection failed: {e}"

    elif ctype == "xmlrpc":
        import xmlrpc.client

        method = parse_env(check.get("rpc_method", ""))
        params_str = parse_env(check.get("rpc_params", "[]"))
        expect = parse_env(check.get("expect"))
        try:
            params = json.loads(params_str) if params_str else []
            proxy = xmlrpc.client.ServerProxy(target)
            res = getattr(proxy, method)(*params)
            if expect and expect not in str(res):
                return False, "XML-RPC output mismatch"
            return True, "OK"
        except Exception as e:
            return False, f"XML-RPC check failed: {e}"

    elif ctype == "jsonrpc":
        method = parse_env(check.get("rpc_method", ""))
        params_str = parse_env(check.get("rpc_params", "{}"))
        expect = parse_env(check.get("expect"))
        try:
            params = json.loads(params_str) if params_str else {}
            payload = json.dumps(
                {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
            ).encode("utf-8")
            req = urllib.request.Request(
                target,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                body = response.read().decode("utf-8")
                if expect and expect not in body:
                    return False, "JSON-RPC output mismatch"
            return True, "OK"
        except Exception as e:
            return False, f"JSON-RPC check failed: {e}"

    elif ctype == "postgres" or ctype == "anomaly":
        port = int(parse_env(check.get("port", 5432)))
        dbname = parse_env(check.get("dbname", "odoo"))
        user = parse_env(check.get("user", "odoo"))
        password = parse_env(check.get("password", ""))
        query = (
            parse_env(check.get("query", "SELECT 1;"))
            if ctype == "anomaly"
            else "SELECT 1;"
        )

        if psycopg2:
            conn = None
            try:
                conn = psycopg2.connect(
                    host=target,
                    port=port,
                    dbname=dbname,
                    user=user,
                    password=password,
                    connect_timeout=2,
                )
                with conn.cursor() as cur:
                    cur.execute(query)
                    val = cur.fetchone()[0]

                if ctype == "anomaly":
                    critical_min = int(check.get("critical", 0))
                    if val < critical_min:
                        return (
                            False,
                            f"Anomaly Threshold Breached: {val} < {critical_min}",
                        )
                return True, "OK"
            except Exception as e:
                return False, f"PostgreSQL/Anomaly check failed: {e}"
            finally:
                if conn:
                    conn.close()
        else:
            if ctype == "anomaly":
                return False, "psycopg2 required for anomaly queries"
            try:
                with socket.create_connection((target, port), timeout=2):
                    return True, "OK"
            except Exception as e:
                return False, f"PostgreSQL socket fallback failed: {e}"

    elif ctype == "ssl":
        try:
            port = int(parse_env(check.get("port", 443)))
            ctx = ssl.create_default_context()
            with socket.create_connection((target, port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                    cert = ssock.getpeercert()
                    expire_date = datetime.datetime.strptime(
                        cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                    )
                    days_left = (expire_date - datetime.datetime.utcnow()).days
                    critical_days = int(check.get("critical", 14))
                    if days_left <= critical_days:
                        return False, f"SSL Cert expires in {days_left} days"
            return True, "OK"
        except Exception as e:
            return False, f"SSL check failed: {e}"

    elif ctype == "synthetic":
        script = parse_env(check.get("script", ""))
        if not script:
            return False, "Synthetic script path missing"
        try:
            import shlex

            res = subprocess.run(
                shlex.split(script),
                shell=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if res.returncode != 0:
                return (
                    False,
                    f"Synthetic failure (Code {res.returncode}): {res.stderr[:100]}",
                )
            return True, "OK"
        except Exception as e:
            return False, f"Synthetic execution error: {e}"

    elif ctype == "certbot":
        headers = {"User-Agent": "HamMonitor/1.0"}
        try:
            req = urllib.request.Request(
                "https://acme-v02.api.letsencrypt.org/directory", headers=headers
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status != 200:
                    return False, f"Let's Encrypt API unreachable ({response.status})"
        except Exception as e:
            return False, f"Let's Encrypt API unreachable: {e}"

        domains = parse_env(check.get("target", ""))
        if domains and domains != "auto":
            try:
                req = urllib.request.Request("https://api.ipify.org", headers=headers)
                with urllib.request.urlopen(req, timeout=10) as ip_resp:
                    my_ip = ip_resp.read().decode("utf-8").strip()

                domain_list = [d.strip() for d in domains.split(",") if d.strip()]
                for d in domain_list:
                    try:
                        resolved = socket.gethostbyname(d)
                        if resolved != my_ip:
                            return (
                                False,
                                f"Domain {d} resolves to {resolved}, expected our IP {my_ip}.",
                            )
                    except socket.gaierror:
                        return False, f"Domain {d} failed DNS resolution."
            except Exception as e:
                logger.warning(f"Could not verify public IP for domain matching: {e}")

        exe, _ = ensure_executable("certbot")
        if exe:
            try:
                res = subprocess.run(
                    [exe, "renew", "--dry-run"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if res.returncode != 0:
                    failed = [
                        line.strip()
                        for line in (res.stdout + "\n" + res.stderr).split("\n")
                        if "Failed to renew" in line or "Challenge failed" in line
                    ]
                    err_msg = "Certbot dry-run failed!"
                    if failed:
                        err_msg += " " + " | ".join(failed[:2])
                    return False, err_msg
            except subprocess.TimeoutExpired:
                return False, "Certbot dry-run timed out."
            except Exception as e:
                return False, f"Certbot execution error: {e}"

        return True, "OK"

    elif ctype == "pg_dump":
        port = str(parse_env(check.get("port", 5432)))
        dbname = parse_env(check.get("dbname", "odoo"))
        user = parse_env(check.get("user", "odoo"))
        password = parse_env(check.get("password", ""))
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password
        exe, err = ensure_executable("pg_dump")
        if not exe:
            return False, err
        try:
            res = subprocess.run(
                [
                    exe,
                    "-s",
                    "-U",
                    user,
                    "-h",
                    target or "127.0.0.1",
                    "-p",
                    port,
                    dbname,
                ],
                capture_output=True,
                text=True,
                env=env,
                timeout=30,
            )
            if res.returncode != 0:
                return False, f"pg_dump pre-flight failed: {res.stderr[:100]}"
            return True, "OK"
        except Exception as e:
            return False, f"pg_dump execution error: {e}"

    elif ctype == "nginx":
        exe, err = ensure_executable("nginx")
        if not exe:
            return False, err
        try:
            res = subprocess.run(
                [exe, "-t"], capture_output=True, text=True, timeout=15
            )
            if res.returncode != 0:
                return False, f"Nginx config error: {res.stderr[:100]}"
            return True, "OK"
        except Exception as e:
            return False, f"Nginx execution error: {e}"

    elif ctype == "logrotate":
        exe, err = ensure_executable("logrotate")
        if not exe:
            return False, err
        conf = target or "/etc/logrotate.conf"
        try:
            res = subprocess.run(
                [exe, "-d", conf], capture_output=True, text=True, timeout=30
            )
            if res.returncode != 0:
                return False, f"Logrotate dry-run failed: {res.stderr[:100]}"
            return True, "OK"
        except Exception as e:
            return False, f"Logrotate execution error: {e}"

    elif ctype == "cloudflared":
        if not target:
            return False, "Cloudflared requires target (Tunnel ID or Name)"
        exe, err = ensure_executable("cloudflared")
        if not exe:
            return False, err
        try:
            res = subprocess.run(
                [exe, "tunnel", "info", target],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if res.returncode != 0:
                return False, f"Cloudflared tunnel info failed: {res.stderr[:100]}"
            return True, "OK"
        except Exception as e:
            return False, f"Cloudflared execution error: {e}"

    elif ctype == "smtp_dryrun":
        port = int(parse_env(check.get("port", 587)))
        user = parse_env(check.get("user", ""))
        password = parse_env(check.get("password", ""))
        if not target:
            return False, "SMTP dry-run requires target host"
        try:
            with smtplib.SMTP(target, port, timeout=10) as server:
                server.ehlo()
                if port in (587, 465) or server.has_extn("STARTTLS"):
                    server.starttls()
                    server.ehlo()
                if user and password:
                    server.login(user, password)
            return True, "OK"
        except Exception as e:
            return False, f"SMTP dry-run failed: {e}"

    elif ctype == "icmp":
        if not target:
            return False, "ICMP requires target"
        exe, err = ensure_executable("ping")
        if not exe:
            return False, err
        try:
            res = subprocess.run(
                [exe, "-c", "3", "-W", "2", target],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if res.returncode != 0:
                return (
                    False,
                    f"ICMP ping failed: {res.stderr.strip() or res.stdout.strip()[:100]}",
                )
            return True, "OK"
        except Exception as e:
            return False, f"ICMP execution error: {e}"

    elif ctype == "docker":
        if not target:
            return False, "Docker check requires target container name"
        exe, err = ensure_executable("docker")
        if not exe:
            return False, err
        try:
            res = subprocess.run(
                [exe, "inspect", "-f", "{{.State.Running}}", target],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if res.returncode != 0:
                return False, f"Docker inspect failed: {res.stderr.strip()[:100]}"
            if res.stdout.strip().lower() != "true":
                return False, f"Docker container {target} is not running"
            return True, "OK"
        except Exception as e:
            return False, f"Docker execution error: {e}"

    elif ctype == "memcached":
        port = int(parse_env(check.get("port", 11211)))
        if not target:
            return False, "Memcached requires target"
        try:
            with socket.create_connection((target, port), timeout=2) as s:
                s.sendall(b"stats\r\n")
                res = s.recv(1024)
                if b"STAT " not in res:
                    return False, "Memcached stats mismatch"
            return True, "OK"
        except Exception as e:
            return False, f"Memcached connection failed: {e}"

    elif ctype == "ssh":
        port = int(parse_env(check.get("port", 22)))
        if not target:
            return False, "SSH requires target"
        try:
            with socket.create_connection((target, port), timeout=5) as s:
                res = s.recv(1024)
                if not res.startswith(b"SSH-"):
                    return False, "SSH protocol mismatch"
            return True, "OK"
        except Exception as e:
            return False, f"SSH connection failed: {e}"

    elif ctype == "heartbeat":
        chk_uuid = parse_env(check.get("uuid"))
        if not client:
            return False, "Client not provided for heartbeat"
        try:
            res = client.execute(
                "ham.pager.check",
                "check_heartbeat_rpc",
                chk_uuid,
                int(check.get("interval", 60)),
            )
            if res:
                return True, "OK"
            return False, "Heartbeat missing"
        except Exception as e:
            return False, f"Heartbeat check failed: {e}"

    elif ctype == "file_absent":
        if not target:
            return False, "Target required"
        if os.path.exists(target):
            return False, f"File {target} exists"
        return True, "OK"

    elif ctype == "systemd":
        if not target:
            return False, "Systemd check requires service name in target"
        exe, err = ensure_executable("systemctl")
        if not exe:
            return False, err
        try:
            res = subprocess.run(
                [exe, "is-active", target], capture_output=True, text=True, timeout=10
            )
            if res.returncode != 0 or res.stdout.strip() != "active":
                return (
                    False,
                    f"Systemd service {target} is not active: {res.stdout.strip()}",
                )
            return True, "OK"
        except Exception as e:
            return False, f"Systemd execution error: {e}"

    return False, "Unknown check type"


def polling_thread(client, check):
    name = check.get("name", "Unknown")
    interval = int(check.get("interval", 60))
    grace = int(check.get("grace", 0))
    thread_start_time = time.time()

    # Give the thread 3x its interval or at least 5 minutes before we consider it dead
    THREAD_TIMEOUTS[name] = max(300, interval * 3)
    logger.info(
        f"Starting polling thread for [{name}] every {interval}s (Grace: {grace}s)"
    )

    # Do all monitoring once immediately at startup
    THREAD_HEARTBEATS[name] = time.time()
    success, msg = execute_check(check, client)
    clean_loops = 1 if success else 0
    if not success:
        FAILING_CHECKS.add(name)
        if time.time() - thread_start_time < grace:
            logger.info(
                f"[{name}] Startup grace period active. Suppressing failure: {msg}"
            )
        else:
            report(client, name, msg, "high")
            remedy = check.get("remediate")
            if clean_loops > 0 and remedy and os.path.exists(remedy):
                logger.info(f"[{name}] Triggering auto-remediation script: {remedy}")
                try:
                    subprocess.Popen([remedy], shell=False)
                except Exception as e:
                    logger.error(f"Remediation failed: {e}")
    else:
        FAILING_CHECKS.discard(name)

    # Apply stochastic jitter before entering the main cycle to prevent thundering herds
    jitter = secrets.SystemRandom().uniform(0, interval)
    logger.info(f"[{name}] Applying startup jitter: sleeping for {jitter:.1f}s")
    time.sleep(jitter)  # audit-ignore-sleep

    while True:
        THREAD_HEARTBEATS[name] = time.time()
        parent = check.get("parent")

        if is_in_maintenance(check):
            time.sleep(interval)  # audit-ignore-sleep
            continue

        if parent and parent in FAILING_CHECKS:
            logger.debug(f"[{name}] Suppressed due to parent '{parent}' failure.")
            time.sleep(interval)  # audit-ignore-sleep
            continue

        success, msg = execute_check(check, client)
        if not success:
            FAILING_CHECKS.add(name)
            if time.time() - thread_start_time < grace:
                logger.info(
                    f"[{name}] Startup grace period active. Suppressing failure: {msg}"
                )
            else:
                report(client, name, msg, "high")
                remedy = check.get("remediate")
                if clean_loops > 0 and remedy and os.path.exists(remedy):
                    logger.info(
                        f"[{name}] Triggering auto-remediation script: {remedy}"
                    )
                    try:
                        subprocess.Popen([remedy], shell=False)
                    except Exception as e:
                        logger.error(f"Remediation failed: {e}")
            clean_loops = 0
        else:
            FAILING_CHECKS.discard(name)
            clean_loops += 1
            if clean_loops == 3:
                auto_resolve(client, name)
        time.sleep(interval)  # audit-ignore-sleep


def log_tail_thread(client, check):
    name = check.get("name", "Log Monitor")
    filepath = parse_env(check.get("target", ""))
    regex_str = parse_env(check.get("regex", ""))
    grace = int(check.get("grace", 0))
    thread_start_time = time.time()

    # Log tail checks continuously; if it hangs for 2 minutes, something is deeply wrong
    THREAD_TIMEOUTS[name] = 120
    logger.info(
        f"Starting log tail thread for [{name}] on {filepath} (Grace: {grace}s)"
    )

    cur_inode = None
    f = None
    while True:
        THREAD_HEARTBEATS[name] = time.time()
        try:
            stat = os.stat(filepath)
            new_inode = stat.st_ino
            if cur_inode != new_inode:
                if f:
                    f.close()
                f = open(filepath, "r")
                if cur_inode is None:
                    # First run: start from the end to avoid alerting on historical data
                    f.seek(0, 2)
                else:
                    # File rotated: start from the absolute beginning to catch all new lines
                    f.seek(0, 0)
                cur_inode = new_inode
                logger.info(f"Tailing log file {filepath} (inode: {cur_inode})")
            if f:
                line = f.readline()
                if not line:
                    time.sleep(1)  # audit-ignore-sleep
                    continue
                if regex_str and re.search(regex_str, line, re.IGNORECASE):
                    if time.time() - thread_start_time < grace:
                        logger.info(
                            f"[{name}] Suppressed log alert during grace period."
                        )
                    else:
                        report(client, name, line.strip(), "critical")
            else:
                time.sleep(1)  # audit-ignore-sleep
        except FileNotFoundError:
            time.sleep(5)  # audit-ignore-sleep
            continue


if __name__ == "__main__":
    client = get_odoo_client(logger)
    config_path = os.path.join(os.path.dirname(__file__), "pager_config.yaml")

    if not os.path.exists(config_path):
        logger.critical(f"Configuration file not found at {config_path}. Halting.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    checks = config.get("checks", [])
    logger.info(f"Loaded {len(checks)} checks from configuration.")

    verify_and_install_dependencies(client, checks)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(checks)))
    futures = []
    for check in checks:
        if check.get("type") == "log":
            futures.append(executor.submit(log_tail_thread, client, check))
        else:
            futures.append(executor.submit(polling_thread, client, check))

    # Main thread becomes the Watchdog
    try:
        while True:
            time.sleep(10)  # audit-ignore-sleep
            now = time.time()
            for t_name, last_beat in THREAD_HEARTBEATS.items():
                timeout = THREAD_TIMEOUTS.get(t_name, 300)
                if now - last_beat > timeout:
                    logger.critical(
                        f"WATCHDOG: Thread '{t_name}' hung for {now - last_beat:.1f}s (Timeout: {timeout}s)! Force restarting daemon."
                    )
                    os._exit(
                        1
                    )  # OS-level exit forces systemd/docker to cleanly respawn the daemon
    except KeyboardInterrupt:
        logger.info("Shutting down monitoring daemon.")
