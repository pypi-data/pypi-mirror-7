#! /usr/bin/env python

import unittest

import pyslet.odata2.csdl as edm
import pyslet.odata2.edmx as edmx
from pyslet.vfs import OSFilePath as FilePath
from test_odata2_core import DataServiceRegressionTests

from pyslet.odata2.memds import *       # noqa


def suite():
    loader = unittest.TestLoader()
    loader.testMethodPrefix = 'test'
    return unittest.TestSuite((
        loader.loadTestsFromTestCase(MemDSTests),
        loader.loadTestsFromTestCase(RegressionTests)
    ))


def load_tests(loader, tests, pattern):
    return suite()


TEST_DATA_DIR = FilePath(
    FilePath(__file__).abspath().split()[0], 'data_odatav2')


class MemDSTests(unittest.TestCase):

    def setUp(self):        # noqa
        self.doc = edmx.Document()
        mdpath = TEST_DATA_DIR.join('sample_server', 'metadata.xml')
        with mdpath.open('rb') as f:
            self.doc.Read(f)
        self.schema = self.doc.root.DataServices['SampleModel']
        self.containerDef = self.doc.root.DataServices[
            "SampleModel.SampleEntities"]
        self.container = InMemoryEntityContainer(self.containerDef)
        self.employees = self.container.entityStorage['Employees']

    def tearDown(self):     # noqa
        pass

    def test_constructors(self):
        es = self.schema['SampleEntities.Employees']
        self.assertTrue(isinstance(es.OpenCollection(), EntityCollection))

    def test_length(self):
        es = self.schema['SampleEntities.Employees']
        self.assertTrue(isinstance(es, edm.EntitySet))
        with es.OpenCollection() as collection:
            self.assertTrue(len(collection) == 0, "Length on load")
            self.employees.data[u"ABCDE"] = (
                u"ABCDE", u"John Smith", None, None)
            self.assertTrue(len(collection) == 1, "Length after insert")
            self.employees.data[u"FGHIJ"] = (
                u"FGHIJ", u"Jane Smith", None, None)
            self.assertTrue(len(collection) == 2, "Length after 2xinsert")
            del collection[u"ABCDE"]
            self.assertTrue(len(collection) == 1, "Length after delete")

    def test_entity_set_data(self):
        self.employees.data[u"ABCDE"] = (u"ABCDE", u"John Smith", None, None)
        self.employees.data[u"FGHIJ"] = (u"FGHIJ", u"Jane Smith", None, None)


class RegressionTests(DataServiceRegressionTests):

    def setUp(self):        # noqa
        DataServiceRegressionTests.setUp(self)
        self.container = InMemoryEntityContainer(
            self.ds['RegressionModel.RegressionContainer'])

    def test_all_tests(self):
        self.run_combined()


if __name__ == "__main__":
    unittest.main()
