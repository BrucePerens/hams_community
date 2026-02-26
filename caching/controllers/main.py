from odoo import http
from odoo.http import request
from odoo.modules import get_module_resource

class ServiceWorkerController(http.Controller):
    
    @http.route('/sw.js', type='http', auth='public', sitemap=False)
    def service_worker(self):
        """
        Serves the Service Worker script from the root scope so it can 
        intercept all platform requests.
        """
        file_path = get_module_resource('caching', 'static/src/sw', 'sw.js')
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            return request.not_found()

        headers = [
            ('Content-Type', 'application/javascript'),
            ('Cache-Control', 'no-cache, max-age=0') 
        ]
        return request.make_response(content, headers=headers)
