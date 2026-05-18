import os
import re

filepath = 'pager_duty/daemon/generalized_monitor.py'
with open(filepath, 'r') as f:
    content = f.read()

# I will use a list of simple replacements for the exact strings.
# This is safer than regex.

reps = [
    ('except Exception as e: # audit-ignore-catch-all\n            logger.warning("Failed to query Odoo databases: %s", e)',
     'except (urllib.error.URLError, json.JSONDecodeError, socket.timeout) as e:\n            logger.warning("Failed to query Odoo databases: %s", e)'),

    ('try:\n        return OdooClient(url, db, user, password)\n    except Exception as e: # audit-ignore-catch-all',
     'try:\n        return OdooClient(url, db, user, password)\n    except (ValueError, KeyError) as e:'),

    ('logger.warning(f"Provision failed: {err_msg}")\n                except Exception as e: # audit-ignore-catch-all',
     'logger.warning(f"Provision failed: {err_msg}")\n                except (urllib.error.URLError, json.JSONDecodeError) as e:'),

    ('"description": msg,\n                    },\n                )\n            except Exception as e: # audit-ignore-catch-all',
     '"description": msg,\n                    },\n                )\n            except (urllib.error.URLError, json.JSONDecodeError) as e:'),

    ('if start <= now <= end:\n                return True\n        except Exception as e: # audit-ignore-catch-all',
     'if start <= now <= end:\n                return True\n        except ValueError as e:'),

    ('server.send_message(em)\n        logger.info("Successfully dispatched SMTP fallback email.")\n    except Exception as e: # audit-ignore-catch-all',
     'server.send_message(em)\n        logger.info("Successfully dispatched SMTP fallback email.")\n    except (smtplib.SMTPException, socket.error, ssl.SSLError) as e:'),

    ('with urllib.request.urlopen(req, timeout=5):\n                pass\n        except Exception as e: # audit-ignore-catch-all',
     'with urllib.request.urlopen(req, timeout=5):\n                pass\n        except (urllib.error.URLError, socket.timeout) as e:'),

    ('client.execute("pager.incident", "report_incident", vals=payload)\n        logger.error(f"Incident reported [{source}]: {msg}")\n    except Exception as e: # audit-ignore-catch-all',
     'client.execute("pager.incident", "report_incident", vals=payload)\n        logger.error(f"Incident reported [{source}]: {msg}")\n    except (urllib.error.URLError, json.JSONDecodeError, socket.timeout) as e:'),

    ('client.execute("pager.incident", "auto_resolve_incidents", source=source)\n        logger.info(f"[{source}] System stable. Auto-resolved open incidents.")\n    except Exception as e: # audit-ignore-catch-all',
     'client.execute("pager.incident", "auto_resolve_incidents", source=source)\n        logger.info(f"[{source}] System stable. Auto-resolved open incidents.")\n    except (urllib.error.URLError, json.JSONDecodeError, socket.timeout) as e:'),

    ('if pct > check.get("critical", 90):\n                    return False, f"Disk space at {pct}% on {part}"\n            except Exception as e: # audit-ignore-catch-all',
     'if pct > check.get("critical", 90):\n                    return False, f"Disk space at {pct}% on {part}"\n            except (PermissionError, psutil.Error) as e:'),

    ('return True, f"OK (Load: {load1:.2f})"\n        except Exception as e: # audit-ignore-catch-all',
     'return True, f"OK (Load: {load1:.2f})"\n        except (OSError, ValueError) as e:'),

    ('ftp.login()\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'ftp.login()\n            return True, "OK"\n        except (ftplib.all_errors, socket.error) as e:'),

    ('imap.logout()\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'imap.logout()\n            return True, "OK"\n        except (imaplib.IMAP4.error, socket.error, ssl.SSLError) as e:'),

    ('pop.quit()\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'pop.quit()\n            return True, "OK"\n        except (poplib.error_proto, socket.error, ssl.SSLError) as e:'),

    ('conn.close()\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'conn.close()\n            return True, "OK"\n        except (pymysql.MySQLError, socket.error) as e:'),

    ('conn.unbind()\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'conn.unbind()\n            return True, "OK"\n        except (ldap3.core.exceptions.LDAPException, socket.error) as e:'),

    ('return True, f"OK (Offset: {response.offset:.4f}s)"\n        except Exception as e: # audit-ignore-catch-all',
     'return True, f"OK (Offset: {response.offset:.4f}s)"\n        except (ntplib.NTPException, socket.error) as e:'),

    ('if expect and expect not in res.stdout:\n                return False, "SNMP payload mismatch"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if expect and expect not in res.stdout:\n                return False, "SNMP payload mismatch"\n            return True, "OK"\n        except (subprocess.SubprocessError, socket.error) as e:'),

    ('socket.gethostbyname(domain)\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'socket.gethostbyname(domain)\n            return True, "OK"\n        except (subprocess.SubprocessError, socket.gaierror) as e:'),

    ('return False, f"HTTP status {response.status}"\n        except Exception as e: # audit-ignore-catch-all',
     'return False, f"HTTP status {response.status}"\n        except (urllib.error.URLError, socket.timeout) as e:'),

    ('if expect and expect not in res.stdout:\n                return False, "HTTP/3 body mismatch"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if expect and expect not in res.stdout:\n                return False, "HTTP/3 body mismatch"\n            return True, "OK"\n        except (subprocess.SubprocessError, socket.error) as e:'),

    ('if expect:\n                    response = s.recv(1024)\n                    if expect.encode("utf-8") not in response:\n                        return False, "TCP payload mismatch"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if expect:\n                    response = s.recv(1024)\n                    if expect.encode("utf-8") not in response:\n                        return False, "TCP payload mismatch"\n            return True, "OK"\n        except (socket.error, binascii.Error) as e:'),

    ('if expect:\n                    response, _ = s.recvfrom(4096)\n                    if expect.encode("utf-8") not in response:\n                        return False, "UDP payload mismatch"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if expect:\n                    response, _ = s.recvfrom(4096)\n                    if expect.encode("utf-8") not in response:\n                        return False, "UDP payload mismatch"\n            return True, "OK"\n        except (socket.error, binascii.Error) as e:'),

    ('if r.ping():\n                return True, "OK"\n            return False, "Redis PING returned False"\n        except Exception as e: # audit-ignore-catch-all',
     'if r.ping():\n                return True, "OK"\n            return False, "Redis PING returned False"\n        except (redis_lib.RedisError, socket.error) as e:'),

    ('if len(res) > 0:\n                    return True, "OK"\n                return False, "RabbitMQ handshake mismatch"\n        except Exception as e: # audit-ignore-catch-all',
     'if len(res) > 0:\n                    return True, "OK"\n                return False, "RabbitMQ handshake mismatch"\n        except socket.error as e:'),

    ('if expect and expect not in str(res):\n                return False, "XML-RPC output mismatch"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if expect and expect not in str(res):\n                return False, "XML-RPC output mismatch"\n            return True, "OK"\n        except (xmlrpc.client.Error, socket.error) as e:'),

    ('if expect and expect not in body:\n                    return False, "JSON-RPC output mismatch"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if expect and expect not in body:\n                    return False, "JSON-RPC output mismatch"\n            return True, "OK"\n        except (urllib.error.URLError, json.JSONDecodeError, socket.timeout) as e:'),

    ('return True, "OK"\n            except Exception as e: # audit-ignore-catch-all',
     'return True, "OK"\n            except (psycopg2.Error, socket.error) as e:'),

    ('with socket.create_connection((target, port), timeout=2):\n                    return True, "OK"\n            except Exception as e: # audit-ignore-catch-all',
     'with socket.create_connection((target, port), timeout=2):\n                    return True, "OK"\n            except socket.error as e:'),

    ('if days_left <= critical_days:\n                        return False, f"SSL Cert expires in {days_left} days"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if days_left <= critical_days:\n                        return False, f"SSL Cert expires in {days_left} days"\n            return True, "OK"\n        except (socket.error, ssl.SSLError, ValueError) as e:'),

    ('return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'return True, "OK"\n        except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('if response.status != 200:\n                    return False, f"Let\'s Encrypt API unreachable ({response.status})"\n        except Exception as e: # audit-ignore-catch-all',
     'if response.status != 200:\n                    return False, f"Let\'s Encrypt API unreachable ({response.status})"\n        except (urllib.error.URLError, socket.timeout) as e:'),

    ('logger.warning(f"Could not verify public IP for domain matching: {e}")\n            except Exception as e: # audit-ignore-catch-all',
     'logger.warning(f"Could not verify public IP for domain matching: {e}")\n            except (urllib.error.URLError, socket.timeout) as e:'),

    ('except subprocess.TimeoutExpired:\n                return False, "Certbot dry-run timed out."\n            except Exception as e: # audit-ignore-catch-all',
     'except subprocess.TimeoutExpired:\n                return False, "Certbot dry-run timed out."\n            except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('if res.returncode != 0:\n                return False, f"pg_dump pre-flight failed: {res.stderr[:100]}"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if res.returncode != 0:\n                return False, f"pg_dump pre-flight failed: {res.stderr[:100]}"\n            return True, "OK"\n        except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('if res.returncode != 0:\n                return False, f"Nginx config error: {res.stderr[:100]}"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if res.returncode != 0:\n                return False, f"Nginx config error: {res.stderr[:100]}"\n            return True, "OK"\n        except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('if res.returncode != 0:\n                return False, f"Logrotate dry-run failed: {res.stderr[:100]}"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if res.returncode != 0:\n                return False, f"Logrotate dry-run failed: {res.stderr[:100]}"\n            return True, "OK"\n        except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('if res.returncode != 0:\n                return False, f"Cloudflared tunnel info failed: {res.stderr[:100]}"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if res.returncode != 0:\n                return False, f"Cloudflared tunnel info failed: {res.stderr[:100]}"\n            return True, "OK"\n        except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('if user and password:\n                    server.login(user, password)\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if user and password:\n                    server.login(user, password)\n            return True, "OK"\n        except (smtplib.SMTPException, socket.error, ssl.SSLError) as e:'),

    ('return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'return True, "OK"\n        except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('if res.stdout.strip().lower() != "true":\n                return False, f"Docker container {target} is not running"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if res.stdout.strip().lower() != "true":\n                return False, f"Docker container {target} is not running"\n            return True, "OK"\n        except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('if b"STAT " not in res:\n                    return False, "Memcached stats mismatch"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if b"STAT " not in res:\n                    return False, "Memcached stats mismatch"\n            return True, "OK"\n        except socket.error as e:'),

    ('if not res.startswith(b"SSH-"):\n                    return False, "SSH protocol mismatch"\n            return True, "OK"\n        except Exception as e: # audit-ignore-catch-all',
     'if not res.startswith(b"SSH-"):\n                    return False, "SSH protocol mismatch"\n            return True, "OK"\n        except socket.error as e:'),

    ('if res:\n                return True, "OK"\n            return False, "Heartbeat missing"\n        except Exception as e: # audit-ignore-catch-all',
     'if res:\n                return True, "OK"\n            return False, "Heartbeat missing"\n        except (urllib.error.URLError, json.JSONDecodeError) as e:'),

    ('return True, "OK"\n        except Exception as e: # audit-ignore-catch-all\n            logger.warning("SMART check failed: %s", e)',
     'return True, "OK"\n        except (json.JSONDecodeError, IOError) as e:\n            logger.warning("SMART check failed: %s", e)'),

    ('return True, "OK"\n        except Exception as e: # audit-ignore-catch-all\n            logger.warning("Synthetic script check failed: %s", e)',
     'return True, "OK"\n        except (json.JSONDecodeError, IOError) as e:\n            logger.warning("Synthetic script check failed: %s", e)'),

    ('return True, "OK"\n        except Exception as e: # audit-ignore-catch-all\n            logger.warning("Systemd check failed: %s", e)',
     'return True, "OK"\n        except (subprocess.SubprocessError, FileNotFoundError) as e:\n            logger.warning("Systemd check failed: %s", e)'),

    ('subprocess.Popen([remedy], shell=False)\n                except Exception as e: # audit-ignore-catch-all',
     'subprocess.Popen([remedy], shell=False)\n                except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('subprocess.Popen([remedy], shell=False)\n                    except Exception as e: # audit-ignore-catch-all',
     'subprocess.Popen([remedy], shell=False)\n                    except (subprocess.SubprocessError, FileNotFoundError) as e:'),

    ('with open(config_path, "r", encoding="utf-8") as f:\n            config = json.load(f)\n    except Exception as e: # audit-ignore-catch-all',
     'with open(config_path, "r", encoding="utf-8") as f:\n            config = json.load(f)\n    except (json.JSONDecodeError, IOError) as e:'),

    ('report(\n                        cl,\n                        payload["source"],\n                        payload["description"],\n                        payload["severity"],\n                    )\n            except Exception as e: # audit-ignore-catch-all',
     'report(\n                        cl,\n                        payload["source"],\n                        payload["description"],\n                        payload["severity"],\n                    )\n            except (redis_lib.RedisError, json.JSONDecodeError, KeyError) as e:'),
]

for old, new in reps:
    content = content.replace(old, new, 1)

with open(filepath, 'w') as f:
    f.write(content)
