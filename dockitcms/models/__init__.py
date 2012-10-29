from dockitcms.models.design import FieldEntry, DesignMixin, SchemaEntry, DocumentDesign
from dockitcms.models.collection import Application, Collection, BaseCollection
from dockitcms.models.index import Index, CollectionIndex, FilteredCollectionIndex, ModelIndex, FilteredModelIndex, CollectionFilter, ModelFilter, CollectionParam, ModelParam
from dockitcms.models.view_point import Subsite, BaseViewPoint, ViewPoint
from dockitcms.models.mixin import EventMixin, create_document_mixin
from dockitcms.models.recipe import BaseRecipe, Recipe


from dockitcms import fields
from dockitcms import viewpoints

def suite(): #returns a test suite for dockitcms
    import dockitcms
    from django.utils import unittest
    return unittest.defaultTestLoader.loadTestsFromModule(dockitcms)
