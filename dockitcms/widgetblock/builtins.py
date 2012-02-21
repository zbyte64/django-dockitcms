from models import BaseTemplateWidget, Widget

import dockit

from dockitcms.models import Collection

from django.utils.translation import ugettext_lazy as _

class TextWidget(Widget):
    text = dockit.TextField()
    
    class Meta:
        typed_key = 'widgetblock.textwidget'
    
    def render(self, context):
        return self.text

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
        typed_key = 'widgetblock.ctawidget'
    
    @classmethod
    def get_admin_form_class(cls):
        from forms import CTAWidgetForm
        return CTAWidgetForm

class CollectionWidget(BaseTemplateWidget):
    '''
    A widget that is powered by another collection
    '''
    collection = dockit.ReferenceField(Collection)
    
    class Meta:
        typed_key = 'widgetblock.collectionwidget'

