from optparse import OptionParser, make_option

from dockit.datataps import DocumentDataTap

from dockitcms.models import Application, Collection, Index, Subsite, PublicResourceDefinition, VirtualDocumentCollection

from datatap.loading import register_datatap


class DocKitCMSDataTap(DocumentDataTap):
    '''
    Reads and writes from DocKitCMS
    '''
    def __init__(self, applications=[], collections=[], indexes=[], subsites=[], publicresources=[], **kwargs):
        collection_sources = self.order_collection_sources(applications, collections, indexes, subsites, publicresources)
        super(DocumentDataTap, self).__init__(*collection_sources, **kwargs)
    
    def order_collection_sources(self, applications, collections, indexes, subsites, publicresources):
        #return in loading order
        result = list()
        exported_collections = list()
        for app_slug in applications:
            result.append(Application.objects.get(slug=app_slug))
        for key in collections:#TODO not all collections have a key
            collection = Collection.objects.get(key=key)
            result.append(collection)
            if isinstance(collection, VirtualDocumentCollection):
                exported_collections.append(collection)
        for name in indexes:#TODO ambigious
            result.extend(Index.objects.filter(name=name))
        for slug in subsites:
            result.append(Subsite.objects.get(slug=slug))
        for pubres_url in publicresources:#TODO ambigious
            result.append(PublicResourceDefinition.objects.get(url=pubres_url))
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
    
    @classmethod
    def load_from_command_line(cls, arglist):
        '''
        Retuns an instantiated DataTap with the provided arguments from commandline
        '''
        parser = OptionParser(option_list=cls.command_option_list)
        options, args = parser.parse_args(arglist)
        return cls(*args, **options.__dict__)

register_datatap('DocKitCMS', DocKitCMSDataTap)
