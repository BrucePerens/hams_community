import os
import socket
import psycopg2
from psycopg2 import sql
from psycopg2.errors import UndefinedTable


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(base_dir, "deploy", "env")

    db_user = "odoo"
    db_password = None
    db_host = None
    db_port = "5432"
    db_name = "hams"

    # Safely parse the vault to extract database credentials
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("POSTGRES_USER=") or line.startswith("DB_USER="):
                    db_user = line.split("=", 1)[1].strip("'\"")
                elif line.startswith("POSTGRES_PASSWORD=") or line.startswith(
                    "DB_PASSWORD="
                ):
                    db_password = line.split("=", 1)[1].strip("'\"")
                elif line.startswith("POSTGRES_HOST=") or line.startswith("DB_HOST="):
                    db_host = line.split("=", 1)[1].strip("'\"")
                elif line.startswith("POSTGRES_PORT=") or line.startswith("DB_PORT="):
                    db_port = line.split("=", 1)[1].strip("'\"")

    # Smart Fallback: Force Unix Socket if Docker hostname is unresolvable locally
    if db_host == "postgres":
        try:
            socket.gethostbyname("postgres")
        except socket.error:
            db_host = None  # Fallback to local Unix sockets

    # Construct connection dictionary
    conn_kwargs = {"dbname": db_name, "user": db_user, "port": db_port}
    if db_password:
        conn_kwargs["password"] = db_password
    if db_host:
        conn_kwargs["host"] = db_host

    try:
        conn = psycopg2.connect(**conn_kwargs)
    except Exception as e:
        print(
            "[!] Failed to connect directly to PostgreSQL database '{}': {}".format(
                db_name, e
            )
        )
        return

    # Map Odoo models to actual PostgreSQL table names
    tables = ["res_users", "res_partner", "ham_qso", "ham_callbook", "ham_dns_zone"]

    counts = {}

    with conn.cursor() as cr:
        for table in tables:
            try:
                # Use psycopg2.sql to safely inject table names per Burn List rules
                query = sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
                cr.execute(query)
                counts[table] = cr.fetchone()[0]
                conn.commit()
            except UndefinedTable:
                conn.rollback()
                counts[table] = "Not Installed"
            except Exception as e:
                conn.rollback()
                counts[table] = "Error: {}".format(e)

    conn.close()

    print("\nDatabase Record Counts (Direct PostgreSQL Connection):")
    print("--------------------------------------------------------")
    for table in tables:
        # Format Odoo model name for clean display
        display_name = table.replace("_", ".")
        print("{:<15}: {}".format(display_name, counts[table]))
    print("--------------------------------------------------------\n")


if __name__ == "__main__":
    main()
