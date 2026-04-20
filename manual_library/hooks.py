# -*- coding: utf-8 -*-
# Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

def post_init_hook(env):
    """
    Hook executed upon module installation.
    The documentation installation logic is now handled by
    ir.module.module._register_hook to ensure all modules are loaded.
    """
    pass
