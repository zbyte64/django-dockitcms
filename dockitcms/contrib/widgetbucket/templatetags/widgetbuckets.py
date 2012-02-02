from django import template

register = template.Library()

from classytags.core import Options
from classytags.helpers import InclusionTag
from classytags.arguments import Argument

from dockitcms.contrib.widgetbucket.models import BaseWidget

class WidgetBucket(InclusionTag):
    name = 'widgetbucket'
    template = 'widgetbucket/widget_holder.html'
    options = Options(
        Argument('bucket_key', resolve=True),
        Argument('vary_on', resolve=True, required=False),
    )
    
    def get_widgets(self, bucket_key, vary_on=''):
        base_qs = BaseWidget.objects.filter.bucket_key(bucket_key)
        if vary_on:
            obj_qs = base_qs & BaseWidget.objects.filter.vary_on(vary_on)
            if obj_qs:
                return obj_qs
        obj_qs = base_qs & BaseWidget.objects.filter.vary_on('')
        return obj_qs
    
    def prep_vary_on(self, vary_on):
        if vary_on is None:
            return ''
        if isinstance(vary_on, basestring):
            return vary_on
        #TODO handle db.Model and dockit.Document
        return vary_on
    
    def get_context(self, context, bucket_key, vary_on=''):
        vary_on = self.prep_vary_on(vary_on)
        widgets = self.get_widgets(bucket_key, vary_on)
        rendered_widgets = list()
        for widget in widgets:
            rendered_widgets.append(widget.render(context))
        return {'rendered_widgets':rendered_widgets,
                'widgets':widgets,
                'bucket_key':bucket_key,
                'vary_on':vary_on,}

register.tag(WidgetBucket)
