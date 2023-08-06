"""Tests for vumi.persist.txriak_manager."""

from twisted.internet.defer import inlineCallbacks

from vumi.persist.model import Manager
from vumi.tests.helpers import VumiTestCase, import_skip


class DummyModel(object):

    bucket = "dummy_model"

    VERSION = None
    MIGRATORS = None

    def __init__(self, manager, key, _riak_object=None):
        self.manager = manager
        self.key = key
        self._riak_object = _riak_object

    @classmethod
    def load(cls, manager, key, result=None):
        return manager.load(cls, key, result=result)

    def set_riak(self, riak_object):
        self._riak_object = riak_object

    def get_data(self):
        return self._riak_object.get_data()

    def set_data(self, data):
        self._riak_object.set_data(data)

    def add_index(self, index_name, key):
        self._riak_object.add_index(index_name, key)


class CommonRiakManagerTests(object):
    """Common tests for Riak managers.

    Tests assume self.manager is set to a suitable Riak
    manager.
    """

    def mkdummy(self, key, data=None):
        dummy = DummyModel(self.manager, key)
        dummy.set_riak(self.manager.riak_object(dummy, key))
        if data is not None:
            dummy.set_data(data)
        return dummy

    def test_from_config(self):
        manager_cls = self.manager.__class__
        manager = manager_cls.from_config({'bucket_prefix': 'test.'})
        self.assertEqual(manager.__class__, manager_cls)
        self.assertEqual(manager.load_bunch_size,
                         manager.DEFAULT_LOAD_BUNCH_SIZE)
        self.assertEqual(manager.mapreduce_timeout,
                         manager.DEFAULT_MAPREDUCE_TIMEOUT)

    def test_from_config_with_bunch_size(self):
        manager_cls = self.manager.__class__
        manager = manager_cls.from_config({'bucket_prefix': 'test.',
                                           'load_bunch_size': 10,
                                           })
        self.assertEqual(manager.load_bunch_size, 10)

    def test_from_config_with_mapreduce_timeout(self):
        manager_cls = self.manager.__class__
        manager = manager_cls.from_config({'bucket_prefix': 'test.',
                                           'mapreduce_timeout': 1000,
                                           })
        self.assertEqual(manager.mapreduce_timeout, 1000)

    def test_sub_manager(self):
        sub_manager = self.manager.sub_manager("foo.")
        self.assertEqual(sub_manager.client, self.manager.client)
        self.assertEqual(sub_manager.bucket_prefix, 'test.foo.')

    def test_bucket_name_on_modelcls(self):
        dummy = self.mkdummy("bar")
        bucket_name = self.manager.bucket_name(type(dummy))
        self.assertEqual(bucket_name, "test.dummy_model")

    def test_bucket_name_on_instance(self):
        dummy = self.mkdummy("bar")
        bucket_name = self.manager.bucket_name(dummy)
        self.assertEqual(bucket_name, "test.dummy_model")

    def test_bucket_for_modelcls(self):
        dummy_cls = type(self.mkdummy("foo"))
        bucket1 = self.manager.bucket_for_modelcls(dummy_cls)
        bucket2 = self.manager.bucket_for_modelcls(dummy_cls)
        self.assertEqual(id(bucket1), id(bucket2))
        self.assertEqual(bucket1.get_name(), "test.dummy_model")

    def test_riak_object(self):
        dummy = DummyModel(self.manager, "foo")
        riak_object = self.manager.riak_object(dummy, "foo")
        self.assertEqual(riak_object.get_data(), {'$VERSION': None})
        self.assertEqual(riak_object.get_content_type(), "application/json")
        self.assertEqual(riak_object.get_bucket().get_name(),
                         "test.dummy_model")
        self.assertEqual(riak_object.get_key(), "foo")

    @Manager.calls_manager
    def test_store_and_load(self):
        dummy1 = self.mkdummy("foo", {"a": 1})
        result1 = yield self.manager.store(dummy1)
        self.assertEqual(dummy1, result1)

        dummy2 = yield self.manager.load(DummyModel, "foo")
        self.assertEqual(dummy2.get_data(), {"a": 1})

    @Manager.calls_manager
    def test_delete(self):
        dummy1 = self.mkdummy("foo", {"a": 1})
        yield self.manager.store(dummy1)

        dummy2 = yield self.manager.load(DummyModel, "foo")
        yield self.manager.delete(dummy2)

        dummy3 = yield self.manager.load(DummyModel, "foo")
        self.assertEqual(dummy3, None)

    @Manager.calls_manager
    def test_load_missing(self):
        dummy = self.mkdummy("unknown")
        result = yield self.manager.load(DummyModel, dummy.key)
        self.assertEqual(result, None)

    @Manager.calls_manager
    def test_load_all_bunches(self):
        yield self.manager.store(self.mkdummy("foo", {"a": 0}))
        yield self.manager.store(self.mkdummy("bar", {"a": 1}))
        yield self.manager.store(self.mkdummy("baz", {"a": 2}))
        self.manager.load_bunch_size = load_bunch_size = 2

        keys = ["foo", "unknown", "bar", "baz"]

        result_data = []
        for result_bunch in self.manager.load_all_bunches(DummyModel, keys):
            bunch = yield result_bunch
            self.assertTrue(len(bunch) <= load_bunch_size)
            result_data.extend(result.get_data() for result in bunch)
        result_data.sort(key=lambda d: d["a"])
        self.assertEqual(result_data, [{"a": 0}, {"a": 1}, {"a": 2}])

    @Manager.calls_manager
    def test_run_riak_map_reduce(self):
        dummies = [self.mkdummy(str(i), {"a": i}) for i in range(4)]
        for dummy in dummies:
            dummy.add_index('test_index_bin', 'test_key')
            yield self.manager.store(dummy)

        mr = self.manager.riak_map_reduce()
        mr.index('test.dummy_model', 'test_index_bin', 'test_key')

        mr_results = []

        def mapper(manager, link):
            self.assertEqual(manager, self.manager)
            mr_results.append(link)
            dummy = self.mkdummy(link.get_key())
            return manager.load(DummyModel, dummy.key)

        results = yield self.manager.run_map_reduce(mr, mapper)
        results.sort(key=lambda d: d.key)
        expected_keys = [str(i) for i in range(4)]
        self.assertEqual([d.key for d in results], expected_keys)
        mr_results.sort(key=lambda l: l.get_key())
        self.assertEqual([l.get_key() for l in mr_results], expected_keys)

    @Manager.calls_manager
    def test_run_riak_map_reduce_with_timeout(self):
        dummies = [self.mkdummy(str(i), {"a": i}) for i in range(4)]
        for dummy in dummies:
            dummy.add_index('test_index_bin', 'test_key')
            yield self.manager.store(dummy)

        # override mapreduce_timeout for testing
        self.manager.mapreduce_timeout = 1  # millisecond

        mr = self.manager.riak_map_reduce()
        mr.index('test.dummy_model', 'test_index_bin', 'test_key')

        try:
            yield self.manager.run_map_reduce(mr, lambda m, l: None)
        except Exception, err:
            msg = str(err)
            self.assertTrue(msg.startswith("Error running MapReduce"
                                           " operation."))
            self.assertTrue(msg.endswith("Body: '{\"error\":\"timeout\"}'"))
        else:
            self.fail("Map reduce operation did not timeout")

    @Manager.calls_manager
    def test_purge_all(self):
        dummy = self.mkdummy("foo", {"baz": 0})
        yield self.manager.store(dummy)
        yield self.manager.purge_all()
        result = yield self.manager.load(DummyModel, dummy.key)
        self.assertEqual(result, None)


