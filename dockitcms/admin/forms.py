from django import forms

from fieldmaker.spec_widget import ListFormField, MetaFormMixin, FormField
from fieldmaker.admin.forms import FieldEntryForm
from fieldmaker.resource import registry

from dockit.forms import DocumentForm

from dockitcms.models import SchemaDefinition, ViewPoint, Collection
from dockitcms.common import REGISTERED_VIEW_POINTS

class ViewConfigFormField(FormField):
    def __init__(self, **kwargs):
        self.collection = kwargs.pop('collection')
        super(ViewConfigFormField, self).__init__(**kwargs)
    
    def create_field_form(self, name, form):
        prefix = form.add_prefix(name)
        return self.form_cls(data=form.data or None, prefix=prefix, initial=form.initial.get(name), collection=self.collection)

class AdminSchemaDefinitionForm(DocumentForm, MetaFormMixin):
    data = ListFormField(form=FieldEntryForm)
    
    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        self.field_forms = dict()
        self.widget_forms = dict()
        for key, entry in self.get_form_spec().fields.iteritems():
            self.field_forms[key] = entry.render_for_admin(key)
        for key, entry in self.get_form_spec().widgets.iteritems():
            self.widget_forms[key] = entry.render_for_admin(key)
        self.post_form_init()
    
    def get_form_spec(self):
        return registry.form_specifications['base.1']
    
    class Meta:
        document = SchemaDefinition

class AdminViewPointForm(DocumentForm):
    def __init__(self, *args, **kwargs):
        DocumentForm.__init__(self, *args, **kwargs)
        self.fields['view_class'] = forms.ChoiceField(choices=[('','Please select view type')]+[(key, view.label) for key, view in self.registry.iteritems()])
        
        view_form = self._get_form_class('view')
        if view_form:
            self.fields['view_config'] = ViewConfigFormField(form=view_form, collection=self.instance)
            self.fields['view_config'].post_form_init('view_config', self)
        
        self.view_config_forms = dict()
        for key, view_class in self.registry.iteritems():
            form = view_class.get_templated_form(collection=self.instance)
            self.view_config_forms[key] = form
    
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
        return entry.get_form_class(collection=self.instance)
    
    def _get_media(self):
        """
        Provide a description of all media required to render the widgets on this form
        """
        media = super(AdminViewPointForm, self)._get_media()
        for entry in self.registry.itervalues():
            media += entry.get_templated_form(collection=self.instance).media
        return media
    media = property(_get_media)
    
    
    class Meta:
        document = Collection
        dotpath = 'view_points.*'

