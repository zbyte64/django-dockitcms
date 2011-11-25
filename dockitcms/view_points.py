from common import BaseViewPointClass, register_view_point_class

from dockit.views import ListView, DetailView

from django.conf.urls.defaults import patterns
from django import forms

class ListViewPointForm(forms.Form):
    list_template_name = forms.CharField(initial='dockitcms/list.html')
    detail_template_name = forms.CharField(initial='dockitcms/detail.html')
    paginate_by = forms.IntegerField(required=False)

class ListViewPointClass(BaseViewPointClass):
    form_class = ListViewPointForm
    label = 'List View'
    
    def get_urls(self, view_point_doc):
        document = view_point_doc.collection.get_document()
        params = view_point_doc.view_config
        return patterns('',
            (r'^$', ListView.as_view(document=document,
                                     template_name=params['list_template_name'],
                                     paginate_by=params.get('paginate_by', None)),
            ),
            (r'^(?P<pk>.+)/$', DetailView.as_view(document=document,
                                                  template_name=params['detail_template_name']),
            ),
        )

register_view_point_class('list', ListViewPointClass)
