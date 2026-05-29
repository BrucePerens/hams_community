# Jules Issues - caching

## Test Failures

### `TestCachingTour.test_caching_service_worker_tour`

The tour failed with the following error:
```
2026-05-29 00:50:40,242 21081 WARNING zero_sudo odoo.addons.caching.tests.test_tour.TestCachingTour.test_caching_service_worker_tour: Chrome headless failed to start:
[21150:21173:0529/005031.464190:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Failed to connect to socket /dev/null: Connection refused
...
2026-05-29 00:50:40,259 21081 INFO zero_sudo odoo.addons.caching.tests.test_tour: skipped TestCachingTour.test_caching_service_worker_tour : Failed to detect chrome devtools port after 10.0s.
```

It seems like Chrome headless failed to start, possibly due to environment issues in the Jules VM.
