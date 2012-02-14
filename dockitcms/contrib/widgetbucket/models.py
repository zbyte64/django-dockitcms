import dockit

from django.utils.translation import ugettext_lazy as _

from django.template import Template, Context
from django.template.loader import get_template
from django.utils.safestring import mark_safe

class BaseWidget(dockit.Document):
    bucket_key = dockit.CharField()
    vary_on = dockit.CharField(blank=True)
    
    class Meta:
        typed_field = 'widget_type'
    
    def render(self, context):
        raise NotImplementedError

BaseWidget.objects.index("bucket_key", "vary_on").commit()

TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]

class BaseTemplateWidget(BaseWidget):
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

class CTAImage(dockit.Schema):
    image = dockit.FileField(upload_to='ctas')
    url = dockit.CharField(blank=True)
    
    def __unicode__(self):
        if self.image:
            return unicode(self.image)
        return repr(self)

class CTAWidget(BaseTemplateWidget):
    default_url = dockit.CharField()
    width = dockit.CharField()
    height = dockit.CharField()
    delay = dockit.DecimalField(help_text=_("Display interval of each item"), max_digits=5, decimal_places=2, default=5)
    
    images = dockit.ListField(dockit.SchemaField(CTAImage)) #TODO the following will be an inline when supported
    
    class Meta:
        typed_key = 'cta_widget'
    
    @classmethod
    def get_admin_form_class(cls):
        from forms import CTAWidgetForm
        return CTAWidgetForm

