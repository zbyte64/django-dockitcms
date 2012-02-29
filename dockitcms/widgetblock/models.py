from dockit import schema

from django.utils.translation import ugettext_lazy as _
from django.template import Template, Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from common import ExpandedSchemas

class Widget(schema.Schema):
    class Meta:
        typed_field = 'widget_type'
    
    def render(self, context):
        raise NotImplementedError
    
    @classmethod
    def get_admin_class(cls):
        from admin import WidgetAdmin
        return WidgetAdmin

block_widget_schemas = ExpandedSchemas(None, Widget._meta.fields['widget_type'].schemas)

class BlockWidget(Widget):
    block_key = schema.CharField()
    widget_type = schema.SchemaTypeField(block_widget_schemas, editable=False)
    
    @classmethod
    def get_admin_class(cls):
        from admin import BlockWidgetAdmin
        return BlockWidgetAdmin
    
    class Meta:
        proxy = True

block_widget_schemas.base_schema = BlockWidget

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

class ModelWidgets(schema.Document):
    content_type = schema.ModelReferenceField(ContentType)
    object_id = schema.CharField()
    widgets = schema.ListField(schema.SchemaField(BlockWidget))

ModelWidgets.objects.index('content_type', 'object_id').commit()

reusable_widget_schemas = ExpandedSchemas(None, Widget._meta.fields['widget_type'].schemas)

class ReusableWidget(schema.Document):
    '''
    Stores already configured widgets for quick reuse throughout the site
    '''
    name = schema.CharField()
    widget_type = schema.SchemaTypeField(reusable_widget_schemas, editable=False)
    
    class Meta:
        typed_field = 'widget_type'
    
    def __unicode__(self):
        if self.name:
            return self.name
        return repr(self)

reusable_widget_schemas.base_schema = ReusableWidget

