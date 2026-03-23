#!/usr/bin/env python3
import os
import sys
import json
import time
import pika
import subprocess
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), "../../core_base"))
try:
    from json_rpc_client import SecureJSONRPCClient
except ImportError:
    SecureJSONRPCClient = None

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [BACKUP_WORKER] - %(message)s"
)
logger = logging.getLogger("backup_worker")

ODOO_URL = os.environ.get("ODOO_URL", "[http://127.0.0.1:8069](http://127.0.0.1:8069)")
ODOO_DB = os.environ.get("DB_NAME", "hams")

RMQ_HOST = os.environ.get("RMQ_HOST", "127.0.0.1")
RMQ_USER = os.environ.get("RMQ_USER", "guest")
RMQ_PASS = os.environ.get("RMQ_PASS", "guest")


def execute_job(ch, method, properties, body):
    try:
        payload = json.loads(body)
        job_id = payload["job_id"]
        engine = payload["engine"]
        target_path = payload["target_path"]
        config_id = payload["config_id"]

        logger.info(f"Processing job {job_id} ({engine})")

        env_path = os.environ.get(
            "DAEMON_ENV_PATH", "/var/lib/odoo/daemon_keys/backup_worker.env"
        )
        if not SecureJSONRPCClient:
            logger.error("SecureJSONRPCClient missing. Requeueing...")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return

        try:
            client = SecureJSONRPCClient(
                env_path=env_path, base_url=ODOO_URL, db_name=ODOO_DB
            )
        except Exception as e:
            logger.error(f"JSON-RPC authentication/key load failed: {e}. Requeueing...")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return

        client.call(
            "backup.job",
            "write",
            args=[
                [job_id],
                {"state": "processing", "output_log": f"Starting {engine} backup...\n"},
            ],
        )

        config_data = client.call(
            "backup.config",
            "read",
            args=[[config_id]],
            kwargs={"fields": ["kopia_password"]},
        )
        config = config_data[0] if config_data else {}

        env_vars = os.environ.copy()
        if engine == "kopia" and config.get("kopia_password"):
            env_vars["KOPIA_PASSWORD"] = config["kopia_password"]

        cmd = []
        if engine == "kopia":
            cmd = ["kopia", "snapshot", "create", target_path, "--json"]
        elif engine == "pgbackrest":
            cmd = ["pgbackrest", "backup", f"--stanza={target_path}", "--type=full"]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env_vars,
            shell=False,
        )

        log_buffer = ""
        last_update = time.time()

        for line in iter(proc.stdout.readline, ""):
            log_buffer += line
            if time.time() - last_update < 2.0:
                client.call(
                    "backup.job",
                    "write",
                    args=[[job_id], {"output_log": log_buffer}],
                )
                last_update = time.time()

        proc.stdout.close()
        return_code = proc.wait()

        final_state = "done" if return_code == 0 else "failed"
        log_buffer += f"\nProcess exited with code {return_code}"

        client.call(
            "backup.job",
            "write",
            args=[[job_id], {"state": final_state, "output_log": log_buffer}],
        )

        if final_state == "done":
            client.call(
                "backup.config",
                "action_sync_snapshots",
                args=[[config_id]],
            )
        else:
            # Trigger Pager Duty reporting via Odoo model
            error_msg = f"{engine.capitalize()} backup failed for job {job_id}."
            client.call(
                "backup.config",
                "_report_backup_failure",
                args=[[config_id], error_msg],
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Job {job_id} finished: {final_state}")

    except Exception as e:
        logger.error(f"Fatal error processing job: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    while True:
        try:
            credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=RMQ_HOST, credentials=credentials
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.queue_declare(queue="backup_tasks", durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue="backup_tasks", on_message_callback=execute_job)

            logger.info("Connected to RMQ. Waiting for backup tasks...")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ offline. Retrying in 5s...")
            time.sleep(5)  # audit-ignore-sleep
        except Exception as e:
            logger.error(f"RabbitMQ consumer crash: {e}. Restarting...")
            time.sleep(5)  # audit-ignore-sleep


if __name__ == "__main__":
    main()
