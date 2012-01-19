from django.conf.urls.defaults import patterns
from django import forms

from dockitcms.common import CMSURLResolver

class BaseViewPointForm(forms.Form):
    def __init__(self, **kwargs):
        self.collection = kwargs.pop('collection')
        super(BaseViewPointForm, self).__init__(**kwargs)

class BaseViewPointClass(object):
    form_class = None
    label = None
    
    def get_document(self, collection, view_point_doc):
        doc_cls = collection.get_document()
        return doc_cls
    
    def register_view_point(self, collection, view_point_doc):
        pass
        #here it would ensure all neceassry indexes are created
    
    def get_urls(self, collection, view_point_doc):
        return patterns('')
    
    def get_templated_form(self, collection):
        kwargs = self.get_template_form_kwargs(collection)
        return self.get_form_class(collection)(**kwargs)
    
    def get_template_form_kwargs(self, collection):
        return {'collection':collection}
    
    def get_form_class(self, collection):
        return self.form_class
    
    def get_resolver(self, collection, view_point_doc):
        urls = self.get_urls(collection, view_point_doc)
        return CMSURLResolver(r'^'+view_point_doc.url, urls)
    
    def dispatch(self, request, collection, view_point_doc):
        resolver = self.get_resolver(collection, view_point_doc)
        view_match = resolver.resolve(request.path)
        return view_match.func(request, *view_match.args, **view_match.kwargs)
    
    def reverse(self, collection, view_point_doc, name, *args, **kwargs):
        resolver = self.get_resolver(collection, view_point_doc)
        return resolver.reverse(name, *args, **kwargs)
