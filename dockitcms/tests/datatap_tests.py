from django.utils import unittest

from dockitcms.models import Application, Collection, Index, Subsite, PublicResourceDefinition, VirtualDocumentCollection
from dockitcms.datataps import DocKitCMSDataTap


class DocKitCMSDataTapTestCase(unittest.TestCase):
    def test_write_item(self):
        tap = DocKitCMSDataTap()
        tap.open('w')
        result = tap.write_item({
            'collection': Application._meta.collection,
            'fields': {
                'name': 'test app',
                'slug': 'test-app',
            }
        })
        self.assertTrue(isinstance(result, Application))
        tap.close()
    
    def test_get_item_stream(self):
        Application.objects.all().delete()
        Application(name='test app', slug='test-app').save()
        
        tap = DocKitCMSDataTap(applications=['test-app'])
        tap.open('r')
        items = list(tap.get_item_stream())
        self.assertTrue(items)
        self.assertEqual(len(items), Application.objects.all().count())
        assert len(items)
        tap.close()

from tempfile import mkstemp
import zipfile
import json

from datatap.management.commands import datatap


class DocKitCMSToZipCommandIntregrationTestCase(unittest.TestCase):
    def test_dumpdatatap(self):
        Application.objects.all().delete()
        Application(name='test app', slug='test-app').save()
        filename = mkstemp('zip', 'datataptest')[1]
        cmd = datatap.Command()
        argv = ['manage.py', 'datatap', 'DocKitCMS', '--application=test-app', '--', 'ZipFile', '--file', filename]
        cmd.run_from_argv(argv)
        
        archive = zipfile.ZipFile(filename)
        self.assertTrue('manifest.json' in archive.namelist())
        manifest = json.load(archive.open('manifest.json', 'r'))
        self.assertEqual(len(manifest), Application.objects.all().count())
    
    def test_loaddatatap(self):
        Application.objects.all().delete()
        item = {
            'collection': Application._meta.collection,
            'fields': {
                'name': 'test app',
                'slug': 'test-app',
            }
        }
        filename = mkstemp('zip', 'datataptest')[1]
        archive = zipfile.ZipFile(filename, 'w')
        archive.writestr('manifest.json', json.dumps([item]))
        archive.writestr('originator.txt', 'DocKitCMS')
        archive.close()
        
        cmd = datatap.Command()
        argv = ['manage.py', 'datatap', 'ZipFile', '--file', filename]
        cmd.run_from_argv(argv)
        
        result = Application.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].slug, 'test-app')
