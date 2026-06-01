# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. All Rights Reserved.
from odoo.tools import mail
from lxml_html_clean import Cleaner

# Odoo uses a subclass _Cleaner, but patching the base Cleaner.__init__
# ensures all instances are affected.
_orig_init = Cleaner.__init__

def _patched_init(self, *args, **kw):
    """
    Force the cleaner to preserve scripts and iframes globally
    by forcefully overriding any parameters that would strip them.
    """
    kw["scripts"] = False
    kw["frames"] = False
    kw["embedded"] = False
    _orig_init(self, *args, **kw)


def post_load():
    """
    Executes after the module is loaded. We place the global monkey patches here
    so they do not poison the registry during test discovery or module updates
    before the module is officially active.
    """
    # 1. Expand Odoo's native safelists
    # [@ANCHOR: expand_tag_safelist]
    # Odoo 19 uses SANITIZE_TAGS which contains 'allow_tags', 'kill_tags', and 'remove_tags'
    tags_to_add = {"script", "iframe", "dfn"}
    mail.SANITIZE_TAGS["allow_tags"] = mail.SANITIZE_TAGS["allow_tags"] | tags_to_add

    # We must also remove them from kill_tags if they are there, as kill_tags takes precedence.
    # Preserve original tuple/list/frozenset type
    if "kill_tags" in mail.SANITIZE_TAGS:
        orig_type = type(mail.SANITIZE_TAGS["kill_tags"])
        new_kill = [tag for tag in mail.SANITIZE_TAGS["kill_tags"] if tag not in tags_to_add]
        mail.SANITIZE_TAGS["kill_tags"] = orig_type(new_kill)

    if "remove_tags" in mail.SANITIZE_TAGS:
        orig_type = type(mail.SANITIZE_TAGS["remove_tags"])
        new_remove = [tag for tag in mail.SANITIZE_TAGS["remove_tags"] if tag not in tags_to_add]
        mail.SANITIZE_TAGS["remove_tags"] = orig_type(new_remove)

    # [@ANCHOR: expand_attribute_safelist]
    # Odoo 19 uses safe_attrs
    mail.safe_attrs = mail.safe_attrs | {
        "src",
        "allowfullscreen",
        "frameborder",
        "allow",
        "type",
        "async",
        "defer",
        "charset",
        "crossorigin",
        "data-bs-toggle",
    }

    # 2. Patch the underlying lxml Cleaner
    # [@ANCHOR: patch_lxml_cleaner]
    Cleaner.__init__ = _patched_init
