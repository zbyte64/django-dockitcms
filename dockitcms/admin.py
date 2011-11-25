from django.contrib import admin
from django import forms

from fieldmaker.spec_widget import ListFormField, MetaFormMixin, FormField
from fieldmaker.admin.forms import FieldEntryForm
from fieldmaker.resource import field_registry

from dockit.admin.documentadmin import DocumentAdmin
from dockit.forms import DocumentForm

from models import SchemaDefinition, Collection, ViewPoint
from common import REGISTERED_VIEW_POINTS

class AdminSchemaDefinitionForm(DocumentForm, MetaFormMixin):
    data = ListFormField(form=FieldEntryForm)
    
    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        self.field_forms = dict()
        self.widget_forms = dict()
        for key, entry in field_registry.fields.iteritems():
            self.field_forms[key] = entry.render_for_admin(key)
        for key, entry in field_registry.widgets.iteritems():
            self.widget_forms[key] = entry.render_for_admin(key)
        self.post_form_init()
    
    class Meta:
        document = SchemaDefinition

class AdminViewPointForm(DocumentForm):
    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        self.fields['view_class'] = forms.ChoiceField(choices=[('','Please select view type')]+[(key, view.label) for key, view in self.registry.iteritems()])
        
        view_form = self._get_form_class('view')
        if view_form:
            self.fields['view_config'] = FormField(form=view_form)
            self.fields['view_config'].post_form_init('view_config', self)
    
    @property
    def registry(self):
        return REGISTERED_VIEW_POINTS
    
    def _get_form_class(self, atype):
        selected_type = None
        if hasattr(self, 'cleaned_data'):
            selected_type = self.cleaned_data[atype+'_class']
        elif atype+'_class' in self.data:
            #TODO take into account the form prefix
            selected_type = self.data[atype+'_class']
        elif atype+'_class' in self.initial:
            selected_type = self.initial[atype+'_class']
        if not selected_type:
            return None
        entry = self.registry[selected_type]
        return entry.get_form_class()
    
    def _get_media(self):
        """
        Provide a description of all media required to render the widgets on this form
        """
        media = super(AdminViewPointForm, self)._get_media()
        for entry in self.registry.itervalues():
            media += entry.get_templated_form().media
        return media
    media = property(_get_media)
    
    
    class Meta:
        document = ViewPoint

class SchemaDefinitionAdmin(DocumentAdmin):
    form_class = AdminSchemaDefinitionForm

admin.site.register([SchemaDefinition], SchemaDefinitionAdmin)

class CollectionAdmin(DocumentAdmin):
    pass

admin.site.register([Collection], CollectionAdmin)

class ViewPointAdmin(DocumentAdmin):
    form_class = AdminViewPointForm

admin.site.register([ViewPoint], ViewPointAdmin)
