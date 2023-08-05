"""These are not really 'tests', but just give a relative measure of
the time to perform various actions between a normal python defaultdict and
the disk cache version of such.

NOTE: this is all low grade not to be fully believed performance estimation!
"""

import collections
import contextlib
import os
import random
import time

import disk_cache_dict

import utils

# data set sizes, should be one larger and one smaller than cache sizes
SMALL_SET = 1000
LARGE_SET = 10000

# cache sizes - this is the max cache size for the dcd
SMALL_CACHE = 10
LARGE_CACHE = 100000

disk_cache_dict.DEBUG = False


@contextlib.contextmanager
def temp_db():
    temp_dir = utils.make_temp_dir('dcd_temp')
    db_file = os.path.join(temp_dir, 'perf_db.dict')
    try:
        yield db_file
    finally:
        utils.remove_dir(temp_dir)


def time_once(func):
    """Adds an additional return value of the run time"""

    def time_func(*args, **kwargs):
        # print '\tstart: {0}'.format(func.__name__)
        start = time.time()
        func(*args, **kwargs)
        total = time.time() - start
        # print '\tend: {0} {1}s'.format(func.__name__, total)
        return total

    return time_func


@time_once
def populate(container, items):
    for key, value in items:
        container[key] = value


@time_once
def random_access(container, keys):
    for _ in range(len(keys)):
        container[random.choice(keys)]


@time_once
def sequential_access(container, keys):
    for test_key in keys:
        container[test_key]


@time_once
def random_update(container, keys):
    for i in range(len(keys)):
        # doing an int to incur some call cost
        container[random.choice(keys)] = int(i)


@time_once
def sequential_update(container, keys):
    for test_key in keys:
        container[test_key] = int(test_key)


def _delete(contaner, key):
    try:
        del contaner[key]
    except KeyError:
        pass


def _update(container, key):
    container[key] = random.getrandbits(16)


def _add(container, _):
    nkey = ''.join([random.choice('abcdefghijklmnopqrstuvwzyz')
                    for _ in range(10)])
    container[nkey] = nkey
    return nkey


def _get(container, key):
    container[key]


@time_once
def random_actions(container, keys):
    actions = [_delete, _update, _add, _get]
    for _ in range(5000):
        action = random.choice(actions)
        key = random.choice(keys)
        nkey = action(container, key)
        if nkey and nkey not in keys:
            keys.append(nkey)


@time_once
def iterate(container, keys):
    citer = iter(container)
    for _ in keys:
        citer.next()


def log(name, py, dcd, log_fd=None, lru=None, in_cache=None,
        backend=None, item_count=None, max_size=None):
    percent = (((dcd - py) / py) * 100)
    print ('{name:' '<30}\tdifference: {percent:' '<5}%\tpy: {py:.4f}s\t'
           'dcd: {dcd:.4f}s'.format(py=py, dcd=dcd, name=name,
                                    percent='{:.2f}'.format(percent)))
    log_spec = ('{name}, {percent}, {py}, {dcd}, {lru}, '
                '{in_cache}, {backend}, {item_count}, {max_size}\n')
    if log_fd:
        logfd.write(log_spec.format(name=name, percent=percent, py=py,
                                    dcd=dcd, lru=lru, max_size=max_size,
                                    in_cache=in_cache, backend=backend,
                                    item_count=item_count))


def gen_tests():
    fd = None
    try:
        fd = open('perflog.csv', 'ab')
        fd.write('name, percent, py, dcd, lru, in_cache, '
                 'backend, item_count, max_size\n')
        for item_count in [SMALL_SET, LARGE_SET]:
            for max_size in [SMALL_CACHE, LARGE_CACHE]:
                for backend in [None, ]:
                    for lru in [True, False]:
                        for in_cache in [True, False]:
                            if not item_count or not max_size:
                                continue
                            if in_cache and max_size < LARGE_CACHE:
                                continue
                            yield item_count, lru, max_size, backend, in_cache, fd
    finally:
        if fd:
            fd.close()


if __name__ == '__main__':
    for item_count, lru, max_size, backend, in_cache, logfd in gen_tests():
        keys = [str(i) for i in range(item_count)]
        items = [(str(i), str(i)) for i in keys]
        print ('Running lru: {0} max_size: {1} backend: {2} '
               'item_count: {3} in_cache_only: {4}'.format(lru, max_size,
                                                           backend or 'default',
                                                           item_count,
                                                           in_cache))
        with temp_db() as db_file:
            pydict = collections.defaultdict(list)
            dcd = disk_cache_dict.DefaultCacheDict(default_factory=list,
                                                   max_size=max_size,
                                                   db_file=db_file, lru=lru,
                                                   current_dictionary=None,
                                                   backend=backend)

            # populate is a special case - doesn't compare to must stuff
            # so we don't keep the time in the aggregate which is slightly a
            # lie
            py_time = populate(pydict, items)
            dcd_time = populate(dcd, items)
            log('Populate', py_time, dcd_time)

            py_sum = dcd_sum = 0

            if in_cache:
                test_keys = dcd._cache.keys()
            else:
                test_keys = keys

            py_time = random_access(pydict, test_keys)
            dcd_time = random_access(dcd, test_keys)
            py_sum += py_time
            dcd_sum += dcd_time
            log('Rand Access', py_time, dcd_time, log_fd=logfd,
                item_count=item_count, lru=lru, max_size=max_size,
                backend=backend, in_cache=in_cache)

            py_time = random_update(pydict, test_keys)
            dcd_time = random_update(dcd, test_keys)
            py_sum += py_time
            dcd_sum += dcd_time
            log('Rand Update', py_time, dcd_time, log_fd=logfd,
                item_count=item_count, lru=lru, max_size=max_size,
                backend=backend, in_cache=in_cache)

            py_time = sequential_access(pydict, test_keys)
            dcd_time = sequential_access(dcd, test_keys)
            py_sum += py_time
            dcd_sum += dcd_time
            log('Sequential Access', py_time, dcd_time, log_fd=logfd,
                item_count=item_count, lru=lru, max_size=max_size,
                backend=backend, in_cache=in_cache)

            py_time = sequential_update(pydict, test_keys)
            dcd_time = sequential_update(dcd, test_keys)
            py_sum += py_time
            dcd_sum += dcd_time
            log('Sequential Update', py_time, dcd_time, log_fd=logfd,
                item_count=item_count, lru=lru, max_size=max_size,
                backend=backend, in_cache=in_cache)

            py_time = iterate(pydict, test_keys)
            dcd_time = iterate(dcd, test_keys)
            py_sum += py_time
            dcd_sum += dcd_time
            log('Iterate', py_time, dcd_time, log_fd=logfd,
                item_count=item_count, lru=lru, max_size=max_size,
                backend=backend, in_cache=in_cache)

            py_time = random_actions(pydict, test_keys)
            dcd_time = random_actions(dcd, test_keys)
            py_sum += py_time
            dcd_sum += dcd_time
            log('Random Actions', py_time, dcd_time, log_fd=logfd,
                item_count=item_count, lru=lru, max_size=max_size,
                backend=backend, in_cache=in_cache)

            print 'Run Average: {0}%\n\n'.format(((dcd_sum / py_sum) * 100))
