from django import forms

from django.template import Template, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _


class TemplateFormMixin(object):
    #for forms with fields template_html & content
    def _clean_template_html(self, content):
        if not content:
            return content
        try:
            Template(content)
        except TemplateSyntaxError, e:
            raise forms.ValidationError(unicode(e))
        return content
    
    def clean_template_html(self):
        return self._clean_template_html(self.cleaned_data.get('template_html'))
    
    def clean_content(self):
        return self._clean_template_html(self.cleaned_data.get('content'))
    
    def clean(self):
        #TODO pump the error to their perspective field
        if self.cleaned_data.get('template_source') == 'name':
            if not self.cleaned_data.get('template_name'):
                raise forms.ValidationError(_('Please specify a template name'))
        if self.cleaned_data.get('template_source') == 'html':
            if not self.cleaned_data.get('template_html'):
                raise forms.ValidationError(_('Please specify the template html'))
        return self.cleaned_data

