from django.db.models import Model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from models import ModelWidgets

def widgets(scope):
    if 'object' in scope.kwargs:
        obj = scope.kwargs['object']
        if hasattr(obj, 'widgets'):
            manage_urls = {}
            if hasattr(obj, 'get_manage_urls'):
                urls = obj.get_manage_urls()
                if 'edit' in urls:
                    base_url = urls['edit']
                    manage_urls['list'] = base_url + '?_dotpath=widgets'
            scope.add_data('widgets', obj.widgets, manage_urls)

def modelwidgets(scope):
    if 'widgets' not in scope.data and 'object' in scope.kwargs:
        obj = scope.kwargs['object']
        if isinstance(obj, Model):
            ct = ContentType.objects.get_for_model(obj)
            pk = obj.pk
            #TODO make this a lazy lookup
            entries = ModelWidgets.objects.filter(content_type=ct, object_id=str(pk))
            widgets = list()
            for entry in entries:
                widgets.extend(entry.widgets)
            #TODO compute admin url
            url = reverse('admin:widgetblock_modelwidgets_lookup',
                          kwargs={'app_label':ct.app_label,
                                  'module_name':ct.model,
                                  'pk':pk,})
            manage_urls = {'list':url}
            scope.add_data('widgets', widgets, manage_urls)

