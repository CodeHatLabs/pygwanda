import threading
from time import time


CREATED = '_pygwanda_resource_pool_created__'
RELEASED = '_pygwanda_resource_pool_released__'


class ResourcePool(object):
    """
        Abstract thread-safe class for pooling reusable resources. You must
        override the _CreateNewResource in child classes, and if needed you
        must also override the _FreeResource method.

        Obtain a resource from the pool by calling Get, and release the
        resource back into the pool by calling Release(resource).

        You can get the current status of the pool by calling GetStatus.
    """
    # class defaults
    count_cleared = 0
    count_created = 0
    count_killed_stale = 0
    count_killed_ttl = 0
    count_overflow_discard = 0
    count_served_from_pool = 0
    pool_size_limit = 100
    # TTL - kill resources that have existed for more than max_age seconds
    max_age = 60 * 30
    # kill resources that have been idle for more than max_idle_time seconds
    max_idle_time = 60 * 5

    def __init__(self, **kwargs):
        # create the pool and the pool lock
        self.__pool = []
        self.__pool_lock = threading.Lock()
        # store any keyword settings passed to the constructor
        self.__dict__.update(**kwargs)

    def _CreateNewResource(self):
        """
            Override this method in child classes to return a new
            instance of the pooled resource type.
        """
        return None

    def ClearPool(self, new_pool_size_limit=None):
        """
            def ClearPool(self, new_pool_size_limit=None):
            Clear the pool and destroy all the resources it contains,
            optionally setting a new pool size limit.
        """
        # lock the pool and swap in a new, empty one
        self.__pool_lock.acquire()
        try:
            old_pool = self.__pool
            self.__pool = []
            if new_pool_size_limit != None:
                self.pool_size_limit = new_pool_size_limit
        finally:
            self.__pool_lock.release()
        # free all the resources that were in the old pool
        self.count_cleared += len(old_pool)
        self._DestroyResources(old_pool)

    def _DestroyResources(self, resource_list):
        """
            def _DestroyResources(self, resource_list):
            Destroy the resources passed in resource_list.
        """
        for resource in resource_list:
            self._FreeResource(resource)

    def _FreeResource(self, resource):
        """
            Override this method in child classes to destroy the
                resource instance passed in resource (if needed).
        """
        pass

    def Get(self):
        """
            def Get(self):
            Get a resource instance from the pool. If none are available
            one will be created by calling self._CreateNewResource().
        """
        # snapshot the current moment in time and prepare to validate
        #   the age of the available resources
        now_time = time()
        min_fresh_time = now_time - self.max_idle_time
        min_created_time = now_time - self.max_age
        kill_list = []
        while True:
            # get the oldest instance and remove it from the pool
            resource = self._Pull()
            if not resource:
                break
            resdict = resource.__dict__
            # serve the resource if it is fresh enough, else kill it
            if resdict.get(CREATED, 0) < min_created_time:
                self.count_killed_ttl += 1
                kill_list.append(resource)
            elif resdict.get(RELEASED, 0) < min_fresh_time:
                self.count_killed_stale += 1
                kill_list.append(resource)
            else:
                self.count_served_from_pool += 1
                break
        # destroy resources in the kill list
        self._DestroyResources(kill_list)
        # if no resource was available in the pool then create a new one
        if not resource:
            resource = self._CreateNewResource()
            # store this directly in the instance dict to bypass
            #   any class dunder machines (i.e. __setattr__)
            resource.__dict__[CREATED] = time()
            self.count_created += 1
        return resource

    def GetStatus(self):
        """
            def GetStatus(self):
            Returns a dictionary containing the current state of the pool.
            The following values are returned:
                pool_size (# of available resources in the pool)
                pool_size_limit (max resources allowed in the pool)
                count_created (vs count_served_from_pool)
                count_cleared (destroyed by calls to ClearPool)
                count_killed_stale (max_idle_time timeout)
                count_killed_ttl (max_age timeout)
                count_overflow_discard (exceeded pool_size_limit)
                count_served_from_pool (vs count_created)
        """
        return {
            "pool_size": len(self.__pool),
            "pool_size_limit": self.pool_size_limit,
            "count_created": self.count_created,
            "count_cleared": self.count_cleared,
            "count_killed_stale": self.count_killed_stale,
            "count_killed_ttl": self.count_killed_ttl,
            "count_overflow_discard": self.count_overflow_discard,
            "count_served_from_pool": self.count_served_from_pool,
            }

    def Preheat(self, count):
        for res in [self.Get() for x in range(count)]:
            self.Release(res)

    def _Pull(self):
        """
            def _Pull(self):
            Pull the oldest resource instance from the pool and return it.
        """
        self.__pool_lock.acquire()
        try:
            return self.__pool.pop(0) if self.__pool else None
        finally:
            self.__pool_lock.release()

    def Release(self, resource):
        """
            def Release(self, resource):
            Release a resource instance back to the pool. If the pool is
            full the resource will be destroyed.
        """
        # lock the pool and store the resource
        self.__pool_lock.acquire()
        try:
            if (not self.pool_size_limit) or (len(self.__pool) < self.pool_size_limit):
                # store this directly in the instance dict to bypass
                #   any class dunder machines (i.e. __setattr__)
                resource.__dict__[RELEASED] = time()
                self.__pool.append(resource)
                stored = True
            else:
                stored = False
        finally:
            self.__pool_lock.release()
        if not stored:
            self.count_overflow_discard += 1
            self._FreeResource(resource)

    def RestartPool(self, pool_size_limit):
        """
            def RestartPool(self, pool_size_limit):
            Destroy the current pool and all the resrouces it contains and
            create a new pool with pool_size_limit.
        """
        self.ClearPool(pool_size_limit)

    def ShutDownPool(self):
        """
            def ShutDownPool(self):
            Destroy the current pool and all the resrouces it contains.
            No new pool is created. All future Get calls will return
            new resource instances. All future Release calls will immediately
            destroy the released resource instances.
        """
        self.ClearPool(-1)


# quick and dirty unit test
if __name__ == "__main__":
    print()
    from time import sleep
    class TestResource(object):
        pass
    class TestPool(ResourcePool):
        def _CreateNewResource(self):
            return TestResource()
    pool = TestPool(max_age=5, max_idle_time=3, pool_size_limit=2)
    try:
        print(pool.GetStatus())
        obj = pool.Get()
        print(pool.GetStatus())
        pool.Release(obj)
        print(pool.GetStatus())
        obj = pool.Get()
        print(pool.GetStatus())
        pool.Release(obj)
        print(pool.GetStatus())
        print()
        sleep(3)
        obj1 = pool.Get()
        obj2 = pool.Get()
        obj3 = pool.Get()
        print(pool.GetStatus())
        pool.Release(obj1)
        pool.Release(obj2)
        pool.Release(obj3)
        print(pool.GetStatus())
        obj = pool.Get()
        print(pool.GetStatus())
        pool.Release(obj)
        print(pool.GetStatus())
        print()
        sleep(5)
        obj = pool.Get()
        print(pool.GetStatus())
        pool.Release(obj)
        print(pool.GetStatus())
    finally:
        print()
        pool.ShutDownPool()
        print(pool.GetStatus())
    print()


