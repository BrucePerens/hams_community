@@BOUNDARY_TEST_PY_REFAC@@
Path: tools/test.py
Operation: search-and-replace

:::: SEARCH
    def _safe_run(cmd, **kw): return subprocess.run(cmd, check=True, **kw)
    infrastructure.apply_production_directories(_safe_run, environment="test", dest_dir="/mnt/upper")
    infrastructure.write_env_files("/opt/hams/etc", dict(os.environ), _safe_run, dest_dir="/mnt/upper")
    infrastructure.provision_static_files(_safe_run, dict(os.environ), environment="test", dest_dir="/mnt/upper")
    infrastructure.execute_hooks("test", _safe_run, dict(os.environ), dest_dir="/mnt/upper")

    for item in os.listdir("/mnt/upper"):
        if item == "mnt": continue
        os.makedirs(f"/mnt/work/{item}", exist_ok=True)
        subprocess.run(["mount", "-t", "overlay", "overlay", "-o", f"lowerdir=/{item},upperdir=/mnt/upper/{item},workdir=/mnt/work/{item}", f"/{item}"], check=True)

    # Bind mount host tmp directory AFTER overlayfs so it isnt shadowed
====
    def _safe_run(cmd, **kw): return subprocess.run(cmd, check=True, **kw)

    print("[*] Creating overlay filesystem for isolated testing...")
    for item in ["etc", "opt", "var", "usr", "home", "tmp", "run"]:
        if not os.path.exists(f"/{item}"): continue
        os.makedirs(f"/mnt/upper/{item}", exist_ok=True)
        os.makedirs(f"/mnt/work/{item}", exist_ok=True)
        try:
            subprocess.run(["mount", "-t", "overlay", "overlay", "-o", f"lowerdir=/{item},upperdir=/mnt/upper/{item},workdir=/mnt/work/{item}", f"/{item}"], check=True)
        except subprocess.CalledProcessError as e:
            _logger.debug("Failed to overlay mount /%s: %s", item, e)

    # Bind mount host tmp directory AFTER overlayfs so it isnt shadowed
