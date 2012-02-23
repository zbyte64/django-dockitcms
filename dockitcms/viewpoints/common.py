from django.utils.translation import ugettext_lazy as _

from dockitcms.models import ViewPoint

from dockit import schema

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class AuthenticatedMixin(schema.Schema):
    authenticated_users_only = schema.BooleanField(default=False)
    staff_only = schema.BooleanField(default=False)

class TemplateMixin(schema.Schema):
    template_source = schema.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = schema.CharField(default='dockitcms/list.html', blank=True)
    template_html = schema.TextField(blank=True)
    content = schema.TextField(blank=True)

class CanonicalMixin(schema.Schema):
    canonical = schema.BooleanField(help_text=_('If checked, this view point defines the canonical urls for these collections'))


