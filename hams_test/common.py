# -*- coding: utf-8 -*-
import psutil
import logging
from unittest.mock import MagicMock, patch
from odoo.tests.common import HttpCase, TransactionCase, ChromeBrowser

_logger = logging.getLogger(__name__)

# =================================================================================
# SYSTEM OVERRIDE: Robust WebSocket Request Handler
# =================================================================================
_original_ws_req = ChromeBrowser._websocket_request

def _robust_ws_req(self, method, params=None, timeout=10.0, **kwargs):
    """
    Intercepts core Odoo CDP websocket requests to detect silent Chrome crashes
    or broken pipes instantly, rather than hanging for the full timeout.
    """
    process = getattr(self, '_process', None) or getattr(self, '_chrome_process', None)
    if process and process.poll() is not None:
        raise RuntimeError(f"FATAL: Chrome process (PID {process.pid}) died before CDP command '{method}'.")

    try:
        return _original_ws_req(self, method, params=params, timeout=timeout, **kwargs)
    except TimeoutError as e:
        if process and process.poll() is not None:
            raise RuntimeError(f"FATAL: Chrome process died during CDP command '{method}'.") from e
        raise e
    except Exception as e:  # audit-ignore-catch-all
        _logger.warning("WebSocket exception in CDP command %s: %s", method, e)
        err_name = type(e).__name__
        if 'Connection' in err_name or 'Closed' in err_name or 'BrokenPipe' in err_name:
            raise RuntimeError(f"FATAL: WebSocket pipe broke during CDP command '{method}'. Error: {e}") from e
        raise e

ChromeBrowser._websocket_request = _robust_ws_req


class DiagnosticMock(MagicMock):
    """
    A strict mock designed to trap runaway recursion and excessive deep calling
    often seen when Odoo registry models are incorrectly shadowed or cyclically patched.
    """
    def __init__(self, *args, **kwargs):
        # ADR-0012: Prevent runaway test execution by hard-capping mock recursion.
        max_depth = kwargs.pop("max_recursion_depth", 5)
        # MUST call super before setting attributes to avoid Py3.13 MagicMock getattr crash
        super().__init__(*args, **kwargs)
        self._max_depth = max_depth
        self._current_depth = 0

    def __call__(self, *args, **kwargs):
        self._current_depth += 1
        if self._current_depth > self._max_depth:
            self._current_depth = 0  # Reset for subsequent isolated assertions
            raise RecursionError(
                f"DiagnosticMock Security Trip: Recursion depth limit ({self._max_depth}) exceeded "
                f"on mock '{self._mock_name or 'unnamed'}'. You likely have a cyclic patch or "
                f"are mocking a core Odoo registry propagation method."
            )
        try:
            return super().__call__(*args, **kwargs)
        finally:
            self._current_depth -= 1


class SafePatchMixin:
    """
    Mixin to provide safe, runtime-only patching to avoid Odoo registry
    early-import corruption and mock recursion traps.
    """
    def safe_patch(self, target, *args, **kwargs):
        if not args and "new" not in kwargs and "new_callable" not in kwargs:
            kwargs["new_callable"] = DiagnosticMock
        patcher = patch(target, *args, **kwargs)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj

    def safe_patch_object(self, target, attribute, *args, **kwargs):
        if not args and "new" not in kwargs and "new_callable" not in kwargs:
            kwargs["new_callable"] = DiagnosticMock
        patcher = patch.object(target, attribute, *args, **kwargs)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj


class HamsTransactionCase(TransactionCase, SafePatchMixin):
    # [@ANCHOR: hams_transaction_case]
    """
    Base class for standard transaction tests enforcing safe patching.
    """
    pass


