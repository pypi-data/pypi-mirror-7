from yadm.documents import Document
from yadm import fields
from yadm.markers import NotLoaded

from .test_database import BaseDatabaseTest


class QuerySetTest(BaseDatabaseTest):
    def setUp(self):
        super().setUp()

        for n in range(10):
            self.db.db.testdocs.insert({
                'i': n,
                's': 'str({})'.format(n),
            })

        class TestDoc(Document):
            __collection__ = 'testdocs'
            i = fields.IntegerField
            s = fields.StringField

        self.TestDoc = TestDoc
        self.qs = self.db.get_queryset(TestDoc)

    def test_count(self):
        qs = self.qs.find({'i': {'$gte': 6}})
        self.assertEqual(qs.count(), 4)

    def test_len(self):
        qs = self.qs.find({'i': {'$gte': 6}})
        self.assertEqual(len(qs), 4)

    def test_find_one(self):
        td = self.qs.find_one({'i': 7})
        self.assertIsInstance(td, self.TestDoc)
        self.assertTrue(hasattr(td, 'i'))
        self.assertEqual(td.i, 7)

    def test_find(self):
        qs = self.qs.find({'i': {'$gte': 6}})
        self.assertEqual(len([d for d in qs]), 4)
        self.assertEqual({d.i for d in qs}, {6, 7, 8, 9})

    def test_update(self):
        self.qs.find({'i': {'$gte': 6}}).update({'$set': {'s': 'test'}})

        self.assertEqual(self.db.db.testdocs.count(), 10)
        self.assertEqual({d['i'] for d in self.db.db.testdocs.find()}, set(range(10)))
        self.assertEqual(self.db.db.testdocs.find({'s': 'test'}).count(), 4)

        for doc in self.db.db.testdocs.find({'i': {'$lt': 6}}):
            self.assertNotEqual(doc['s'], 'test')
            self.assertTrue(doc['s'].startswith('str('))

        for doc in self.db.db.testdocs.find({'i': {'$gte': 6}}):
            self.assertEqual(doc['s'], 'test')

    def test_update_not_multi(self):
        self.qs.find({'i': {'$gte': 6}}).update({'$set': {'s': 'test'}}, multi=False)

        self.assertEqual(self.db.db.testdocs.count(), 10)
        self.assertEqual({d['i'] for d in self.db.db.testdocs.find()}, set(range(10)))
        self.assertEqual(self.db.db.testdocs.find({'s': 'test'}).count(), 1)

    def test_remove(self):
        self.qs.find({'i': {'$gte': 6}}).remove()
        self.assertEqual(len([d for d in self.qs]), 6)
        self.assertEqual({d.i for d in self.qs}, set(range(6)))

        self.assertEqual(self.db.db.testdocs.count(), 6)
        self.assertEqual({d['i'] for d in self.db.db.testdocs.find()}, set(range(6)))

    def test_sort(self):
        qs = self.qs.find({'i': {'$gte': 6}}).sort(('i', -1))
        self.assertEqual([d.i for d in qs], [9, 8, 7, 6])

    def test_fields(self):
        doc = self.qs.fields('s').find_one({'i': 3})
        self.assertIn('i', doc.__data__)
        self.assertIs(doc.__data__['i'], NotLoaded)
        self.assertEqual(doc.s, 'str(3)')

    def test_fields_all(self):
        doc = self.qs.fields('s').fields_all().find_one({'i': 3})
        self.assertIn('i', doc.__data__)
        self.assertIs(doc.__data__['i'], 3)
        self.assertEqual(doc.s, 'str(3)')
        self.assertEqual(doc.i, 3)

    def test_with_id(self):
        id = self.db.db.testdocs.find_one({'i': 4}, {'_id': True})['_id']
        doc = self.qs.with_id(id)
        self.assertEqual(doc.s, 'str(4)')
        self.assertEqual(doc.i, 4)

    def test_contains(self):
        doc = self.qs.find_one({'i': 0})
        self.assertIn(doc, self.qs)
        self.assertNotIn(doc, self.qs.find({'i': {'$ne': 0}}))
