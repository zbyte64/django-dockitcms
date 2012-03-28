from django import forms
from django.forms import widgets
from django.forms.formsets import formset_factory
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from resource import registry
from utils import prep_for_kwargs
import spec_widget

class BaseFieldForm(forms.Form):
    required = forms.BooleanField(initial=True, required=False)
    label = forms.CharField(required=False)
    initial = forms.CharField(required=False)
    help_text = forms.CharField(required=False)
    
    def clean(self):
        for key, value in self.cleaned_data.items():
            if value in ("", None):
                del self.cleaned_data[key]
        return self.cleaned_data

class BaseField(object):
    field = None
    identities = list()
    form = BaseFieldForm
    default_widget = 'TextInput'
    
    def create_field(self, data, widget=None):
        kwargs = prep_for_kwargs(data)
        if widget:
            kwargs['widget'] = widget
        return self.field(**kwargs)
    
    def widget_choices(self):
        choices = list()
        for key, widget in registry.widgets.iteritems():
            if not widget.identities:
                choices.append((key, key))
            else:
                for identity in widget.identities:
                    if identity in self.identities:
                        choices.append((key, key))
                        break
        return choices
    
    def render_example(self):
        field = self.create_field({})
        return field.render('name', 'value')
    
    def get_form(self):
        return self.form
    
    def render_for_admin(self, key):
        return mark_safe('<table class="%s">%s</table>' % (key, self.get_form()(prefix='prefix').as_table()))

class BooleanField(BaseField):
    field = forms.BooleanField
    identities = ['BooleanField']

registry.register_field('BooleanField', BooleanField)

class CharFieldForm(BaseFieldForm):
    max_length = forms.IntegerField(required=False)
    min_length = forms.IntegerField(required=False)

class CharField(BaseField):
    form = CharFieldForm
    field = forms.CharField
    identities = ['CharField']

registry.register_field('CharField', CharField)

class ChoiceFieldForm(BaseFieldForm):
    choices = forms.CharField(widget=widgets.Textarea, help_text='each line to contain: "value","label"')

class ChoiceField(BaseField):
    form = ChoiceFieldForm
    field = forms.ChoiceField
    identities = ['ChoiceField']

    def create_field(self, data, widget=None):
        kwargs = prep_for_kwargs(data)
        if widget:
            kwargs['widget'] = widget
        kwargs['choices'] = [row.split(',',1) for row in kwargs['choices'].split('\n')]
        return self.field(**kwargs)

registry.register_field('ChoiceField', ChoiceField)

class MultipleChoiceField(BaseField):
    form = ChoiceFieldForm
    field = forms.MultipleChoiceField
    identities = ['MultipleChoiceField']

    def create_field(self, data, widget=None):
        kwargs = prep_for_kwargs(data)
        if widget:
            kwargs['widget'] = widget
        kwargs['choices'] = [row.split(',',1) for row in kwargs['choices'].split('\n')]
        return self.field(**kwargs)

registry.register_field('MultipleChoiceField', MultipleChoiceField)

class DateField(BaseField):
    field = forms.DateField
    identities = ['DateField']

registry.register_field('DateField', DateField)

class DateTimeField(BaseField):
    field = forms.DateTimeField
    identities = ['DateTimeField']

registry.register_field('DateTimeField', DateTimeField)

class DecimalFieldForm(BaseFieldForm):
    max_value = forms.IntegerField(required=False)
    min_value = forms.IntegerField(required=False)
    max_digits = forms.IntegerField(required=False)
    decimal_places = forms.IntegerField(required=False)

class DecimalField(BaseField):
    form = DecimalFieldForm
    field = forms.DecimalField
    identities = ['DecimalField']

registry.register_field('DecimalField', DecimalField)

class EmailField(CharField):
    field = forms.EmailField
    identities = ['EmailField']

registry.register_field('EmailField', EmailField)

class FileField(BaseField):
    field = forms.FileField
    identities = ['FileField']

registry.register_field('FileField', FileField)

class FloatFieldForm(BaseFieldForm):
    max_value = forms.IntegerField(required=False)
    min_value = forms.IntegerField(required=False)

class FloatField(BaseField):
    form = FloatFieldForm
    field = forms.FloatField
    identities = ['FloatField']

