from django.utils.translation import ugettext_lazy as _

from dockit import schema

from dockitcms.widgetblock.models import BaseTemplateWidget, Widget, ReusableWidget


class TextWidget(Widget):
    text = schema.TextField()

    class Meta:
        typed_key = 'widgetblock.textwidget'

    def render(self, context):
        return self.text


class ImageWidget(BaseTemplateWidget):
    template_name = schema.CharField(blank=True, default='widgetblock/image_widget.html')

    image = schema.FileField()
    alt = schema.CharField(blank=True)
    link = schema.CharField(blank=True)

    class Meta:
        typed_key = 'widgetblock.imagewidget'


class CTAImage(schema.Schema):
    image = schema.FileField(upload_to='ctas')
    url = schema.CharField(blank=True)

    def __unicode__(self):
        if self.image:
            return unicode(self.image)
        return repr(self)


class CTAWidget(BaseTemplateWidget):
    template_name = schema.CharField(blank=True, default='widgetblock/cta_widget.html')

    default_url = schema.CharField()
    width = schema.CharField()
    height = schema.CharField()
    delay = schema.DecimalField(help_text=_("Display interval of each item"), max_digits=5, decimal_places=2, default=5)

    images = schema.ListField(schema.SchemaField(CTAImage))

    class Meta:
        typed_key = 'widgetblock.ctawidget'

    #@classmethod
    #def get_admin_form_class(cls):
        #from dockitcms.widgetblock.forms import CTAWidgetForm
        #return CTAWidgetForm


class FlatMenuEntry(schema.Schema):
    title = schema.CharField()
    url = schema.CharField()


class FlatMenuWidget(BaseTemplateWidget):
    template_name = schema.CharField(blank=True, default='widgetblock/menu_widget.html')

    entries = schema.ListField(schema.SchemaField(FlatMenuEntry))

    class Meta:
        typed_key = 'widgetblock.flatmenuwidget'

    def get_context(self, context):
        context = BaseTemplateWidget.get_context(self, context)
        #TODO find the active menu entry
        return context


class PredefinedWidget(Widget):
    widget = schema.ReferenceField(ReusableWidget)

    def render(self, context):
        return self.widget.render(context)

    def __unicode__(self):
        if self.widget:
            return unicode(self.widget)
        return repr(self)

    class Meta:
        typed_key = 'widgetblock.predefinedwidget'
