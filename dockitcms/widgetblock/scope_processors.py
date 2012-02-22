from django.db.models import Model
from django.contrib.contenttypes.models import ContentType

from models import ModelWidgets

def widgets(scope):
    if 'object' in scope.kwargs:
        obj = scope.kwargs['object']
        if hasattr(obj, 'widgets'):
            #TODO compute admin url
            manage_urls = {}
            if hasattr(obj, 'get_manage_urls'):
                base_url = obj.get_manage_urls()['edit']
                manage_urls['list'] = base_url + '?_dotpath=widgets'
            print obj, manage_urls
            scope.add_data('widgets', obj.widgets, manage_urls)

def modelwidgets(scope):
    if 'widgets' not in scope.data and 'object' in scope.kwargs:
        obj = scope.kwargs['object']
        if isinstance(obj, Model):
            ct = ContentType.objects.get_for_model(obj)
            pk = obj.pk
            #TODO make this a lazy lookup
            entries = ModelWidgets.objects.filter(content_type=ct, object_id=pk)
            widgets = list()
            for entry in entries:
                widgets.extend(entry.widgets)
            #TODO compute admin url
            scope.add_data('widgets', widgets)

