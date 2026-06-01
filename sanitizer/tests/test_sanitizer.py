# -*- coding: utf-8 -*-
from odoo.addons.zero_sudo.tests.common import HamsTransactionCase
from odoo.tools import mail
from lxml_html_clean import Cleaner

class TestSanitizer(HamsTransactionCase):

    def test_safelists(self):
        # Tests [@ANCHOR: expand_tag_safelist]
        # Tests [@ANCHOR: expand_attribute_safelist]
        self.assertIn("script", mail.SANITIZE_TAGS["allow_tags"])
        self.assertIn("iframe", mail.SANITIZE_TAGS["allow_tags"])
        self.assertIn("dfn", mail.SANITIZE_TAGS["allow_tags"])
        self.assertNotIn("script", mail.SANITIZE_TAGS["kill_tags"])
        self.assertNotIn("iframe", mail.SANITIZE_TAGS["kill_tags"])
        self.assertNotIn("dfn", mail.SANITIZE_TAGS["kill_tags"])

        expected_attrs = {
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
        for attr in expected_attrs:
            self.assertIn(attr, mail.safe_attrs)

    def test_cleaner_patch(self):
        # Tests [@ANCHOR: patch_lxml_cleaner]
        # We test both the base Cleaner and any subclass (like Odoo's _Cleaner)
        cleaner = Cleaner(scripts=True, frames=True)
        self.assertFalse(cleaner.scripts)
        self.assertFalse(cleaner.frames)

        # Test that it even overrides if explicitly requested to True
        cleaner2 = Cleaner(scripts=True, frames=True)
        self.assertFalse(cleaner2.scripts)
        self.assertFalse(cleaner2.frames)

    def test_actual_sanitization(self):
        # Test that html_sanitize actually preserves our tags and attributes
        # Tests [@ANCHOR: expand_tag_safelist]
        # Tests [@ANCHOR: expand_attribute_safelist]
        test_html = (
            '<div>'
            '<script src="test.js" async type="text/javascript" defer charset="utf-8" crossorigin="anonymous">alert(1)</script>'
            '<iframe src="test.html" allowfullscreen frameborder="0" allow="camera"> </iframe>'
            '<dfn title="Hertz">Hz</dfn>'
            '<button data-bs-toggle="tooltip">Hover me</button>'
            '</div>'
        )
        sanitized = mail.html_sanitize(test_html, sanitize_tags=True, sanitize_attributes=True)

        # Check Tags
        self.assertIn('<script', sanitized)
        self.assertIn('</script>', sanitized)
        self.assertIn('<iframe', sanitized)
        self.assertIn('</iframe>', sanitized)
        self.assertIn('<dfn', sanitized)
        self.assertIn('</dfn>', sanitized)

        # Check Attributes
        self.assertIn('src="test.js"', sanitized)
        self.assertIn('async', sanitized)
        self.assertIn('type="text/javascript"', sanitized)
        self.assertIn('defer', sanitized)
        self.assertIn('charset="utf-8"', sanitized)
        self.assertIn('crossorigin="anonymous"', sanitized)

        self.assertIn('src="test.html"', sanitized)
        self.assertIn('allowfullscreen', sanitized)
        self.assertIn('frameborder="0"', sanitized)
        self.assertIn('allow="camera"', sanitized)

        self.assertIn('title="Hertz"', sanitized)
        self.assertIn('data-bs-toggle="tooltip"', sanitized)

        # Check content
        self.assertIn('alert(1)', sanitized)
        self.assertIn('Hz', sanitized)
