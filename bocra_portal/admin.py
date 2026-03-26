from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class BOCRAAdminSite(AdminSite):
    site_header = _('BOCRA Administration')
    site_title = _('BOCRA Admin Portal')
    index_title = _('Dashboard')

admin_site = BOCRAAdminSite(name='bocra_admin')