# -*- coding: utf-8 -*-
from odoo import models, api, tools
from odoo.modules.module import get_manifest
import hashlib
import logging

_logger = logging.getLogger(__name__)

class Module(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _register_hook(self):
        super()._register_hook()

        # Prevent documentation bootstrapping during active module installations or uninstalls
        # to avoid interacting with unstable or incomplete registry states.
        if self.env.context.get("install_mode") or self.env.context.get("module_uninstall"):
            return

        if not hasattr(self.env.registry, '_zero_sudo_docs_checked'):
            self.env.registry._zero_sudo_docs_checked = True
            self._bootstrap_knowledge_docs()

    @api.model
    def _bootstrap_knowledge_docs(self):
        # [@ANCHOR: zero_sudo_doc_installer]
        # Verified by [@ANCHOR: test_zero_sudo_doc_installer]
        article_model_name = None
        if 'knowledge.article' in self.env:
            article_model_name = 'knowledge.article'
        elif 'manual.article' in self.env:
            article_model_name = 'manual.article'

        if not article_model_name:
            return

        utils = self.env['zero_sudo.security.utils']

        # Securely resolve the appropriate service account utilizing direct SQL checks
        # to ensure the account truly exists before invoking the zero_sudo resolver.
        self.env.cr.execute(
            "SELECT res_id FROM ir_model_data WHERE module='manual_library' AND name='user_manual_library_service_account' AND model='res.users'"
        )
        res = self.env.cr.fetchone()
        svc_account = "manual_library.user_manual_library_service_account" if res else "zero_sudo.odoo_facility_service_internal"

        try:
            env_svc = utils._get_service_env(svc_account)
        except Exception as e:
            _logger.warning("Could not resolve service account for documentation installation: %s", e)
            return

        Article = env_svc[article_model_name]

        modules = self.env['ir.module.module'].search([('state', '=', 'installed')], limit=10000)
        for mod in modules:
            manifest = get_manifest(mod.name)
            if not manifest or 'knowledge_docs' not in manifest:
                continue

            for doc_info in manifest['knowledge_docs']:
                self._install_single_doc(utils, Article, mod.name, doc_info)

    @api.model
    def _install_single_doc(self, utils, Article, module_name, doc_info):
        rel_path = doc_info.get('path')
        if not rel_path:
            return

        # Strip module name prefix if the user accidentally left it in to ensure backward compatibility
        if rel_path.startswith(f"{module_name}/"):
            rel_path = rel_path[len(f"{module_name}/"):]

        full_path = f"{module_name}/{rel_path}"

        try:
            with tools.file_open(full_path, 'rb') as f:
                content_bytes = f.read()
                content_hash = hashlib.sha256(content_bytes).hexdigest()
                doc_body = content_bytes.decode('utf-8')
        except Exception as e:
            _logger.error("Failed to load doc file %s for module %s: %s", full_path, module_name, e)
            return

        name = doc_info.get('name', f"{module_name} Documentation")
        icon = doc_info.get('icon', '📄')
        category = doc_info.get('category', 'workspace')

        hash_key = f"zero_sudo.doc_hash_{module_name}_{name.replace(' ', '_')}"
        existing_hash = utils._get_kv(hash_key)

        if existing_hash == content_hash:
            return

        vals = {
            'name': name,
            'body': doc_body,
        }

        model_fields = Article._fields
        if 'is_published' in model_fields:
            vals['is_published'] = True
        if 'category' in model_fields:
            vals['category'] = category
        if 'internal_permission' in model_fields:
            vals['internal_permission'] = 'read'
        if 'icon' in model_fields:
            vals['icon'] = icon

        existing = Article.search([('name', '=', name)], limit=1)
        if existing:
            existing.write(vals)
        else:
            Article.create(vals)

        utils._set_kv(hash_key, content_hash)
        _logger.info("Installed/Updated knowledge documentation for %s", name)
