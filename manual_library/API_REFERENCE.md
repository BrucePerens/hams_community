# Manual Library (`manual_library`) - API Reference

## Purpose
A clean-room, open-source drop-in replacement for the Odoo Enterprise `knowledge` module. It allows modules to natively inject hierarchical documentation using standard Odoo XML data loading.

## Data Model API: `knowledge.article`

Dependent modules do not need to call Python methods; they simply declare XML records targeting `knowledge.article`.

### Core Fields
* `name` (Char): The title of the article.
* `body` (Html): The rich-text content.
* `parent_id` (Many2one): Used to nest articles for the dynamic Table of Contents.
* `is_published` (Boolean): Determines frontend visibility.
* `internal_permission` (Selection): `'read'`, `'write'`, or `'none'`. Controls access for logged-in standard users.
* `icon` (Char): Emoji or icon class.

### Example XML Injection
```xml
<record id="my_module_doc" model="knowledge.article">
    <field name="name">My Module Guide</field>
    <field name="is_published" eval="True"/>
    <field name="internal_permission">read</field>
    <field name="body" type="html">
        <![CDATA[ <h1>Guide</h1><p>Content...</p> ]]>
    </field>
</record>
```
