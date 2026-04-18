#!/usr/bin/env python3
import os
import json
import time
import pika
import subprocess
import urllib.request
import urllib.error
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [BACKUP_WORKER] - %(message)s"
)
logger = logging.getLogger("backup_worker")

ODOO_URL = os.environ.get("ODOO_URL", "http://127.0.0.1:8069").rstrip("/")
ODOO_DB = os.environ.get("DB_NAME", "odoo")
ODOO_USER = "backup_service_internal"
ODOO_PASS = os.environ.get("ODOO_SERVICE_PASSWORD", "")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "127.0.0.1")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")


def _json2_call(model, method_name, **kwargs):
    headers = {
        "Authorization": f"bearer {ODOO_PASS}",
        "X-Odoo-Database": ODOO_DB,
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(
        f"{ODOO_URL}/json/2/{model}/{method_name}",
        data=json.dumps(kwargs).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        raise Exception(f"JSON-2 API Error {e.code}: {err_body}")


def execute_job(ch, method, properties, body):
    try:
        payload = json.loads(body)
        job_id = payload["job_id"]
        engine = payload["engine"]
        target_path = payload["target_path"]
        config_id = payload["config_id"]

        logger.info(f"Processing job {job_id} ({engine})")

        _json2_call(
            "backup.job",
            "write",
            ids=[job_id],
            vals={
                "state": "processing",
                "output_log": f"Starting {engine} backup...\n",
            },
        )

        config_records = _json2_call(
            "backup.config", "read", ids=[config_id], fields=["kopia_password"]
        )
        config = config_records[0] if config_records else {}

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
            if time.time() - last_update > 2.0:
                _json2_call(
                    "backup.job",
                    "write",
                    ids=[job_id],
                    vals={"output_log": log_buffer},
                )
                last_update = time.time()

        proc.stdout.close()
        return_code = proc.wait()

        final_state = "done" if return_code == 0 else "failed"
        log_buffer += f"\nProcess exited with code {return_code}"

        _json2_call(
            "backup.job",
            "write",
            ids=[job_id],
            vals={"state": final_state, "output_log": log_buffer},
        )

        if final_state == "done":
            _json2_call("backup.config", "action_sync_snapshots", ids=[config_id])
        else:
            error_msg = f"{engine.capitalize()} backup failed for job {job_id}."
            _json2_call(
                "backup.config",
                "_report_backup_failure",
                ids=[config_id],
                message=error_msg,
            )

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Job {job_id} finished: {final_state}")

    except Exception as e:
        logger.error(f"Fatal error processing job: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    while True:
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST, credentials=credentials
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.queue_declare(queue="backup_tasks", durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue="backup_tasks", on_message_callback=execute_job)

            logger.info("Connected to RABBITMQ. Waiting for backup tasks...")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ offline. Retrying in 5s...")
            time.sleep(5)  # audit-ignore-sleep  # fmt: skip
        except Exception as e:
            logger.error(f"RabbitMQ consumer crash: {e}. Restarting...")
            time.sleep(5)  # audit-ignore-sleep  # fmt: skip


if __name__ == "__main__":
    main()