:::: REPLACE
:::: SEARCH
    # 3. PostgreSQL Sandboxing
    try:
        psql_cmd = get_pg_bin("psql")
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

    pg_sock = "/var/run/postgresql"
    if not os.path.exists(pg_sock):
        pg_sock = "/tmp"

    orig_user = os.environ.get("SUDO_USER", "odoo")

    try:
        pg_user = pwd.getpwnam("postgres")
    except KeyError:
        pg_user = pwd.getpwnam("root")

    def preexec_pg():
        os.setresgid(pg_user.pw_gid, pg_user.pw_gid, pg_user.pw_gid)
        os.setresuid(pg_user.pw_uid, pg_user.pw_uid, pg_user.pw_uid)

    wait_for_socket(f"{pg_sock}/.s.PGSQL.5432", "PostgreSQL")

    p = subprocess.Popen([psql_cmd, "-h", pg_sock, "-d", "postgres"], stdin=subprocess.PIPE, preexec_fn=preexec_pg, text=True, stdout=subprocess.DEVNULL)
    sql_create_roles = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'odoo') THEN
            CREATE ROLE odoo WITH SUPERUSER LOGIN PASSWORD 'odoo';
        END IF;
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{orig_user}') THEN
            CREATE ROLE {orig_user} WITH SUPERUSER LOGIN;
        END IF;
    END $$;
    """
    p.communicate(sql_create_roles)
    p.wait()

    # 4. Redis Sandboxing
    redis_user = pwd.getpwnam("redis")
    redis_proc = subprocess.Popen(["redis-server", "--daemonize", "no"], preexec_fn=lambda: (os.setresgid(redis_user.pw_gid, redis_user.pw_gid, redis_user.pw_gid), os.setresuid(redis_user.pw_uid, redis_user.pw_uid, redis_user.pw_uid)), stdout=subprocess.DEVNULL)
    wait_for_port(6379, "Redis")

    # 5. RabbitMQ Sandboxing
    subprocess.run(["systemctl", "stop", "rabbitmq-server"], check=False, stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-u", "rabbitmq"], check=False, stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "epmd"], check=False, stderr=subprocess.DEVNULL)

    os.makedirs("/var/lib/rabbitmq", exist_ok=True)
    with open("/var/lib/rabbitmq/.erlang.cookie", "w") as f:
        f.write("HAMS_TEST_RABBITMQ_COOKIE_12345")

    rmq_user = pwd.getpwnam("rabbitmq")
    os.chown("/var/lib/rabbitmq/.erlang.cookie", rmq_user.pw_uid, rmq_user.pw_gid)
    os.chmod("/var/lib/rabbitmq/.erlang.cookie", 0o400)

    def preexec_rmq():
        os.setresgid(rmq_user.pw_gid, rmq_user.pw_gid, rmq_user.pw_gid)
        os.setresuid(rmq_user.pw_uid, rmq_user.pw_uid, rmq_user.pw_uid)
        os.environ["HOME"] = "/var/lib/rabbitmq"

    subprocess.run(["rabbitmq-server", "-detached"], preexec_fn=preexec_rmq, check=True, stdout=subprocess.DEVNULL)
    wait_for_port(5672, "RabbitMQ")

    # 6. Execute Inner Odoo Test Suite
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["HAMS_ISOLATED_NS"] = "1"
    os.environ["PGHOST"] = pg_sock
====
    print("[*] Provisioning isolated environment via infrastructure.py...")
    orig_user = os.environ.get("SUDO_USER", "odoo")
    env_vars = dict(os.environ)
    env_vars["REPO_ROOT"] = base_dir

    infrastructure.provision_environment(_safe_run, env_vars, orig_user, skip_apt=True)

    # Execute Inner Odoo Test Suite
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["HAMS_ISOLATED_NS"] = "1"
    pg_sock = "/var/run/postgresql"
    if not os.path.exists(pg_sock):
        pg_sock = "/tmp"
    os.environ["PGHOST"] = pg_sock
:::: REPLACE
:::: SEARCH
    # 7. Graceful Ephemeral Teardown
    subprocess.run(["rabbitmqctl", "stop"], preexec_fn=preexec_rmq, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    redis_proc.terminate()

    try:
        orig_uid = pwd.getpwnam(orig_user).pw_uid
    except KeyError:
        orig_uid = -1
====
    # Graceful Ephemeral Teardown
    subprocess.run(["systemctl", "stop", "rabbitmq-server", "redis-server", "postgresql"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        orig_uid = pwd.getpwnam(orig_user).pw_uid
    except KeyError:
        orig_uid = -1
:::: REPLACE
:::: SEARCH
def wait_for_port(port, name, host="127.0.0.1", timeout=60.0):
    print(f"[*] Waiting for {name} on {host}:{port} to open...")
    start_time = global_vclock.time()
    while global_vclock.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            if sock.connect_ex((host, port)) == 0:
                print(f"[*] {name} is ready.")
                return True
        time.sleep(0.5)
    print(f"❌ ERROR: {name} did not open port {port} within {timeout} seconds.")
    return False

def wait_for_socket(sock_path, name, timeout=60.0):
    print(f"[*] Waiting for {name} unix socket {sock_path} to open...")
    start_time = global_vclock.time()
    while global_vclock.time() - start_time < timeout:
        if os.path.exists(sock_path):
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(1.0)
                try:
                    sock.connect(sock_path)
                    print(f"[*] {name} socket is ready.")
                    return True
                except OSError as e:
                    _logger.debug("Ignored OSError: %s", e)
        time.sleep(0.5)
    print(f"❌ ERROR: {name} socket {sock_path} did not open within {timeout} seconds.")
    return False


def get_pg_bin(name):
====
def get_pg_bin(name):
:::: REPLACE
:::: SEARCH
def start_jules_daemons():
    print("[*] Clearing port 8069 bindings...")
    subprocess.run(["sudo", "fuser", "-k", "8069/tcp"], check=False, stderr=subprocess.DEVNULL)

    print("[*] Configuring local PostgreSQL...")
    try:
        psql_cmd = get_pg_bin("psql")
    except FileNotFoundError as err:
        print(f"❌ ERROR: {err}")
        sys.exit(1)

    subprocess.run(["sudo", "systemctl", "start", "postgresql"], check=False, stderr=subprocess.DEVNULL)

    pg_socket = "/var/run/postgresql"
    if not os.path.exists(pg_socket):
        pg_socket = "/tmp"

    wait_for_socket(f"{pg_socket}/.s.PGSQL.5432", "PostgreSQL")

    orig_user = os.environ.get("USER") or "odoo"
    custom_env = dict(os.environ)
    custom_env["PGUSER"] = "postgres"
    p = subprocess.Popen(["sudo", "-u", "postgres", psql_cmd, "-h", pg_socket, "-d", "postgres"], stdin=subprocess.PIPE, env=custom_env, text=True, stdout=subprocess.DEVNULL)
    sql_create_roles = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'odoo') THEN
            CREATE ROLE odoo WITH SUPERUSER LOGIN PASSWORD 'odoo';
        END IF;
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{orig_user}') THEN
            CREATE ROLE {orig_user} WITH SUPERUSER LOGIN;
        END IF;
    END $$;
    """
    p.communicate(sql_create_roles)
    p.wait()

    print("[*] Starting local Redis and RabbitMQ...")
    subprocess.run(["sudo", "systemctl", "start", "redis-server"], check=False, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "systemctl", "start", "rabbitmq-server"], check=False, stderr=subprocess.DEVNULL)

    if not wait_for_port(6379, "Redis", timeout=15.0):
        print("[*] Redis systemctl failed, attempting direct daemonize...")
        subprocess.Popen(["redis-server", "--daemonize", "yes"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_for_port(6379, "Redis")

    if not wait_for_port(5672, "RabbitMQ", timeout=20.0):
        print("[*] RabbitMQ systemctl failed, attempting direct daemonize...")
        os.makedirs("/tmp/rabbitmq", exist_ok=True)
        custom_rmq = dict(os.environ)
        custom_rmq["RABBITMQ_BASE"] = "/tmp/rabbitmq"
        subprocess.Popen(["rabbitmq-server", "-detached"], env=custom_rmq, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_for_port(5672, "RabbitMQ")

    os.environ["PGHOST"] = pg_socket


def main():
====
def main():
:::: REPLACE
:::: SEARCH
    os.environ.setdefault("HAMS_KEYS_DIR", "/opt/hams/etc/keys")

    if os.environ.get("IN_JULES_VM") or os.environ.get("JULES_SESSION_ID"):
        existing_args = os.environ.get("ODOO_TEST_CHROME_ARGS", "")
        if "--no-sandbox" not in existing_args:
            os.environ["ODOO_TEST_CHROME_ARGS"] = f"{existing_args} --no-sandbox --disable-dev-shm-usage".strip()

    if os.environ.get("HAMS_ISOLATED_NS") != "1" and not os.environ.get("IN_JULES_VM") and not os.environ.get("JULES_SESSION_ID"):
        if "--internal-ns-init" in sys.argv:
====
    os.environ.setdefault("HAMS_KEYS_DIR", "/opt/hams/etc/keys")

    is_jules = bool(os.environ.get("IN_JULES_VM")) or bool(os.environ.get("JULES_SESSION_ID"))

    if is_jules:
        existing_args = os.environ.get("ODOO_TEST_CHROME_ARGS", "")
        if "--no-sandbox" not in existing_args:
            os.environ["ODOO_TEST_CHROME_ARGS"] = f"{existing_args} --no-sandbox --disable-dev-shm-usage".strip()

        if os.geteuid() != 0:
            print("[*] Elevating privileges for Jules provisioning...")
            exec_cmd = ["sudo", "-H", "-E", sys.executable] + sys.argv
            os.execvpe("sudo", exec_cmd, os.environ)

    if os.environ.get("HAMS_ISOLATED_NS") != "1" and not is_jules:
        if "--internal-ns-init" in sys.argv:
:::: REPLACE
:::: SEARCH
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()

    is_jules = bool(os.environ.get("IN_JULES_VM")) or bool(os.environ.get("JULES_SESSION_ID"))

    if is_jules:
        start_jules_daemons()

    python_exec = "/usr/bin/python3"
====
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()

    if is_jules:
        print("[*] Clearing port 8069 bindings...")
        subprocess.run(["fuser", "-k", "8069/tcp"], check=False, stderr=subprocess.DEVNULL)
        
        print("[*] Provisioning Jules environment via infrastructure.py...")
        def _safe_run(cmd, **kw): return subprocess.run(cmd, check=True, **kw)
        orig_user = os.environ.get("SUDO_USER") or os.environ.get("USER") or "odoo"
        env_vars = dict(os.environ)
        env_vars["REPO_ROOT"] = base_dir
        infrastructure.provision_environment(_safe_run, env_vars, orig_user, skip_apt=True)
        
        pg_socket = "/var/run/postgresql"
        if not os.path.exists(pg_socket):
            pg_socket = "/tmp"
        os.environ["PGHOST"] = pg_socket

    python_exec = "/usr/bin/python3"
:::: REPLACE
@@BOUNDARY_TEST_PY_REFAC@@--
