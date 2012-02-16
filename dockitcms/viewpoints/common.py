from django.utils.translation import ugettext_lazy as _

from dockitcms.models import ViewPoint

import dockit

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class AuthenticatedMixin(dockit.Schema):
    authenticated_users_only = dockit.BooleanField(default=False)
    staff_only = dockit.BooleanField(default=False)

class TemplateMixin(dockit.Schema):
    template_source = dockit.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = dockit.CharField(default='dockitcms/list.html', blank=True)
    template_html = dockit.TextField(blank=True)
    content = dockit.TextField(blank=True)



