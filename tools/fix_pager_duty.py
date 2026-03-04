import os
import re

pd_acl_path = 'pager_duty/security/ir.model.access.csv'
if os.path.exists(pd_acl_path):
    with open(pd_acl_path, 'r') as f:
        existing_acls = f.read()
    
    if 'access_res_company_pager_admin' not in existing_acls:
        with open(pd_acl_path, 'a') as f:
            f.write('access_res_company_pager_admin,res.company pager admin,base.model_res_company,pager_duty.group_pager_admin,1,0,0,0\n')
            f.write('access_mail_message_pager_admin,mail.message pager admin,mail.model_mail_message,pager_duty.group_pager_admin,1,1,1,0\n')
            f.write('access_discuss_channel_pager_admin,discuss.channel pager admin,mail.model_discuss_channel,pager_duty.group_pager_admin,1,1,0,0\n')
            f.write('access_mail_followers_pager_admin,mail.followers pager admin,mail.model_mail_followers,pager_duty.group_pager_admin,1,1,1,1\n')
            f.write('access_mail_template_pager_admin,mail.template pager admin,mail.model_mail_template,pager_duty.group_pager_admin,1,0,0,0\n')
            f.write('access_res_users_pager_admin,res.users pager admin,base.model_res_users,pager_duty.group_pager_admin,1,0,0,0\n')
            f.write('access_mail_alias_domain_pager_admin,mail.alias.domain pager admin,mail.model_mail_alias_domain,pager_duty.group_pager_admin,1,0,0,0\n')

for root, dirs, files in os.walk('pager_duty'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            
            new_content = re.sub(r"(['\"])user_mail_service_internal(['\"])", r"\1pager_duty.user_pager_service_internal\2", content)
            new_content = re.sub(r"(['\"])user_pager_service_internal(['\"])", r"\1pager_duty.user_pager_service_internal\2", new_content)
            new_content = new_content.replace('pager_duty.pager_duty.', 'pager_duty.')
            
            if content != new_content:
                with open(path, 'w') as f:
                    f.write(new_content)

pd_sec_path = 'pager_duty/security/security.xml'
if os.path.exists(pd_sec_path):
    with open(pd_sec_path, 'r') as f:
        content = f.read()
    
    if 'user_pager_service_internal' not in content:
        inject = """
        <record id="user_pager_service_internal" model="res.users">
            <field name="name">Pager Duty Service Account</field>
            <field name="login">pager_service_internal</field>
            <field name="is_service_account" eval="True"/>
            <field name="group_ids" eval="[(6, 0, [ref('pager_duty.group_pager_admin')])]"/>
        </record>
        """
        content = content.replace('</data>', f'{inject}\n    </data>')
        with open(pd_sec_path, 'w') as f:
            f.write(content)

print('✅ Pager Duty ACLs and Missing Service Accounts Fixed!')
