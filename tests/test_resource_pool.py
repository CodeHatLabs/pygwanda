import pytest
from freezegun import freeze_time

from pygwanda import ResourcePool


def mock_time(time):
    return freeze_time("2018-11-11 {}".format(time))


class MockResource(object):
    def __init__(self, _num):
        self.num = _num


class MockPool(ResourcePool):
    num = 0
    def _CreateNewResource(self):
        self.num += 1
        return MockResource(self.num)


class TestResourcePool:
    """
    One big test for all functionality of ResourcePool:
    - pool size limit
    - reuse of pooled resources when possible (rather than creation)
    - stale resource removal
    - resource TTL
    """

    def test_pool(self):
        pool = MockPool(max_age=5, max_idle_time=3, pool_size_limit=2)
        expected = pool.GetStatus()

        assert expected['count_created'] == 0
        assert expected['pool_size'] == 0
        assert expected['count_served_from_pool'] == 0

        with mock_time("12:00:00"):
            obj = pool.Get()
            expected['count_created'] = 1
            assert expected == pool.GetStatus()

            pool.Release(obj)
            expected['pool_size'] = 1
            assert expected == pool.GetStatus()

            obj = pool.Get()
            expected['count_served_from_pool'] = 1
            expected['pool_size'] = 0
            assert expected == pool.GetStatus()

            pool.Release(obj)
            expected['pool_size'] = 1
            assert expected == pool.GetStatus()

        with mock_time("12:00:03.001"):
            # 3 seconds later
            assert expected == pool.GetStatus()

            obj1 = pool.Get()
            obj2 = pool.Get()
            obj3 = pool.Get()
            expected['count_created'] = 4
            expected['pool_size'] = 0
            expected['count_killed_stale'] = 1
            assert expected == pool.GetStatus()

            pool.Release(obj1)
            pool.Release(obj2)
            pool.Release(obj3)
            expected['pool_size'] = 2
            expected['count_overflow_discard'] = 1
            assert expected == pool.GetStatus()

            obj = pool.Get()
            expected['pool_size'] = 1
            expected['count_served_from_pool'] = 2
            assert expected == pool.GetStatus()

            pool.Release(obj)
            expected['pool_size'] = 2
            assert expected == pool.GetStatus()

        with mock_time("12:00:08.002"):
            # 5 seconds later
            assert expected == pool.GetStatus()

            obj = pool.Get()
            expected['pool_size'] = 0
            expected['count_created'] = 5
            expected['count_killed_ttl'] = 2
            assert expected == pool.GetStatus()

            pool.Release(obj)
            expected['pool_size'] = 1
            assert expected == pool.GetStatus()

            pool.ShutDownPool()
            expected['pool_size'] = 0
            expected['pool_size_limit'] = -1
            expected['count_cleared'] = 1
            assert expected == pool.GetStatus()
        print()
