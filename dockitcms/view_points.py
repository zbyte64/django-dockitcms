from common import BaseViewPointClass, register_view_point_class

from dockit.views import ListView, DetailView

from django.conf.urls.defaults import patterns, url
from django import forms

class ListViewPointForm(forms.Form):
    list_template_name = forms.CharField(initial='dockitcms/list.html')
    detail_template_name = forms.CharField(initial='dockitcms/detail.html')
    paginate_by = forms.IntegerField(required=False)

class ListViewPointClass(BaseViewPointClass):
    form_class = ListViewPointForm
    label = 'List View'
    
    def get_document(self, view_point_doc):
        doc_cls = view_point_doc.collection.get_document()
        view_point = self
        class WrappedDoc(doc_cls):
            def get_absolute_url(self):
                return view_point.reverse(view_point_doc, 'detail', self.pk)
            
            class Meta:
                proxy = True
        
        return WrappedDoc
    
    def get_urls(self, view_point_doc):
        document = self.get_document(view_point_doc)
        params = view_point_doc.view_config
        return patterns('',
            url(r'^$', 
                ListView.as_view(document=document,
                                 template_name=params['list_template_name'],
                                 paginate_by=params.get('paginate_by', None)),
                name='index',
            ),
            url(r'^(?P<pk>.+)/$', 
                DetailView.as_view(document=document,
                                   template_name=params['detail_template_name']),
                name='detail',
            ),
        )

register_view_point_class('list', ListViewPointClass)
