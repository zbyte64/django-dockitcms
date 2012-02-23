from listpoint import ListViewPoint

from django import forms
from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _

from dockitcms.common import BaseViewPointClass, register_view_point_class
from dockitcms.utils import ConfigurableTemplateResponseMixin

from dockit import schema
from dockit.views import ListView


class TagListViewPointForm(ListViewPoint):
    tag_field = schema.CharField(help_text=_('Dotpoint notation to the tag field'))

class TagPointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class TagListViewPointClass(BaseViewPointClass):
    tag_list_view_class = TagPointListView
    label = _('Tag View')
    
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
                                      view_point=self,
                                      paginate_by=params.get('paginate_by', None)),
                name='index',
            ),
            url(r'^t/(?P<tag>.+)/$', 
                self.tag_list_view_class.as_view(document=document,
                                                 configuration=self._configuration_from_prefix(params, 'list'),
                                                 view_point=self,
                                                 paginate_by=params.get('paginate_by', None)),
                name='tag',
            ),
            url(r'^(?P<pk>.+)/$', 
                self.detail_view_class.as_view(document=document,
                                        view_point=self,
                                        configuration=self._configuration_from_prefix(params, 'detail'),),
                name='detail',
            ),
        )

register_view_point_class('taglist', TagListViewPointClass)