class HamsHttpCase(HttpCase, SafePatchMixin):
    # [@ANCHOR: hams_http_case]
    """
    Base class for standard HTTP/UI Tour tests enforcing safe patching.
    """
    def tearDown(self):
        # RUTHLESS TEARDOWN V3: Process Tree Annihilation (Linter Compliant)
        # Chrome is multi-process. Killing the parent orphans the child renderers.
        if hasattr(self, 'browser') and self.browser:
            process = getattr(self.browser, '_process', None) or getattr(self.browser, '_chrome_process', None)
            if process:
                pid = process.pid
                try:
                    parent = psutil.Process(pid)
                    # recursively kill all child processes (renderers, network, GPU)
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()
                    _logger.info(f"Reaper V3: Eradicated Chrome process tree for PID {pid}.")
                except psutil.NoSuchProcess:
                    pass
                except Exception as e:  # audit-ignore-catch-all
                    _logger.warning(f"Reaper V3: Could not terminate Chrome process tree: {e}")
        super().tearDown()

    def start_tour(self, *args, **kwargs):
        try:
            super().start_tour(*args, **kwargs)
        except Exception as e:  # audit-ignore-catch-all
            _logger.error("\n=== TOUR FAILED OR HUNG. DUMPING COMPILED ASSETS ===")
            try:
                bundle = self.env['ir.qweb']._get_asset_bundle('web.assets_tests').js()
                # Bypass Jules VM permission restrictions on /tmp by targeting /var/tmp
                dump_path = '/var/tmp/failed_tour_bundle.js'
                with open(dump_path, 'w') as f:
                    if isinstance(bundle, str):
                        f.write(bundle)
                    elif hasattr(bundle, 'decode'):
                        f.write(bundle.decode('utf-8'))
                    elif hasattr(bundle, 'raw'):
                        f.write(bundle.raw.decode('utf-8'))
                    else:
                        f.write(str(bundle))
                _logger.error(f"Dumped compiled JS bundle to {dump_path}")

                # --- NEW: DOM STATE DUMPING TELEMETRY ---
                try:
                    # Extract the live frozen DOM from the headless browser via raw CDP websocket
                    # ADR-0012: Enforce strict timeouts on telemetry extraction to prevent Python test runner deadlocks
                    # Jules VM Elasticity: Scale the timeout using Odoo's throttling factor for slow environments
                    telemetry_timeout = 10.0 * getattr(self.browser, 'throttling_factor', 1.0)
                    if hasattr(self.browser, '_websocket_request'):
                        res = self.browser._websocket_request('Runtime.evaluate', params={'returnByValue': True, 'expression': 'document.documentElement.outerHTML'}, timeout=telemetry_timeout)
                    else:
                        res = self.browser._websocket.request('Runtime.evaluate', returnByValue=True, expression='document.documentElement.outerHTML', timeout=telemetry_timeout)
                    dom_html = res.get('result', {}).get('value', '<html><body>Failed to extract DOM state from browser process.</body></html>')
                    dom_path = '/var/tmp/failed_tour_dom.html'
                    with open(dom_path, 'w', encoding='utf-8') as f:
                        f.write(dom_html)
                    _logger.error(f"Dumped frozen DOM state to {dom_path}. Inspect this file locally to see exactly what the browser rendered at the moment of the crash.")
                except Exception as dom_e:  # audit-ignore-catch-all
                    _logger.error(f"Telemetry Error: Could not extract DOM state from Chrome DevTools Protocol: {dom_e}")
                with open('/var/tmp/failed_tour_exception.txt', 'w') as f:
                    f.write(str(e))
            except Exception as inner_e:  # audit-ignore-catch-all
                _logger.error(f"Could not dump bundle to /var/tmp: {inner_e}")

            # Kill Chrome cleanly before abandoning the process to avoid zombie storms
            if hasattr(self, 'browser') and self.browser:
                process = getattr(self.browser, '_process', None) or getattr(self.browser, '_chrome_process', None)
                if process:
                    try:
                        parent = psutil.Process(process.pid)
                        for child in parent.children(recursive=True):
                            child.kill()
                        parent.kill()
                    except Exception as kill_e:  # audit-ignore-catch-all
                        _logger.warning("Reaper emergency teardown failed: %s", kill_e)

            _logger.error("Tour failed. Telemetry saved. Re-raising exception to proceed to next test.")
            raise e


class HamsIntegrationCase(HamsHttpCase):
    # [@ANCHOR: integration_daemon_testing]
    """
    Base class for heavy I/O integration tests.
    Automatically starts and stops required external daemons.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._daemons = []

    @classmethod
    def tearDownClass(cls):
        env = cls.env
        daemon_utils = env["zero_sudo.daemon.utils"]
        for process in cls._daemons:
            daemon_utils.stop_daemon_process(process)
        cls._daemons.clear()
        super().tearDownClass()

    @classmethod
    def start_daemon(cls, script_path, args=None, env_vars=None, health_url=None, timeout=600):
        """
        Starts a daemon and waits for it to become healthy.
        Must be called within setUpClass or setUp.
        """
        env = cls.env
        daemon_utils = env["zero_sudo.daemon.utils"]
        process = daemon_utils.start_daemon_process(script_path, args, env_vars)
        cls._daemons.append(process)

        if health_url:
            daemon_utils.poll_health_check(health_url, timeout=timeout)
        return process
