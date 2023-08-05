from __future__ import unicode_literals
from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, TestEdgeModel, TestEdgeModel2
from mogwai.exceptions import ValidationError, MogwaiQueryError


@attr('unit', 'edge_io')
class TestEdgeIO(BaseMogwaiTestCase):

    def setUp(self):
        super(TestEdgeIO, self).setUp()
        self.v1 = TestVertexModel.create(test_val=8, name='a')
        self.v2 = TestVertexModel.create(test_val=7, name='b')

    def tearDown(self):
        self.v1.delete()
        self.v2.delete()

    def test_model_save_and_load(self):
        """
        Tests that models can be saved and retrieved
        """
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)

        edges = self.v1.outE()
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].id, e1.id)

        e1.delete()

    def test_model_updating_works_properly(self):
        """
        Tests that subsequent saves after initial model creation work
        """
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)

        e1.test_val = 20
        e1.save()

        edges = self.v1.outE()
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].test_val, 20)

        e1.delete()

    def test_model_deleting_works_properly(self):
        """
        Tests that an instance's delete method deletes the instance
        """
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)

        e1.delete()
        edges = self.v1.outE()
        self.assertEqual(len(edges), 0)

        e1.delete()

        # don't actually create a db model and try to delete
        e2 = TestEdgeModel(self.v1, self.v2, test_val=3, name='nonexistant')
        e2.delete()

    def test_reload(self):
        """
        Tests that the reload method performs an inplace update of an instance's values
        """
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)
        e2 = TestEdgeModel.get(e1.id)
        print '\n', e1.id, e2.id, e1 == e2,
        e2.test_val = 5
        e2.save()
        print e2.id

        # we're testing pre-0.5.x expect the reload to not match, must fetch again manually
        e1.reload()
        self.assertEqual(e1.test_val, None)
        e1 = self.v1.outE()[0]
        self.assertEqual(e1.test_val, 5)

        e2.delete()

    def test_all_method_for_known_ids(self):
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)
        e2 = TestEdgeModel.create(self.v1, self.v2, test_val=4)
        results = TestEdgeModel.all([e1.id, e2.id])
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsInstance(result, TestEdgeModel)
            self.assertIn(result, [e1, e2])
        e1.delete()
        e2.delete()

    def test_all_method_for_known_bad_input(self):
        from mogwai.exceptions import MogwaiQueryError
        with self.assertRaises(TypeError):
            results = TestEdgeModel.all()
        with self.assertRaises(MogwaiQueryError):
            results = TestEdgeModel.all(None)
        with self.assertRaises(MogwaiQueryError):
            results = TestEdgeModel.all('test')

    def test_all_method_invalid_length(self):
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)
        e2 = TestEdgeModel.create(self.v1, self.v2, test_val=4)
        from mogwai.exceptions import MogwaiQueryError
        with self.assertRaises(MogwaiQueryError):
            TestEdgeModel.all([e1.id, e2.id, 'invalid'])
        e1.delete()
        e2.delete()

    def test_in_between_method(self):
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)
        results = TestEdgeModel.get_between(self.v1, self.v2)
        self.assertIsInstance(results, list)
        self.assertEqual(results[0], e1)
        e1.delete()

    def test_validation_error(self):
        from mogwai.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            e1 = TestEdgeModel.create(self.v1, None, test_val=3)
        with self.assertRaises(ValidationError):
            e1 = TestEdgeModel.create(None, self.v2, test_val=3)
        with self.assertRaises(ValidationError):
            e1 = TestEdgeModel.create(None, None, test_val=3)

    def test_reload_no_changes(self):
        # NOTE titan 0.4.2 and earlier changes made to an edge deletes and then creates a new edge
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)
        e1.reload()
        e1.delete()

    def test_get_by_id(self):
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)
        results = TestEdgeModel.get(e1.id)
        self.assertIsInstance(results, TestEdgeModel)
        self.assertEqual(results, e1)

        from mogwai.exceptions import MogwaiQueryError
        with self.assertRaises(TestEdgeModel.DoesNotExist):
            results = TestEdgeModel.get(None)

        with self.assertRaises(TestEdgeModel.DoesNotExist):
            results = TestEdgeModel.get('nonexistant')

        e2 = TestEdgeModel2.create(self.v1, self.v2, test_val=2)
        with self.assertRaises(TestEdgeModel.WrongElementType):
            results = TestEdgeModel.get(e2.id)

        e1.delete()
        e2.delete()

    def test_inV_ouV_vertex_traversal(self):
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=3)

        v1 = e1.outV()
        v2 = e1.inV()
        self.assertEqual(v1, self.v1)
        self.assertEqual(v2, self.v2)

        e1.delete()