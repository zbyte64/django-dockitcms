import dockit

from django.utils.translation import ugettext_lazy as _

from django.template import Template, Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe

class Widget(dockit.Schema):
    block_key = dockit.CharField()
    
    class Meta:
        typed_field = 'widget_type'
    
    def render(self, context):
        raise NotImplementedError

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class BaseTemplateWidget(Widget):
    template_source = dockit.CharField(choices=TEMPLATE_SOURCE_CHOICES, default='name')
    template_name = dockit.CharField(blank=True)
    template_html = dockit.TextField(blank=True)

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

'''
class CustomWidgetDefinition(dockit.Document):
    class Meta:
        typed_field = 'widget_def_type'

Custom widgets

'''
