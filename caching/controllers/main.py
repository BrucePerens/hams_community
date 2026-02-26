import os
from odoo import http, tools
from odoo.http import request
from odoo.modules import get_module_resource, get_module_path

class ServiceWorkerController(http.Controller):
    
    @tools.ormcache()
    def _get_global_static_mtime(self):
        """
        Scans the 'static/' directories of all installed modules to find 
        the most recent file modification timestamp. 
        Cached in RAM so it only executes once per worker lifecycle.
        """
        max_mtime = 0.0
        
        # Raw SQL to get installed modules quickly without ORM/sudo overhead
        request.env.cr.execute("SELECT name FROM ir_module_module WHERE state = 'installed'")
        installed_modules = [row[0] for row in request.env.cr.fetchall()]
        
        for module_name in installed_modules:
            mod_path = get_module_path(module_name)
            if not mod_path:
                continue
                
            static_path = os.path.join(mod_path, 'static')
            if os.path.exists(static_path):
                # Walk through the static directory
                for root, dirs, files in os.walk(static_path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            mtime = os.path.getmtime(filepath)
                            if mtime > max_mtime:
                                max_mtime = mtime
                        except OSError:
                            pass
                            
        # Return as an integer string to be used as a cache hash
        return str(int(max_mtime))

    @http.route('/sw.js', type='http', auth='public', sitemap=False)
    def service_worker(self):
        """
        Serves the Service Worker script from the root scope.
        Dynamically injects the latest filesystem mtime into the CACHE_NAME
        to force browser cache invalidation when files change on disk.
        """
        file_path = get_module_resource('caching', 'static/src/sw', 'sw.js')
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            return request.not_found()

        # Dynamically inject the latest modification time to bust the cache
        latest_mtime = self._get_global_static_mtime()
        content = content.replace('odoo-assets-cache-v3', f'odoo-assets-cache-{latest_mtime}')

        headers = [
            ('Content-Type', 'application/javascript'),
            ('Cache-Control', 'no-cache, max-age=0') 
        ]
        return request.make_response(content, headers=headers)
