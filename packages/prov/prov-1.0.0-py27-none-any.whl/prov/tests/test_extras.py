import unittest

from prov.model import *
from prov.tests.utility import ProvJSONRoundTripTest
from prov.dot import prov_to_dot


EX_NS = Namespace('ex', 'http://example.org/')
EX_OTHER_NS = Namespace('other', 'http://exceptions.example.org/')


class TestExtras(unittest.TestCase):
    def test_dot(self):
        # This is naive.. since we can't programatically check the output is correct
        document = ProvDocument()

        bundle1 = ProvBundle(identifier=EX_NS['bundle1'])
        bundle1.usage(activity=EX_NS['a1'], entity=EX_NS['e1'], identifier=EX_NS['use1'])
        bundle1.entity(identifier=EX_NS['e1'], other_attributes={PROV_ROLE: "sausage"})
        bundle1.activity(identifier=EX_NS['a1'])
        document.activity(EX_NS['a2'])

        bundle2 = ProvBundle(identifier=EX_NS['bundle2'])
        bundle2.usage(activity=EX_NS['aa1'], entity=EX_NS['ee1'], identifier=EX_NS['use2'])
        bundle2.entity(identifier=EX_NS['ee1'])
        bundle2.activity(identifier=EX_NS['aa1'])

        document.add_bundle(bundle1)
        document.add_bundle(bundle2)
        prov_to_dot(document)

    def test_serialize_to_path(self):
        document = ProvDocument()
        document.serialize("output.json")
        os.remove('output.json')

        document.serialize("http://netloc/outputmyprov/submit.php")

    def test_bundle_no_id(self):
        document = ProvDocument()

        def test():
            bundle = ProvBundle()
            document.add_bundle(bundle)

        self.assertRaises(ProvException, test)

    def test_use_set_time_helpers(self):
        dt = datetime.datetime.now()
        document1 = ProvDocument()
        document1.activity(EX_NS['a8'], startTime=dt, endTime=dt)

        document2 = ProvDocument()
        a = document2.activity(EX_NS['a8'])
        a.set_time(startTime=dt, endTime=dt)

        self.assertEqual(document1, document2)
        self.assertEqual(a.get_startTime(), dt)
        self.assertEqual(a.get_endTime(), dt)

    def test_bundle_add_garbage(self):
        document = ProvDocument()

        def test():
            document.add_bundle(document.entity(EX_NS['entity_trying_to_be_a_bundle']))

        self.assertRaises(ProvException, test)

        def test():
            bundle = ProvBundle()
            document.add_bundle(bundle)

        self.assertRaises(ProvException, test)


    def test_bundle_equality_garbage(self):
        document = ProvBundle()
        self.assertNotEqual(document, 1)

    def test_bundle_is_bundle(self):
        document = ProvBundle()
        self.assertTrue(document.is_bundle())

    def test_bundle_in_document(self):
        document = ProvDocument()
        bundle = document.bundle('b')
        self.assertTrue(bundle in bundle.document.bundles)

    def test_bundle_get_record_by_id(self):
        document = ProvDocument()
        self.assertEqual(document.get_record(None), None)

        # record = document.entity(identifier=EX_NS['e1'])
        # self.assertEqual(document.get_record(EX_NS['e1']), record)
        #
        # bundle = document.bundle(EX_NS['b'])
        # self.assertEqual(bundle.get_record(EX_NS['e1']), record)

    def test_bundle_get_records(self):
        document = ProvDocument()

        document.entity(identifier=EX_NS['e1'])
        document.agent(identifier=EX_NS['e1'])
        self.assertEqual(len(document.get_records(ProvAgent)), 1)
        self.assertEqual(len(document.get_records()), 2)

    def test_bundle_name_clash(self):
        document = ProvDocument()

        def test():
            document.bundle(EX_NS['indistinct'])
            document.bundle(EX_NS['indistinct'])

        self.assertRaises(ProvException, test)


        document = ProvDocument()

        def test():
            document.bundle(EX_NS['indistinct'])
            bundle = ProvBundle(identifier=EX_NS['indistinct'])
            document.add_bundle(bundle)

        self.assertRaises(ProvException, test)


    def test_document_helper_methods(self):
        document = ProvDocument()
        self.assertFalse(document.is_bundle())
        self.assertFalse(document.has_bundles())
        document.bundle(EX_NS['b'])
        self.assertTrue(document.has_bundles())
        self.assertEqual(u'<ProvDocument>', str(document))

    # def test_document_unification(self):
    #     # TODO: Improve testing of this...
    #     document = ProvDocument()
    #     bundle = document.bundle(identifier=EX_NS['b'])
    #     e1 = bundle.entity(EX_NS['e'])
    #     e2 = bundle.entity(EX_NS['e'])
    #     unified = document.unified()
    #
    #     self.assertEqual(len(unified._bundles[0]._records), 1)


if __name__ == '__main__':
    unittest.main()