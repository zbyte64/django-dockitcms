from django.views.generic import View

from dockit.admin.documentadmin import DocumentAdmin

from dockitcms.models import Collection
from dockitcms.common import CMSURLResolver

class VirtualDocumentAdmin(DocumentAdmin):
    def __init__(self, document, admin_site, base_url):
        DocumentAdmin.__init__(self, document, admin_site)
        self.base_url = base_url
        self.resolver = CMSURLResolver(r'^'+base_url, self.get_urls())
    
    def reverse(self, name, *args, **kwargs):
        ret = self.resolver.reverse(name, *args, **kwargs)
        return self.base_url + ret

class ManageCollectionView(View):
    admin = None
    admin_site = None
    
    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        admin = self.get_document_admin()
        view_match = admin.resolver.resolve(request.path)
        return view_match.func(request, *view_match.args, **view_match.kwargs)
    
    def get_document_admin(self):
        collection = self.get_collection()
        base_url = self.admin.reverse(self.admin.app_name+'_manage', *self.args, **self.kwargs)
        return VirtualDocumentAdmin(collection.get_document(), self.admin_site, base_url)
    
    def get_collection(self):
        return Collection.objects.get(self.kwargs['pk'])

from dockit.admin.views import SingleObjectFragmentView, CreateView, UpdateView, BaseFragmentViewMixin
from dockit.forms import DocumentForm
from dockit.schema.exceptions import DotPathNotFound
import dockit

from dockitcms.common import REGISTERED_VIEW_POINTS
from dockitcms.properties import GenericViewPointEntryField

from fields import ViewPointEntryField

class FieldsMixin(object):
    def formfield_for_field(self, prop, field, **kwargs):
        if isinstance(prop, dockit.ListField) and isinstance(prop.schema, GenericViewPointEntryField):
            field = ViewPointEntryField
            kwargs['dotpath'] = self.dotpath()
            if self.next_dotpath():
                kwargs['required'] = False
            return field(**kwargs)
        return BaseFragmentViewMixin.formfield_for_field(self, prop, field, **kwargs)

class CreateDocumentDesignView(FieldsMixin, CreateView):
    pass

class UpdateDocumentDesignView(FieldsMixin, UpdateView):
    pass

class ViewPointProxyFragmentView(FieldsMixin, SingleObjectFragmentView):
    def get_view_type_value(self):
        obj = self.get_temporary_store()
        if obj:
            try:
                frag = obj.dot_notation(self.dotpath())
            except DotPathNotFound:
                pass
            else:
                if frag.view_type:
                    return frag.view_type
        if 'view_type' in self.request.GET:
            return self.request.GET['view_type']
    
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        view_type = self.get_view_type_value()
        if view_type:
            view_spec = REGISTERED_VIEW_POINTS[view_type]
            kwargs = self.admin.get_view_kwargs()
            kwargs['view_type'] = view_type
            view = view_spec.get_admin_view(**kwargs)
            return view(request, *args, **kwargs)
        return super(ViewPointProxyFragmentView, self).dispatch(request, *args, **kwargs)

class ViewPointDesignerFragmentView(FieldsMixin, SingleObjectFragmentView):
    '''
    default admin handler for designing fields
    '''
    view_spec = None
    view_type = None
    
    def _generate_form_class(self, field_schema):
        view_cls = self
        
        class CustomDocumentForm(DocumentForm):
            class Meta:
                schema = field_schema
                document = self.document
                form_field_callback = self.formfield_for_field
                dotpath = self.dotpath() or None
                exclude = ['view_type']
            
            def _inner_save(self, *args, **kwargs):
                obj = super(CustomDocumentForm, self)._inner_save(*args, **kwargs)
                obj.view_type = view_cls.view_type
                return obj
        
        return CustomDocumentForm
    
    def get_form_class(self):
        return self._generate_form_class(self.view_spec.schema)

