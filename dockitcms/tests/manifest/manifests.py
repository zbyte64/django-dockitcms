from dockit.manifest.datasources import InlineDataSource
from dockit.manifest.common import ManifestLoader

from dockitcms.manifest.manifests import DockitCMSFixtureManifest

from django.utils import unittest

from fixtures import ManifestFixtures

def wrap_inline_fixture(data):
    return [{'source':'inline',
             'data':data}]

class ManifestTestCase(unittest.TestCase):
    def setUp(self):
        self.manifest_loader = ManifestLoader(manifests={'dockitcmsfixture':DockitCMSFixtureManifest,},
                                              data_sources={'inline':InlineDataSource})
        self.fixtures = ManifestFixtures()
    
    def test_load_dockitcmsfixture_manifest(self):
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
        
        manifest = self.manifest_loader.load_manifest(data)
        objects = manifest.load()
        self.assertEqual(len(objects), 6)
        assert False, str(objects)
    
    def test_create_dockitcmsfixture_manifest(self):
        from dockit.models import TemporaryDocument
        foo = TemporaryDocument(extrafield=1)
        data_sources = [(InlineDataSource, [foo], {})]
        payload = self.manifest_loader.create_manifest_payload('dockitcmsfixture', data_sources)
        self.assertEqual(len(payload['data']), 1)