class TestTxRiakManager(CommonRiakManagerTests, VumiTestCase):

    @inlineCallbacks
    def setUp(self):
        try:
            from vumi.persist.txriak_manager import TxRiakManager
            from riakasaurus import transport
        except ImportError, e:
            import_skip(e, 'riakasaurus', 'riakasaurus.riak')
        self.pbc_transport = transport.PBCTransport
        self.http_transport = transport.HTTPTransport
        self.manager = TxRiakManager.from_config({'bucket_prefix': 'test.'})
        self.add_cleanup(self.manager.purge_all)
        yield self.manager.purge_all()

    def test_call_decorator(self):
        self.assertEqual(type(self.manager).call_decorator, inlineCallbacks)

    def test_transport_class_protocol_buffer(self):
        manager_class = type(self.manager)
        manager = manager_class.from_config({
            'transport_type': 'protocol_buffer',
            'bucket_prefix': 'test.',
            })
        self.assertEqual(type(manager.client.transport),
                         self.pbc_transport)
        return manager.client.transport.quit()

    def test_transport_class_http(self):
        manager_class = type(self.manager)
        manager = manager_class.from_config({
            'transport_type': 'http',
            'bucket_prefix': 'test.',
            })
        self.assertEqual(type(manager.client.transport),
                         self.http_transport)

    def test_transport_class_default(self):
        manager_class = type(self.manager)
        manager = manager_class.from_config({
            'bucket_prefix': 'test.',
            })
        self.assertEqual(type(manager.client.transport),
                         self.http_transport)
