from models import BaseTemplateWidget, Widget

import dockit

from dockitcms.viewpoints.collections.common import CollectionMixin

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

class TextWidget(Widget):
    text = dockit.TextField()
    
    class Meta:
        typed_key = 'widgetblock.textwidget'
    
    def render(self, context):
        return self.text

class ImageWidget(Widget):
    image = dockit.FileField()
    
    class Meta:
        typed_key = 'widgetblock.imagewidget'
    
    def render(self, context):
        return mark_safe(u'<img src="%s"/>' % self.image.url)

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

class CollectionWidget(BaseTemplateWidget, CollectionMixin):
    '''
    A widget that is powered by another collection
    '''
    
    class Meta:
        typed_key = 'widgetblock.collectionwidget'
    
    def get_context(self, context):
        context = BaseTemplateWidget.get_context(self, context)
        index = self.get_base_index()
        index.commit() #TODO perhaps schemas should get a save signal for this to be committed?
        context['object_list'] = index
        return context

class ModelWidget(BaseTemplateWidget):
    model = dockit.ModelReferenceField(ContentType)
    
    class Meta:
        typed_key = 'widgetblock.modelwidget'
    
    def get_context(self, context):
        context = BaseTemplateWidget.get_context(self, context)
        model = self.model.model_class()
        context['model'] = model
        context['object_list'] = model.objects.all()
        return context

