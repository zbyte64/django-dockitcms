# -*- coding: utf-8 -*-
from dockitcms.resources.common import CMSDocumentResource
from dockitcms.resources.collection import CMSCollectionMixin


#a document resource of page entries
class PageCollectionResource(CMSCollectionMixin, CMSDocumentResource):
    def build_dynamic_indexes(self):
        indexes = super(PageCollectionResource, self).build_dynamic_indexes()
        #TODO url index?
        #indexes['urlpath'] = URLPathIndex()
        return indexes


#DetailView => url path index (index_name) + page definition rendering

class URLPathIndex(object):
    def get_url_params(self, param_map={}):
        #how do we specify path is to be passed?
        return [r'(?P<path>.+)']

    def get_url_params_from_item(self, item, param_map={}):
        param_map.setdefault('path', 'path')
        return {param_map['path']: item.instance.path}
