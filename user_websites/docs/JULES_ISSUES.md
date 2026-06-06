# JULES ISSUES - user_websites

## Environment Hurdles
- RabbitMQ was not starting initially due to incorrect permissions on `/var/lib/rabbitmq/.erlang.cookie`. Fixed by setting permissions to 400 and restarting the service.
- Redis server was down by default in the Jules environment, causing 'test_01_privacy_friendly_view_counter' to fail. Manually started Redis to resolve.

## Framework Bugs / Hurdles
- Odoo 19 Owl UI tours are prone to race conditions. Using `TourUtils` from `zero_sudo` is recommended.

## Missing Resources
- None identified yet.
