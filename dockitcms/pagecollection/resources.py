# -*- coding: utf-8 -*-
from hyperadmin.indexes import Index

from dockitcms.resources.common import CMSDocumentResource
from dockitcms.resources.collection import CMSCollectionMixin
from dockitcms.viewpoints.endpoints import DetailEndpoint


#a document resource of page entries
class PageCollectionResource(CMSCollectionMixin, CMSDocumentResource):
    detail_endpoint = (DetailEndpoint, {'index_name':'urlpath'})

    def get_indexes(self):
        indexes = super(PageCollectionResource, self).get_indexes()
        indexes['urlpath'] = URLPathIndex('urlpath', self)
        return indexes

class URLPathIndex(Index):
    def get_url_params(self, param_map={}):
        #how do we specify path is to be passed?
        return [r'(?P<path>.+)']

    def get_url_params_from_item(self, item, param_map={}):
        param_map.setdefault('path', 'path')
        return {param_map['path']: item.instance.path}



