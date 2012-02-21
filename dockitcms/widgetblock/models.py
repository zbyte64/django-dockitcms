from dockit import schema

from django.utils.translation import ugettext_lazy as _
from django.template import Template, Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.contrib.sites.models import Site

class Widget(schema.Schema):
    block_key = schema.CharField()
    
    class Meta:
        typed_field = 'widget_type'
    
    def render(self, context):
        raise NotImplementedError

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class BaseTemplateWidget(Widget):
    template_source = schema.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = schema.CharField(blank=True)
    template_html = schema.TextField(blank=True)

    class Meta:
        proxy = True
    
    def get_template(self):
        if self.template_source == 'name':
            return get_template(self.template_name)
        else:
            return Template(self.template_html)
    
    def get_context(self, context):
        return Context({'widget': self})
    
    def render(self, context):
        template = self.get_template()
        context = self.get_context(context)
        return mark_safe(template.render(context))
    
    @classmethod
    def get_admin_form_class(cls):
        from forms import BaseTemplateWidgetForm
        return BaseTemplateWidgetForm

class SiteWidgets(schema.Document):
    site = schema.ModelReferenceField(Site)
    widgets = schema.ListField(schema.SchemaField(Widget))

SiteWidgets.objects.index('site').commit()

'''
class CustomWidgetDefinition(schema.Document):
    class Meta:
        typed_field = 'widget_def_type'

Custom widgets

'''

