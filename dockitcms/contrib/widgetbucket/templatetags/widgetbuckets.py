from django import template

register = template.Library()

from classytags.core import Options
from classytags.helpers import InclusionTag
from classytags.arguments import Argument

from dockitcms.contrib.widgetbucket.models import BaseWidget

from django.db.models import Model
from dockit.schema import Document

class WidgetBucket(InclusionTag):
    name = 'widgetbucket'
    template = 'widgetbucket/widget_holder.html'
    options = Options(
        Argument('bucket_key', resolve=True),
        Argument('vary_on', resolve=True, required=False),
    )
    
    def get_widgets(self, bucket_key, vary_on=''):
        if vary_on:
            obj_qs = BaseWidget.objects.filter(backet_key=bucket_key, vary_on=vary_on)
            if obj_qs:
                return obj_qs
        obj_qs = BaseWidget.objects.filter(backet_key=bucket_key, vary_on='')
        return obj_qs
    
    def prep_vary_on(self, vary_on):
        if vary_on is None:
            return ''
        if isinstance(vary_on, basestring):
            return vary_on
        if isinstance(vary_on, Model):
            vary_on = '%s.%s.%s' % (vary_on._meta.app_label, vary_on._meta.object_name, vary_on.pk)
        elif isinstance(vary_on, Document):
            vary_on = '%s.%s' % (vary_on._meta.collection, vary_on.pk)
        else:
            vary_on = str(vary_on)
        return vary_on
    
    def get_context(self, context, bucket_key, vary_on=''):
        vary_on = self.prep_vary_on(vary_on)
        widgets = list(self.get_widgets(bucket_key, vary_on))
        for widget in widgets:
            widget.rendered_content = widget.render(context)
        return {'widgets':widgets,
                'bucket_key':bucket_key,
                'vary_on':vary_on,}

register.tag(WidgetBucket)
