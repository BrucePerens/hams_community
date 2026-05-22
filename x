s.TestZeroSudoViews.test_02_zero_sudo_tour: Issuing json command http://127.0.0.1:37775/json 
2026-05-22 07:14:52,763 58486 INFO hams_test odoo.tests.common.requests: request SplitResult(scheme='http', netloc='127.0.0.1:37775', path='/json', query='', fragment='') with timeout 3 increased to 10s during tests 
2026-05-22 07:14:52,764 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Websocket url found: ws://127.0.0.1:37775/devtools/page/4B91133A094A79E21A27EBB92E1E0B63 
2026-05-22 07:14:52,766 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Enable chrome headless console log notification 
2026-05-22 07:14:52,767 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Chrome headless enable page notifications 
2026-05-22 07:14:52,779 58486 INFO hams_test odoo.addons.base.models.res_users: Login successful for login:admin from n/a 
2026-05-22 07:14:52,785 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Setting session cookie in browser 
2026-05-22 07:14:52,786 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Open "http://127.0.0.1:8069/odoo" in browser 
2026-05-22 07:14:52,786 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Navigating to: "http://127.0.0.1:8069/odoo" 
2026-05-22 07:14:52,794 58486 INFO hams_test odoo.addons.base.models.ir_http: Generating routing map for key 1 
2026-05-22 07:14:53,216 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /odoo HTTP/1.1" 200 - 157 0.051 0.373
2026-05-22 07:14:53,219 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Navigation result: {'frameId': '4B91133A094A79E21A27EBB92E1E0B63', 'loaderId': '351FA48DD8218A3D57C415551E12A428', 'isDownload': False} 
2026-05-22 07:14:53,219 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Evaluate ready code "odoo.isTourReady('zero_sudo_tour')" 
2026-05-22 07:14:53,238 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/assets/3e438f0/web.assets_web.min.css HTTP/1.1" 200 - 2 0.001 0.008
2026-05-22 07:14:53,241 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/assets/c835d3e/web.assets_web.min.js HTTP/1.1" 200 - 2 0.001 0.011
2026-05-22 07:14:53,269 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/webclient/load_menus HTTP/1.1" 200 - 18 0.009 0.028
2026-05-22 07:14:53,281 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/manifest.webmanifest HTTP/1.1" 200 - 9 0.006 0.041
2026-05-22 07:14:53,290 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/assets/7ad1cd6/web.assets_tests.min.js HTTP/1.1" 200 - 2 0.001 0.004
2026-05-22 07:14:53,311 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/assets/6a95266/web.assets_web_print.min.css HTTP/1.1" 200 - 2 0.001 0.005
2026-05-22 07:14:53,549 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Asking for screenshot 
2026-05-22 07:14:53,558 58486 INFO ? werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/static/img/odoo-icon-192x192.png HTTP/1.1" 200 - 0 0.000 0.003
2026-05-22 07:14:53,559 58486 INFO ? werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/static/img/favicon.ico HTTP/1.1" 200 - 0 0.000 0.004
2026-05-22 07:14:53,567 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/webclient/translations?hash=&lang=en_US HTTP/1.1" 200 - 1 0.001 0.009
2026-05-22 07:14:53,586 58486 INFO hams_test odoo.addons.partner_autocomplete.models.res_company: Starting enrich of company My Company (1) 
2026-05-22 07:14:53,614 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "POST /web/dataset/call_kw/res.company/iap_enrich_auto#res.company.iap_enrich_auto HTTP/1.1" 200 - 23 0.012 0.027
2026-05-22 07:14:53,616 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour: Screenshot in: /var/tmp/odoo_tests/hams_test/screenshots/sc_20260522_071453_610906_test_02_zero_sudo_tour.png 
2026-05-22 07:14:53,618 58486 INFO hams_test odoo.addons.zero_sudo.tests.test_views.TestZeroSudoViews.test_02_zero_sudo_tour.browser: Error received after termination: Owl is running in 'dev' mode. 
2026-05-22 07:14:53,621 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /bus/websocket_worker_bundle?v=19.0-2 HTTP/1.1" 200 - 3 0.001 0.040
2026-05-22 07:14:53,622 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/service-worker.js HTTP/1.1" 200 - 0 0.000 0.009
2026-05-22 07:14:53,632 58486 INFO ? werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /mail/static/lib/idb-keyval/idb-keyval.js HTTP/1.1" 200 - 0 0.000 0.001
2026-05-22 07:14:53,697 58486 INFO ? werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/static/lib/odoo_ui_icons/fonts/odoo_ui_icons.woff2 HTTP/1.1" 200 - 0 0.000 0.002
2026-05-22 07:14:53,700 58486 INFO ? werkzeug: 127.0.0.1 - - [22/May/2026 07:14:53] "GET /web/static/src/libs/fontawesome/fonts/fontawesome-webfont.woff2?v=4.7.0 HTTP/1.1" 200 - 0 0.000 0.001
2026-05-22 07:14:54,088 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /odoo HTTP/1.1" 200 - 82 0.022 0.428
2026-05-22 07:14:54,119 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /odoo/offline HTTP/1.1" 200 - 9 0.003 0.475
2026-05-22 07:14:54,140 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /web/image?model=res.users&field=avatar_128&id=2 HTTP/1.1" 200 - 18 0.005 0.449
2026-05-22 07:14:54,160 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /web/image/res.partner/3/avatar_128?unique=1779434050000 HTTP/1.1" 200 - 16 0.005 0.468
2026-05-22 07:14:54,169 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "POST /web/action/load HTTP/1.1" 200 - 5 0.002 0.480
2026-05-22 07:14:54,212 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "POST /mail/data HTTP/1.1" 200 - 36 0.015 0.495
2026-05-22 07:14:54,215 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /websocket?version=19.0-2 HTTP/1.1" 101 - 0 0.000 0.509
2026-05-22 07:14:54,232 58486 INFO ? odoo.addons.bus.models.bus: Bus.loop listen imbus on db postgres 
2026-05-22 07:14:54,298 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "POST /mail/data HTTP/1.1" 200 - 50 0.016 0.038
2026-05-22 07:14:54,320 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /web/image/res.partner/2/avatar_128?unique=1779434050000 HTTP/1.1" 200 - 16 0.005 0.022
2026-05-22 07:14:54,414 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "POST /web/dataset/call_kw/discuss.channel/channel_fetched#discuss.channel.channel_fetched HTTP/1.1" 200 - 20 0.008 0.017
2026-05-22 07:14:54,447 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "POST /discuss/channel/messages HTTP/1.1" 200 - 27 0.010 0.024
2026-05-22 07:14:54,465 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /web/image/discuss.channel/2/avatar_128?unique=03e4656f6f795faf3585d35eeecc131ec16a6188929ad790b602ebe9583d42abe3c4aef624d6609899312c3e06d0d9b23fb1f1c1b97f8c1c86ae4d525687b4bf HTTP/1.1" 200 - 10 0.004 0.034
2026-05-22 07:14:54,483 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /web/image/discuss.channel/1/avatar_128?unique=8af074e3ad6539d5e3de0e8d54c88d4b59b81514591f39ac58f767916d9d1739508738c22b960cbc4e1315b52b860f920fea23671c026ff2c484b2ef96a3ba93 HTTP/1.1" 200 - 10 0.004 0.053
2026-05-22 07:14:54,488 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /web/bundle/web.assets_emoji?lang=en_US HTTP/1.1" 200 - 1 0.000 0.030
2026-05-22 07:14:54,563 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "POST /discuss/channel/mark_as_read HTTP/1.1" 200 - 31 0.011 0.028
2026-05-22 07:14:54,570 58486 INFO hams_test werkzeug: 127.0.0.1 - - [22/May/2026 07:14:54] "GET /web/assets/1bcd000/web.assets_emoji.min.js HTTP/1.1" 200 - 2 0.001 0.033
^C
[!] CTRL-C detected! Forcefully terminating the test process group...

==========================================================
🎉 TEST RUN COMPLETE: No test failures detected.
==========================================================

Traceback (most recent call last):
  File "/home/bruce/workspace/hams_community/tools/test.py", line 901, in <module>
    main()
    ~~~~^^
  File "/home/bruce/workspace/hams_community/tools/test.py", line 715, in main
    setup_namespace_and_run_tests(real_error_log, sys_args)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/bruce/workspace/hams_community/tools/test.py", line 620, in setup_namespace_and_run_tests
    ret = subprocess.run(test_cmd, preexec_fn=preexec_odoo).returncode
          ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.13/subprocess.py", line 556, in run
    stdout, stderr = process.communicate(input, timeout=timeout)
                     ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.13/subprocess.py", line 1214, in communicate
    self.wait()
    ~~~~~~~~~^^
  File "/usr/lib/python3.13/subprocess.py", line 1280, in wait
    return self._wait(timeout=timeout)
           ~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.13/subprocess.py", line 2066, in _wait
    (pid, sts) = self._try_wait(0)
                 ~~~~~~~~~~~~~~^^^
  File "/usr/lib/python3.13/subprocess.py", line 2024, in _try_wait
    (pid, sts) = os.waitpid(self.pid, wait_flags)
                 ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
KeyboardInterrupt

