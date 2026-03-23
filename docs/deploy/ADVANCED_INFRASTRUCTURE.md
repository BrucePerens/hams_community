# Advanced Infrastructure Upgrades

To support high-throughput contests and secure API integrations, Hams.com utilizes external enterprise services to offload pressure from the main PostgreSQL database.

## 1. Installing Redis & RabbitMQ (Debian/Ubuntu)

Debian natively packages highly stable versions of these services.
We will also install the system-level Python bindings to ensure compatibility with Odoo without violating Debian's PEP-668 virtual environment rules.

```bash
# Update package lists
sudo apt-get update

# Install the core message brokers and data stores
sudo apt-get install -y redis-server rabbitmq-server

# Install the Python drivers globally for Odoo
sudo apt-get install -y python3-redis python3-pika
```

## 2. Enabling and Verifying Services

Ensure the services are configured to start automatically on boot:

```bash
sudo systemctl enable --now redis-server
sudo systemctl enable --now rabbitmq-server

# Verify Redis is responding
redis-cli ping
# Expected Output: PONG
```

## 3. Odoo Service Restart

Once the Python drivers (`python3-redis` and `python3-pika`) are installed, you must restart the Odoo service so the WSGI workers can load the new libraries into memory.

```bash
sudo systemctl restart odoo
```
