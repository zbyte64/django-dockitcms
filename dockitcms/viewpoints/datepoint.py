from listpoint import ListViewPointForm

from django import forms
from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _

from dockitcms.common import BaseViewPointClass, register_view_point_class
from dockitcms.utils import ConfigurableTemplateResponseMixin

from dockit.views import ListView


class DateListViewPointForm(ListViewPointForm):
    date_field = forms.CharField(help_text=_('Dotpoint notation to the date field'))

class DatePointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class DateListViewPointClass(BaseViewPointClass):
    form_class = DateListViewPointForm
    list_view_class = DatePointListView
    label = _('Date View')
    
    def _configuration_from_prefix(self, params, prefix):
        config = dict()
        for key in ('template_source', 'template_name', 'template_html'):
            config[key] = params.get('%s_%s' % (prefix, key), None)
        return config
    
    def get_urls(self, view_point_doc):
        document = self.get_document(view_point_doc)
        params = view_point_doc.view_config
        return patterns('',
            url(r'^$', 
                self.list_view_class.as_view(document=document,
                                      configuration=self._configuration_from_prefix(params, 'list'),
                                      paginate_by=params.get('paginate_by', None)),
                name='index',
            ),
            url(r'^(?P<pk>.+)/$', 
                self.detail_view_class.as_view(document=document,
                                        configuration=self._configuration_from_prefix(params, 'detail'),),
                name='detail',
            ),
        )

register_view_point_class('datelist', DateListViewPointClass)

