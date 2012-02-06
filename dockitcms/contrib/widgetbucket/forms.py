from dockit.forms import DocumentForm
from django import forms

from models import CTAWidget

class CTAWidgetForm(DocumentForm):
    template_name = forms.CharField(required=False, initial='widgetbucket/cta_widget.html')
    
    class Meta:
        document = CTAWidget