registry.register_field('FloatField', FloatField)

class ImageField(BaseField):
    field = forms.ImageField
    identities = ['FileField', 'ImageField']

registry.register_field('ImageField', ImageField)

class IntegerFieldForm(BaseFieldForm):
    max_value = forms.IntegerField(required=False)
    min_value = forms.IntegerField(required=False)

class IntegerField(BaseField):
    form = IntegerFieldForm
    field = forms.IntegerField
    identities = ['IntegerField']

registry.register_field('IntegerField', IntegerField)

class IPAddressField(BaseField):
    field = forms.IPAddressField
    identities = ['IPAddressField']

registry.register_field('IPAddressField', IPAddressField)

class NullBooleanField(BaseField):
    field = forms.NullBooleanField
    identities = ['NullBooleanField']

registry.register_field('NullBooleanField', NullBooleanField)

class RegexFieldForm(CharFieldForm):
    regex = forms.CharField()

class RegexField(BaseField):
    form = RegexFieldForm
    field = forms.RegexField
    identities = ['RegexField']

registry.register_field('RegexField', RegexField)

class SlugField(BaseField):
    field = forms.SlugField
    identities = ['SlugField']

registry.register_field('SlugField', SlugField)

class TimeField(BaseField):
    field = forms.TimeField
    identities = ['TimeField']

registry.register_field('TimeField', TimeField)

class URLFieldForm(BaseFieldForm):
    max_length = forms.IntegerField(required=False)
    min_length = forms.IntegerField(required=False)
    verify_exists = forms.BooleanField(initial=False, required=False)
    validator_user_agent = forms.CharField(required=False)

class URLField(BaseField):
    form = URLFieldForm
    field = forms.URLField
    identities = ['URLField']

registry.register_field('URLField', URLField)

class ModelChoiceFieldForm(BaseFieldForm):
    model = forms.ModelChoiceField(queryset=ContentType.objects.all())
    
    def clean(self):
        if not self._errors:
            self.cleaned_data['model'] = self.cleaned_data['model'].pk
        return self.cleaned_data

class ModelChoiceField(BaseField):
    form = ModelChoiceFieldForm
    field = forms.ModelChoiceField
    identities = ['ChoiceField']
    
    def create_field(self, data, widget=None):
        kwargs = prep_for_kwargs(data)
        if widget:
            kwargs['widget'] = widget
        ct_id = kwargs.pop('model')
        model = ContentType.objects.get(pk=ct_id).model_class()
        kwargs['queryset'] = model.objects.all()
        return self.field(**kwargs)

registry.register_field('ModelChoiceField', ModelChoiceField)

class BaseFormSetField(BaseField):
    formset = spec_widget.BaseListFormSet
    
    def get_form(self):
        formset = formset_factory(self.form,
                                  formset=self.formset,
                                  can_delete=True) #TODO allow for configuration
        return formset
    
    def render_for_admin(self, key):
        parts = list()
        form = self.get_form()()
        for subform in form:
            parts.append(u'<tr class="dynamic-form"><td><table class="module">%s</table></td></tr>' % subform.as_table())
        parts.append(u'<tr class="dynamic-form empty-form"><td><table class="module">%s</table></td></tr>' % (form.empty_form.as_table()))
        return mark_safe(u'<div class="%s dynamic-set">%s<table> %s</table></div>' % (key, unicode(form.management_form), u'\n'.join(parts)))

class FormField(BaseFormSetField):
    form = spec_widget.FieldEntryForm
    field = spec_widget.FormField
    identities = ['FormField']
    
    def create_field(self, data, widget=None):
        entries = list()
        for entry in data:
            if entry:
                entries.append(entry)
        form = registry.form_specifications['base.1'].create_form(entries)
        return self.field(form=form)

registry.register_field('FormField', FormField)

class ListFormField(BaseFormSetField):
    form = spec_widget.FieldEntryForm
    field = spec_widget.ListFormField
    identities = ['ListFormField']
    
    def create_field(self, data, widget=None):
        entries = list()
        for entry in data:
            if entry:
                entries.append(entry)
        form = registry.form_specifications['base.1'].create_form(entries)
        return self.field(form=form)

registry.register_field('ListFormField', ListFormField)

