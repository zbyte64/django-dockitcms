from optparse import OptionParser, make_option

from dockit.datataps import DocumentDataTap

from dockitcms.models import Application, Collection, Index, Subsite, PublicResourceDefinition, VirtualDocumentCollection

from datatap.loading import register_datatap


class DocKitCMSDataTap(DocumentDataTap):
    '''
    Reads and writes from DocKitCMS
    '''
    def __init__(self, instream=None, applications=None, collections=None, indexes=None, subsites=None, publicresources=None, **kwargs):
        '''
        
        :param applications: A list of application slugs
        :param collections: A list of collection keys
        :param indexes: A list of index names
        :param subsites: A list of sugsite slugs
        :param publicresources: A list of public resources urls
        '''
        if instream is None:
            instream = self.order_collection_sources(applications, collections, indexes, subsites, publicresources)
        super(DocKitCMSDataTap, self).__init__(instream, **kwargs)
    
    def order_collection_sources(self, applications, collections, indexes, subsites, publicresources):
        #return in loading order
        result = list()
        exported_collections = list()
        if applications:
            for app_slug in applications:
                result.append(Application.objects.get(slug=app_slug))
        if collections:
            for key in collections:
                collection = Collection.objects.get(key=key)
                result.append(collection)
                if isinstance(collection, VirtualDocumentCollection):
                    exported_collections.append(collection)
        if indexes:
            for name in indexes:#TODO ambigious
                result.extend(Index.objects.filter(name=name))
        if subsites:
            for slug in subsites:
                result.append(Subsite.objects.get(slug=slug))
        if publicresources:
            for pk in publicresources:#TODO find a better identifier, uuid?
                result.append(PublicResourceDefinition.objects.get(pk=pk))
        for collection in exported_collections:
            result.append(collection.get_document())
        return result
    
    command_option_list = [
        make_option('--application',
            action='append',
            type='string',
            dest='applications',
        ),
        make_option('--collection',
            action='append',
            type='string',
            dest='collections',
        ),
        make_option('--index',
            action='append',
            type='string',
            dest='indexes',
        ),
        make_option('--subsite',
            action='append',
            type='string',
            dest='subsites',
        ),
        make_option('--publicresource',
            action='append',
            type='string',
            dest='publicresources',
        )
    ]

register_datatap('DocKitCMS', DocKitCMSDataTap)
