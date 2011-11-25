import dockit
from django import forms

FORM_FIELD_TO_DOCKIT_FIELD = [
    (forms.BooleanField, dockit.BooleanField),
    (forms.CharField, dockit.CharField),
    (forms.DateField, dockit.DateField),
    (forms.DateTimeField, dockit.DateTimeField),
    (forms.DecimalField, dockit.DecimalField),
    (forms.EmailField, dockit.EmailField),
    (forms.FileField, dockit.FileField),
    (forms.FloatField, dockit.FloatField),
    (forms.IntegerField, dockit.IntegerField),
    (forms.IPAddressField, dockit.IPAddressField),
    #(forms.GenericIPAddressField, dockit.GenericIPAddressField),
    (forms.SlugField, dockit.SlugField),
    (forms.TimeField, dockit.TimeField),
]

def dockit_field_for_form_field(form_field):
    df_kwargs = {'blank': not form_field.required,
                 'help_text': form_field.help_text,}
    for ff, df in FORM_FIELD_TO_DOCKIT_FIELD:
        if isinstance(form_field, ff):
            return df(**df_kwargs)

class ViewPoint(object):
    form_class = None
    view_class = None
    
    def register_view_point(self, view_point_doc):
        pass
        #here it would ensure all neceassry indexes are created
    
    def dispatch(self, request):
        return self.view_class(request)

