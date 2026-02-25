# 📚 Manual Library Module (`manual_library`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

**Context:** Technical documentation strictly for LLMs and Integrators. Use this to build dependent modules without needing source code.

---

## 1. 🏗️ Architecture & Enterprise Compatibility
**Open Source Isolation Mandate:** This module is Open Source and available to the Odoo Community. It MUST NEVER be given dependencies on `ham_*` modules or anything else from the proprietary codebase.

**CRITICAL:** This module is a clean-room, 100% drop-in API replacement for the official **Odoo Enterprise Knowledge** module.
* **Target Model:** `knowledge.article`
* **Database Table:** `knowledge_article`
* Because it uses the exact same ORM namespace and core field signatures as Enterprise, any dependent module (like `ham_kns`) MUST inject documentation targeting the `knowledge.article` model. If the platform is ever upgraded to Odoo Enterprise, the data will remain perfectly intact and natively compatible.

---

## 2. 🔌 API Surface & Data Model
To ensure external modules can install documentation using `<record model="knowledge.article" id="...">`, the following API surface must be perfectly exposed.

### Core Interoperability Fields:
* `name` (`Char`): Article title (Required).
* `body` (`Html`): The rich-text HTML content.
* `parent_id` (`Many2one` to `knowledge.article`): Used to build the nested tree. If `False`, the article is a "Root" article.
* `sequence` (`Integer`): Order among siblings.
* `is_published` (`Boolean`): Frontend visibility for the public.
* `icon` (`Char`): An emoji or string class used in the UI (e.g., 📚).
* `active` (`Boolean`): Standard archiving.
* `internal_permission` (`Selection`): `'read'`, `'write'`, `'none'`. Granular control for standard internal users.

---

## 3. 📤 Data Injection Methods

### Method A: XML Data Loading (Recommended)
Dependent modules can inject manuals seamlessly using standard Odoo XML data files.

```xml
<odoo>
    <data noupdate="1">
        <record id="my_module_technical_manual" model="knowledge.article">
            <field name="name">My Module Reference</field>
            <field name="is_published" eval="True"/>
            <field name="internal_permission">read</field>
            <field name="icon">⚙️</field>
            <field name="body" type="html">
                <![CDATA[
                    <h1>Module Reference</h1>
                    <p>Detailed documentation goes here...</p>
                ]]>
            </field>
        </record>
    </data>
</odoo>
```

### Method B: Safe Python Injection (post_init_hook)
For soft-dependencies, use the standard Python hook. Hooks run as `SUPERUSER_ID` natively, so no `.sudo()` is required.
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
