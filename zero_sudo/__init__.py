import logging
import warnings

# Silence standard Python warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Silence Odoo's core framework noise via logging monkeypatch (Cybercrud Policy)
_orig_handle = logging.Logger.handle
def _patched_handle(self, record):
    try:
        msg = record.getMessage().lower()
        if ('deprecated' in msg and 'directive' in msg) or 'pypdf2' in msg:
            return
    except Exception:
        pass
    return _orig_handle(self, record)
logging.Logger.handle = _patched_handle

from . import models  # noqa: F401
from . import controllers  # noqa: F401
