import logging
import warnings

# Silence standard Python warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Silence Odoo's core framework noise via logging monkeypatch (Cybercrud Policy)
_orig_handle = logging.Logger.handle


def _patched_handle(self, record):
    try:
        msg = record.getMessage().lower()
        if ("deprecated" in msg and "directive" in msg) or "pypdf2" in msg:
            return
    except Exception as e:
        import logging  # noqa: E402

        logging.getLogger(__name__).warning("An error occurred: %s", e)
    return _orig_handle(self, record)


logging.Logger.handle = _patched_handle

from . import models  # noqa: F401, E402
from . import controllers  # noqa: F401, E402
