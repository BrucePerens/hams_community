# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError

class TestSEOModels(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_admin = cls.env.ref('base.user_admin')

        cls.regular_user1 = cls.env['res.users'].create({
            'name': 'Regular User 1',
            'login': 'reg1',
            'group_ids': [(6, 0, [cls.env.ref('base.group_portal').id])]
        })

        cls.regular_user2 = cls.env['res.users'].create({
            'name': 'Regular User 2',
            'login': 'reg2',
            'group_ids': [(6, 0, [cls.env.ref('base.group_portal').id])]
        })

        cls.group = cls.env['user.websites.group'].create({
            'name': 'Test SEO Group',
            'website_slug': 'test-seo-group',
            'member_ids': [(6, 0, [cls.regular_user1.id])]
        })

    def test_self_writeable_fields(self):
        """Test that SEO fields are added to writeable fields for users."""
        fields = self.env['res.users'].SELF_WRITEABLE_FIELDS
        seo_fields = [
            "website_meta_title",
            "website_meta_description",
            "website_meta_keywords",
            "website_meta_og_img",
            "seo_name",
        ]
        for field in seo_fields:
            self.assertIn(field, fields, f"Field {field} should be writeable")

    def test_check_access_rule_res_users(self):
        """Test that a user can write to their own SEO fields but not others."""
        # reg1 can write to their own profile
        reg1_record = self.regular_user1.with_user(self.regular_user1)
        # Should not raise exception
        reg1_record.write({'website_meta_title': 'My Title'})

        # reg1 cannot write to reg2
        reg2_record_by_reg1 = self.regular_user2.with_user(self.regular_user1)
        with self.assertRaises(AccessError):
            reg2_record_by_reg1.write({'website_meta_title': 'Hacked Title'})

    def test_check_access_rule_user_websites_group(self):
        """Test that a user can write to a group they are a member of, but not others."""
        # reg1 is a member, can write
        group_by_reg1 = self.group.with_user(self.regular_user1)
        # Should not raise exception
        group_by_reg1.write({'website_meta_title': 'Group Title'})

        # reg2 is not a member, cannot write
        group_by_reg2 = self.group.with_user(self.regular_user2)
        with self.assertRaises(AccessError):
            group_by_reg2.write({'website_meta_title': 'Hacked Group Title'})
