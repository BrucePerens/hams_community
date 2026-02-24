# 📚 Manual Library Module (`manual_library`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Context:** Technical documentation strictly for LLMs and Integrators. Use this to build dependent modules without needing source code.

---

## 1. 🏗️ Architecture & Enterprise Compatibility
**Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER be given dependencies on `ham_*` modules or anything else from the proprietary codebase.

**CRITICAL:** This module is a clean-room, 100% drop-in API replacement for the official **Odoo Enterprise Knowledge** module. Because it uses the exact same ORM namespace (`knowledge.article`), any dependent module can inject documentation natively.

---

## 2. 🔌 API Surface & Data Model

### Interoperability Fields:
* `name` (`Char`): Article title (Required).
* `body` (`Html`): The rich-text HTML content.
* `parent_id` (`Many2one` to `knowledge.article`): Used to build the nested tree.
* `child_ids` (`One2many` to `knowledge.article`): The inverse.
* `sequence` (`Integer`): Ordering.
* `is_published` (`Boolean`): Frontend visibility.
* `icon` (`Char`): Emoji or string class.
* `internal_permission` (`Selection`): `'read'`, `'write'`, `'none'`.

### Custom Analytics Fields:
* **`helpful_count`**, **`unhelpful_count`**: Incremented by the public `/manual/feedback` API endpoint.

---

## 3. 📤 Data Injection Methods

### Method A: XML Data Loading (Recommended)
```xml
<odoo>
    <data noupdate="1">
        <record id="my_module_technical_manual" model="knowledge.article">
            <field name="name">My Module Reference</field>
            <field name="is_published" eval="True"/>
            <field name="internal_permission">read</field>
            <field name="icon">⚙️</field>
            <field name="body" type="html">
                <![CDATA[ <h1>Module Reference</h1><p>Docs...</p> ]]>
            </field>
        </record>
    </data>
</odoo>
```

### Method B: Safe Python Injection (post_init_hook)
```python
def post_init_hook(env):
    if 'knowledge.article' in env:
        env['knowledge.article'].create({
            'name': 'API Reference',
            'body': '<p>HTML content...</p>',
            'is_published': True,
            'internal_permission': 'read'
        })
```
