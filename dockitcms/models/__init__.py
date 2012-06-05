from design import FieldEntry, DesignMixin, SchemaEntry, DocumentDesign
from collection import Application, Collection, BaseCollection
from index import Index, CollectionIndex, FilteredCollectionIndex, ModelIndex, FilteredModelIndex, CollectionFilter, ModelFilter, CollectionParam, ModelParam
from view_point import Subsite, BaseViewPoint, ViewPoint
from mixin import EventMixin, create_document_mixin
from recipe import BaseRecipe, Recipe


from dockitcms import fields
from dockitcms import viewpoints

def suite(): #returns a test suite for dockitcms
    from dockitcms import tests as test_module
    from django.utils import unittest
    return unittest.defaultTestLoader.loadTestsFromModule(test_module)
