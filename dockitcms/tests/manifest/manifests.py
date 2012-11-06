from dockit.manifest.datasources import InlineDataSource
from dockit.manifest.common import ManifestLoader

from dockitcms.manifest.manifests import DockitCMSFixtureManifest
from dockitcms.models import Collection, Subsite, BaseViewPoint

from django.utils import unittest
from django.contrib.sites.models import Site

from fixtures import ManifestFixtures

def wrap_inline_fixture(data):
    return [{'source':'inline',
             'data':data}]

class ManifestTestCase(unittest.TestCase):
    def setUp(self):
        self.manifest_loader = ManifestLoader(manifests={'dockitcmsfixture':DockitCMSFixtureManifest,},
                                              data_sources={'inline':InlineDataSource})
        self.fixtures = ManifestFixtures()
    
    def get_fixture_data(self):
        data = {'loader':'dockitcmsfixture',
                'references': {
                   'applications': ['app1'], #defines app references by natural keys
                   'subsites': ['subsite1'], #includes referenced subsites
                   #CONSIDER: indexes do not have natural keys, but is not needed as we can look for functional equivalence
                   #a special loader can read this info and offer the user to define their own mappings
                },
                'documentdesign': [],#data sources],
                'collections': wrap_inline_fixture(self.fixtures.collection_fixture()),
                'collection_data': {},#self.fixtures.collection_data_fixture(),
                'indexes': wrap_inline_fixture(self.fixtures.index_fixture()),
                'viewpoints': wrap_inline_fixture(self.fixtures.viewpoint_fixture()),
                'subsites': wrap_inline_fixture(self.fixtures.subsite_fixture()),
                'applications': wrap_inline_fixture(self.fixtures.application_fixture()),
               }
        return data
    
    def test_load_dockitcmsfixture_manifest(self):
        data = self.get_fixture_data()
        
        manifest = self.manifest_loader.load_manifest(data)
        objects = manifest.load()
        self.assertEqual(len(objects), 6)
    
    def test_load_dockitcmsfixture_manifest_with_rename_collection(self):
        data = self.get_fixture_data()
        
        dev_subsite = Subsite(url='/dev/',
                              name='Dev Site',
                              sites=[Site.objects.get_current()],
                              mixins=["widgetblock.widgets"],)
        dev_subsite.save()
        
        rename_collections = {
            'team': 'dev.team',
        }
        
        #TODO existing object map is awkward
        existing_object_map = {
            "dockitcms.subsite": [
               ({"name": "Root",}, dev_subsite),
            ]
        }
        
        manifest = self.manifest_loader.load_manifest(data)
        objects = manifest.load(rename_collections=rename_collections, existing_object_map=existing_object_map)
        self.assertEqual(len(objects), 6)
        
        #TODO assert data was coppied over
        
        vp_found = False
        cl_found = False
        for obj in objects:
            if isinstance(obj, BaseViewPoint):
                self.assertEqual(obj.subsite, dev_subsite)
                vp_found = True
            if isinstance(obj, Collection):
                self.assertEqual(obj.key, 'dev.team')
                cl_found = True
        assert vp_found
        assert cl_found
    
    def test_create_dockitcmsfixture_manifest(self):
        dev_subsite = Subsite(url='/dev/',
                              name='Dev Site',
                              sites=[Site.objects.get_current()],
                              mixins=["widgetblock.widgets"],)
        dev_subsite.save()
        data_sources = [(InlineDataSource, [dev_subsite], {})]
        payload = self.manifest_loader.create_manifest_payload('dockitcmsfixture', data_sources)
        self.assertTrue('subsites' in payload)
        self.assertEqual(len(payload['subsites']), 1)
        self.assertEqual(len(payload['subsites'][0]['data']), 1)

