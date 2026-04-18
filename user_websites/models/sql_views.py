from odoo import models, fields, tools


class PublicDirectoryView(models.Model):
    _name = "user_websites.public.directory.view"
    _description = "Public Directory View"
    _auto = False

    name = fields.Char(readonly=True)
    website_slug = fields.Char(readonly=True)
    write_date = fields.Datetime(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW user_websites_public_directory_view AS (
                SELECT u.id, p.name, u.website_slug, u.write_date
                FROM res_users u
                JOIN res_partner p ON u.partner_id = p.id
                WHERE u.privacy_show_in_directory = TRUE AND u.website_slug IS NOT NULL
            )
        """)


class ContentRoutingView(models.Model):
    _name = "user_websites.content.routing.view"
    _description = "Content Routing View"
    _auto = False

    target_url = fields.Char(readonly=True)
    content_owner_id = fields.Many2one("res.users", readonly=True)
    content_group_id = fields.Many2one("user.websites.group", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW user_websites_content_routing_view AS (
                SELECT row_number() OVER () as id, target_url, content_owner_id, content_group_id
                FROM (
                    SELECT '/' || website_slug || '/home' as target_url, id as content_owner_id, NULL::integer as content_group_id
                    FROM res_users WHERE website_slug IS NOT NULL
                    UNION ALL
                    SELECT '/' || website_slug || '/blog' as target_url, id as content_owner_id, NULL::integer as content_group_id
                    FROM res_users WHERE website_slug IS NOT NULL
                    UNION ALL
                    SELECT '/' || website_slug || '/home' as target_url, NULL::integer as content_owner_id, id as content_group_id
                    FROM user_websites_group WHERE website_slug IS NOT NULL
                    UNION ALL
                    SELECT '/' || website_slug || '/blog' as target_url, NULL::integer as content_owner_id, id as content_group_id
                    FROM user_websites_group WHERE website_slug IS NOT NULL
                    UNION ALL
                    SELECT url as target_url, owner_user_id as content_owner_id, user_websites_group_id as content_group_id
                    FROM website_page WHERE url IS NOT NULL AND (owner_user_id IS NOT NULL OR user_websites_group_id IS NOT NULL)
                ) combined
            )
        """)


class WeeklyDigestView(models.Model):
    _name = "user_websites.weekly.digest.view"
    _description = "Weekly Digest Aggregation View"
    _auto = False

    partner_id = fields.Many2one("res.partner", readonly=True)
    author_name = fields.Char(readonly=True)
    owner_model = fields.Char(readonly=True)
    owner_record_id = fields.Integer(readonly=True)
    first_post_id = fields.Integer(readonly=True)
    post_ids_string = fields.Text(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW user_websites_weekly_digest_view AS (
                SELECT
                    row_number() OVER () as id,
                    f.partner_id,
                    COALESCE(up.name, g.name) as author_name,
                    f.res_model as owner_model,
                    f.res_id as owner_record_id,
                    MIN(p.id) as first_post_id,
                    string_agg(p.id::text, ',') as post_ids_string
                FROM blog_post p
                LEFT JOIN res_users u ON p.owner_user_id = u.id
                LEFT JOIN res_partner up ON u.partner_id = up.id
                LEFT JOIN user_websites_group g ON p.user_websites_group_id = g.id
                JOIN mail_followers f ON
                    (f.res_model = 'res.partner' AND f.res_id = u.partner_id) OR
                    (f.res_model = 'user.websites.group' AND f.res_id = g.id)
                WHERE p.is_published = TRUE
                  AND p.create_date >= NOW() - INTERVAL '7 days'
                GROUP BY f.partner_id, COALESCE(up.name, g.name), f.res_model, f.res_id
            )
        """)
