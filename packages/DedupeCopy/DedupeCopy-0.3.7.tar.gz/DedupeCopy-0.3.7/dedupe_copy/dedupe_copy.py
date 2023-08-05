"""Find duplicate files on a file system


work_queue -> files put on here by WalkThread(s), read by ReadThread(s)
result_queue -> Put to by ReadThreads(s) read by ResultProcessor
progress_queue -> read by ProgressThread and put to by all others
walk_queue -> holds directories discovered by WalkThread(s)
copy_queue -> read by CopyThread(s) put to by queue_copy_work

TODO::
    Proper logging
    Unit tests
    better structure in cli
"""

from collections import defaultdict, Counter
import datetime
import fnmatch
import functools
import hashlib
import os
import Queue
import random
import shutil
import tempfile
import threading
import time

from disk_cache_dict import CacheDict, DefaultCacheDict

# For message output
HIGH_PRIORITY = 1
MEDIUM_PRIORITY = 5
LOW_PRIORITY = 10

MAX_TARGET_QUEUE_SIZE = 50000

READ_CHUNK = 1048576  # 1 MB

INCREMENTIAL_SAVE_SIZE = 50000
PATH_RULES = {'mtime': 'Put each file into a directory of the form YYYY_MM',
              'no_change': 'Preserve directory structure from "read_path" up',
              'extension': 'Put all items into directories of their extension',
              }


# Path rule matching

def _path_rules_parser(rules, dest_dir, extension, mtime_str, size,
                       source_dirs, src, read_paths):
    """Builds a path based on the path rules for the given extension pattern"""
    rule_list = rules.get(_best_match(rules.keys(), extension), ['no_change'])
    dest = None
    for rule in rule_list:
        if rule == 'mtime':
            dest_dir = os.path.join(dest_dir, mtime_str)
        elif rule == 'extension':
            dest_dir = os.path.join(dest_dir, extension)
        elif rule == 'no_change':
            # remove the path up to our source_dirs from src so we don't
            # preserve the structure "below" where our copy is from
            for p in read_paths:
                if source_dirs.startswith(p):
                    source_dirs = source_dirs.replace(p, '', 1)
            if source_dirs.startswith(os.sep):
                source_dirs = source_dirs[1:]
            dest_dir = os.path.join(dest_dir, source_dirs)
    if dest is None:
        dest = os.path.join(dest_dir, src)
    return dest, dest_dir


def _best_match(extensions, ext):
    """Returns the best matching extension_pattern for ext from a list of
    extension patterns or none if no extension applies
    """
    ext = '*.{0}'.format(ext)
    if ext in extensions:
        return ext
    matches = []
    for extension_pattern in extensions:
        if fnmatch.fnmatch(ext, extension_pattern):
            matches.append(extension_pattern)
    if not matches:
        return None
    # take the pattern that is the closest to the given extension by length
    best = matches.pop()
    score = abs(len(best.replace('?', '').replace('*', '')) - len(ext))
    for m in matches:
        current_score = abs(
            len(m.replace('?', '').replace('*', '')) - len(ext))
        if current_score < score:
            score = current_score
            best = m
    return best


def _match_extension(extensions, fn):
    """Returns true if extensions is empty"""
    if not extensions:
        return True
    for included_pattern in extensions:
        # first look for an exact match
        if fn.endswith(included_pattern):
            return True
        # now try a pattern match
        if fnmatch.fnmatch(fn, included_pattern):
            return True
    return False


def _throttle_puts(current_size):
    """Delay for some factor to avoid overloading queues"""
    time.sleep(min((current_size * 2) / float(MAX_TARGET_QUEUE_SIZE), 60))


# Worker threads

class CopyThread(threading.Thread):

    """Copy to target_path for given extensions (all if None)"""

    def __init__(self, work_queue, target_path, read_paths, stop_event,
                 extensions=None, path_rules=None, progress_queue=None):
        super(CopyThread, self).__init__()
        self.work = work_queue
        self.target_path = target_path
        self.extensions = extensions
        self.path_rules = path_rules
        self.read_paths = read_paths
        self.stop_event = stop_event
        self.progress_queue = progress_queue
        self.daemon = True

    def run(self):
        while not self.work.empty() or not self.stop_event.is_set():
            try:
                src, mtime, size = self.work.get(True, .1)
                ext = lower_extension(src)
                if not ext:
                    ext = 'no_extension'
                if not _match_extension(self.extensions, src):
                    continue
                if self.path_rules is not None:
                    source_dirs = os.path.dirname(src)
                    dest, dest_dir = self.path_rules(self.target_path, ext,
                                                     mtime, size, source_dirs,
                                                     os.path.basename(src),
                                                     self.read_paths)
                else:
                    dest = os.path.join(self.target_path, ext, mtime,
                                        os.path.basename(src))
                    dest_dir = os.path.dirname(dest)
                try:
                    if not os.path.exists(dest_dir):
                        try:
                            os.makedirs(dest_dir)
                        except Exception:
                            # thread race if it now exists, no issue
                            if not os.path.exists(dest_dir):
                                raise
                    shutil.copy2(src, dest)
                    self.progress_queue.put((LOW_PRIORITY, 'copied', src,
                                             dest))
                except Exception as e:
                    self.progress_queue.put((MEDIUM_PRIORITY, 'error',
                                             src,
                                             'Error copying to {dest}: {e}'.format(
                                                 dest=repr(dest), e=e)))
            except Queue.Empty:
                pass


class ResultProcessor(threading.Thread):

    """Takes results of work queue and builds result data structure"""

    def __init__(self, stop_event, result_queue, collisions, manifest,
                 progress_queue=None, keep_empty=False, save_event=None):
        super(ResultProcessor, self).__init__()
        self.stop_event = stop_event
        self.results = result_queue
        self.collisions = collisions
        self.md5_data = manifest
        self.progress_queue = progress_queue
        self.empty = keep_empty
        self.save_event = save_event
        self.daemon = True

    def run(self):
        processed = 0
        while not self.results.empty() or not self.stop_event.is_set():
            if self.save_event and self.save_event.is_set():
                time.sleep(1)
                continue
            src = ''
            try:
                md5, size, mtime, src = self.results.get(True, .1)
                collision = (md5 in self.md5_data)
                if self.empty and md5 == 'd41d8cd98f00b204e9800998ecf8427e':
                    collision = False
                self.md5_data[md5].append([src, size, mtime])
                if collision:
                    self.collisions[md5] = self.md5_data[md5]
                processed += 1
            except Queue.Empty:
                pass
            except Exception as err:
                self.progress_queue.put((MEDIUM_PRIORITY, 'error', src,
                                         "ERROR in result processing: {e}".format(e=err)))
            if processed > INCREMENTIAL_SAVE_SIZE:
                self.progress_queue.put((HIGH_PRIORITY, 'message',
                                         'Hit incremental save size, '
                                         'will save manifest files'))
                processed = 0
                try:
                    self.md5_data.save()
                except Exception as e:
                    self.progress_queue.put((MEDIUM_PRIORITY, 'error',
                                             self.md5_data.path,
                                             "ERROR Saving incremental: {e}".format(e=e)))


class ReadThread(threading.Thread):

    """Thread worker for hashing"""

    def __init__(self, work_queue, result_queue, stop_event, progress_queue,
                 save_event=None):
        super(ReadThread, self).__init__()
        self.work = work_queue
        self.results = result_queue
        self.stop_event = stop_event
        self.progress_queue = progress_queue
        self.save_event = save_event
        self.daemon = True

    def run(self):
        while not self.stop_event.is_set() or not self.work.empty():
            if self.save_event and self.save_event.is_set():
                time.sleep(1)
                continue
            src = ''
            try:
                src = self.work.get(True, .1)
                try:
                    _throttle_puts(self.results.qsize())
                    self.results.put(read_file(src))
                except Exception as e:
                    self.progress_queue.put((MEDIUM_PRIORITY, 'error',
                                             src, e))
            except Queue.Empty:
                pass
            except Exception as err:
                self.progress_queue.put((MEDIUM_PRIORITY, 'error', src,
                                         "ERROR in file read: {e}".format(
                                             e=err)))


class ProgressThread(threading.Thread):

    """All Status updates should come through here.
    Can process raw messages as well as message of the type:
        message, msg
        file, path
        accepted, path
        ignored, path, reason
        error, path, reason
        copied, src, dest
        not_copied, path
    """
    file_count_log_interval = 1000

    def __init__(self, work_queue, result_queue, progress_queue,
                 walk_queue, stop_event, save_event):

        super(ProgressThread, self).__init__()
        self.work = work_queue
        self.result_queue = result_queue
        self.progress_queue = progress_queue
        self.walk_queue = walk_queue
        self.stop_event = stop_event
        self.daemon = True
        self.last_accepted = None
        self.file_count = 0
        self.directory_count = 0
        self.accepted_count = 0
        self.ignored_count = 0
        self.error_count = 0
        self.copied_count = 0
        self.not_copied_count = 0
        self.last_copied = None
        self.save_event = save_event

    def do_log_dir(self, path):
        self.directory_count += 1

    def do_log_file(self, path):
        self.file_count += 1
        if self.file_count % self.file_count_log_interval == 0 or\
                self.file_count == 1:
            message = ('Discovered {total_files} files (dirs: {dirs}), accepted '
                       '{accepted}.\nWork queue has {count} items. '
                       'Progress queue has {pcount} items. Walk queue has '
                       '{wcount} items.\nCurrent file: {fn} '
                       '(last accepted: {afn})'.format(
                           total_files=self.file_count,
                           dirs=self.directory_count,
                           accepted=self.accepted_count,
                           count=self.work.qsize(),
                           pcount=self.progress_queue.qsize(),
                           wcount=self.walk_queue.qsize(),
                           fn=repr(path), afn=repr(self.last_accepted)))
            print message

    def do_log_copied(self, src, dest):
        self.copied_count += 1
        if self.copied_count % self.file_count_log_interval == 0 or\
                self.copied_count == 1:
            print ('Copied {copied} items. Skipped {skip} items. Last file: '
                   '{src} -> {dest}'.format(copied=self.copied_count,
                                            skip=self.not_copied_count,
                                            src=repr(src),
                                            dest=repr(dest)))
        self.last_copied = src

    def do_log_not_copied(self, path):
        self.not_copied_count += 1

    def do_log_accepted(self, path):
        self.accepted_count += 1
        self.last_accepted = path

    def do_log_ignored(self, path, reason):
        self.ignored_count += 1
        print 'Ignoring {src} for {reason}'.format(src=repr(path),
                                                   reason=repr(reason))

    def do_log_error(self, path, reason):
        self.error_count += 1
        print 'Error for {src} for {reason}'.format(src=repr(path),
                                                    reason=repr(reason))

    def do_log_message(self, message):
        print message

    def run(self):
        """Run loop that slurps items off the progress queue and dispatches
        the correct handler
        """
        last_update = time.time()
        while not self.stop_event.is_set() or not self.progress_queue.empty():
            try:
                # we should only be getting directories on this queue
                item = self.progress_queue.get(True, .1)[1:]
                method_name = 'do_log_{0}'.format(item[0])
                method = getattr(self, method_name)
                method(*item[1:])
                last_update = time.time()
            except Queue.Empty:
                if self.save_event and self.save_event.is_set():
                    print 'Saving...'
                    time.sleep(1)
                if time.time() - last_update > 60:
                    last_update = time.time()
                    print ('Status:  Work Queue Size: {work}. '
                           'Result Queue Size: {result}. '
                           'Progress Queue Size: {progress}. '
                           'Walk Queue Size: {walk}'.format(
                               work=self.work.qsize(),
                               result=self.result_queue.qsize(),
                               progress=self.progress_queue.qsize(),
                               walk=self.walk_queue.qsize()))
                pass
            except Exception as e:
                print 'Failed in progress thread:', e
        if self.file_count:
            print 'Results from walk:'
            print 'Total files: {0}'.format(self.file_count)
            print 'Total accepted: {0}'.format(self.accepted_count)
            print 'Total ignored: {0}'.format(self.ignored_count)
        if self.copied_count:
            print 'Results from copy:'
            print 'Total copied: {0}'.format(self.copied_count)
            print 'Total skipped: {0}'.format(self.not_copied_count)
        print 'Total errors: {0}'.format(self.error_count)


class WalkThread(threading.Thread):

    def __init__(self, walk_queue, stop_event, extensions, ignore, work_queue,
                 already_processed, progress_queue, save_event):
        super(WalkThread, self).__init__()
        self.walk = walk_queue
        self.work = work_queue
        self.extensions = extensions
        self.ignore = ignore
        self.already_processed = already_processed
        self.progress = progress_queue
        self.stop_event = stop_event
        self.save_event = save_event
        self.daemon = True

    def run(self):
        while not self.walk.empty() or not self.stop_event.is_set():
            if self.save_event and self.save_event.is_set():
                time.sleep(1)
                continue
            src = None
            try:
                # we should only be getting directories on this queue
                src = self.walk.get(True, .5)
                if not os.path.exists(src):
                    # are we dealing with a network path, retry after sleeping
                    time.sleep(3)
                    if not os.path.exists(src):
                        raise RuntimeError(
                            "Directory disappeared during walk: {src}".format(
                                src=repr(src)))
                if not os.path.isdir(src):
                    raise ValueError(
                        "Unexpected file in work queue: {src}".format(
                            src=repr(src)))
                # process the files, sending items off to be read and getting
                # new directories put onto the queue we read from
                _distribute_work(src, self.already_processed, self.ignore,
                                 self.extensions, self.progress, self.work,
                                 self.walk)
            except Queue.Empty:
                pass
            except Exception as e:
                self.progress.put((MEDIUM_PRIORITY, 'error', src, e))


# walk / hash helpers

def _distribute_work(src, already_processed, ignore, extensions,
                     progress_queue, work_queue, walk_queue):
    # if the path is excluded, don't traverse
    if ignore:
        for ignored_pattern in ignore:
            if fnmatch.fnmatch(src, ignored_pattern):
                progress_queue.put((HIGH_PRIORITY, 'ignored', src,
                                    ignored_pattern))
                return
    for item in os.listdir(src):
        fn = os.path.join(src, item)
        if os.path.isdir(fn):
            progress_queue.put((LOW_PRIORITY, 'dir', fn))
            _throttle_puts(walk_queue.qsize())
            walk_queue.put(fn)
            continue
        progress_queue.put((LOW_PRIORITY, 'file', fn))
        # first check if this has already been processed, then
        # check the ignore file pattern first, then check if we
        # need to process the extension pattern
        action_required = True
        if fn in already_processed:
            action_required = False
        if ignore and action_required:
            for ignored_pattern in ignore:
                if fnmatch.fnmatch(fn, ignored_pattern):
                    action_required = False
                    progress_queue.put((HIGH_PRIORITY, 'ignored', fn,
                                        ignored_pattern))
                    break
        if extensions and action_required:
            if not _match_extension(extensions, fn):
                action_required = False  # didn't find a match
        if action_required:
            _throttle_puts(walk_queue.qsize())
            work_queue.put(fn)
            progress_queue.put((HIGH_PRIORITY, 'accepted', fn))


def _walk_fs(read_paths, extensions, ignore, work_queue, walk_queue,
             already_processed, progress_queue, walk_threads=4,
             save_event=None):
    walk_done = threading.Event()
    walkers = []
    progress_queue.put((HIGH_PRIORITY, 'message',
                        'Starting {0} walk workers'.format(walk_threads)))
    for _ in range(walk_threads):
        w = WalkThread(walk_queue, walk_done, extensions, ignore, work_queue,
                       already_processed, progress_queue, save_event)
        walkers.append(w)
        w.start()
    for src in read_paths:
        _throttle_puts(walk_queue.qsize())
        walk_queue.put(src)
    walk_done.set()
    for w in walkers:
        w.join()


def lower_extension(src):
    _, extension = os.path.splitext(src)
    return extension[1:].lower()


def hash_file(src):
    """ Hash a file, returning the md5 hexdigest

    :param src: Full path of the source file.
    """
    checksum = hashlib.md5()
    with open(src, 'rb') as inhandle:
        chunk = inhandle.read(READ_CHUNK)
        while chunk:
            checksum.update(chunk)
            chunk = inhandle.read(READ_CHUNK)
    return checksum.hexdigest()


def read_file(src):
    size = os.path.getsize(src)
    mtime = os.path.getmtime(src)
    md5 = hash_file(src)
    return (md5, size, mtime, src)


def _extension_report(md5_data, show_count=10):
    """Print details for each extension, sorted by total size, return
    total size for all extensions
    """
    sizes = Counter()
    extension_counts = Counter()
    for key, info in md5_data.iteritems():
        for items in info:
            extension = lower_extension(items[0])
            if not extension:
                extension = 'no_extension'
            sizes[extension] += items[1]
            extension_counts[extension] += 1
    print 'Top {show_count} extensions by size:'.format(show_count=show_count)
    for key, _ in zip(sorted(sizes, key=sizes.get, reverse=True),
                      range(show_count)):
        print '  {ext}: {total_size} bytes'.format(ext=key,
                                                   total_size=sizes[key])
    print 'Top {show_count} extensions by count:'.format(show_count=show_count)
    for key, _ in zip(sorted(extension_counts, key=extension_counts.get,
                             reverse=True), range(show_count)):
        print '  {ext}: {count}'.format(ext=key,
                                        count=extension_counts[key])
    return sum(sizes.viewvalues())


# duplicate finding

def find_duplicates(read_paths, work_queue, result_queue, manifest,
                    collisions, result_src=None, extensions=None, ignore=None,
                    progress_queue=None, walk_threads=4, read_threads=8,
                    keep_empty=False, save_event=None, walk_queue=None):
    work_stop_event = threading.Event()
    result_stop_event = threading.Event()
    result_processor = ResultProcessor(result_stop_event, result_queue,
                                       collisions, manifest,
                                       keep_empty=keep_empty,
                                       progress_queue=progress_queue,
                                       save_event=save_event)
    result_processor.start()
    result_fh = None
    if result_src is not None:
        result_fh = open(result_src, 'ab')
        result_fh.write('Src: {0}\n'.format(read_paths))
        result_fh.write('Collision #, MD5, Path, Size (bytes), mtime\n')
    try:
        progress_queue.put((HIGH_PRIORITY, 'message',
                            'Starting {0} read workers'.format(read_threads)))
        work_threads = []
        for _ in range(read_threads):
            w = ReadThread(work_queue, result_queue, work_stop_event,
                           progress_queue, save_event=save_event)
            work_threads.append(w)
            w.start()
        _walk_fs(read_paths, extensions, ignore, work_queue, walk_queue,
                 manifest.read_sources, progress_queue=progress_queue,
                 walk_threads=walk_threads, save_event=save_event)
        while not work_queue.empty():
            progress_queue.put((HIGH_PRIORITY, 'message',
                                'Waiting for work queue to empty: {0} '
                                'items remain'.format(work_queue.qsize())))
            time.sleep(5)
        work_stop_event.set()
        # let the workers finish
        for worker in work_threads:
            worker.join()
        result_stop_event.set()
        while result_processor.is_alive():
            result_processor.join(5)  # wait for result processor to complete
        if collisions:
            group = 0
            print 'Hash Collisions:'
            for md5, info in collisions.iteritems():
                group += 1
                print '  MD5: {0}'.format(md5)
                for item in info:
                    print '    {src}, {size}'.format(src=repr(item[0]),
                                                     size=item[1])
                    if result_fh:
                        result_fh.write('{group}, {md5}, {src}, {size}, '
                                        '{mtime}\n'.format(md5=md5,
                                                           src=repr(item[0]),
                                                           size=item[1],
                                                           mtime=item[2],
                                                           group=group))
        else:
            print 'No Duplicates Found'
        return (collisions, manifest)
    finally:
        if result_fh:
            result_fh.close()


def info_parser(data):
    """Yields (MD5, path, mtime_string, size) tuples from a md5_data
    dictionary"""
    if data:
        for md5, info in data.iteritems():
            for item in info:
                try:
                    time_stamp = datetime.datetime.fromtimestamp(item[2])
                    year_month = '{0}_{1:0>2}'.format(time_stamp.year,
                                                      time_stamp.month)
                except Exception as e:
                    print 'ERROR: {src} {e}'.format(src=repr(item[0]), e=e)
                    year_month = 'Unknown'
                yield md5, item[0], year_month, item[1]


# copy core

def queue_copy_work(copy_queue, data, progress_queue, copied, ignore=None,
                    ignore_empty_files=False):
    for md5, path, mtime, size in info_parser(data):
        if md5 not in copied:
            action_required = True
            if ignore:
                for ignored_pattern in ignore:
                    if fnmatch.fnmatch(path, ignored_pattern):
                        action_required = False
                        break
            if action_required:
                if not ignore_empty_files:
                    copied[md5] = None
                elif md5 != 'd41d8cd98f00b204e9800998ecf8427e':
                    copied[md5] = None
                _throttle_puts(copy_queue.qsize())
                copy_queue.put((path, mtime, size))
            else:
                progress_queue.put((LOW_PRIORITY, 'not_copied', path))
        else:
            progress_queue.put((LOW_PRIORITY, 'not_copied', path))
    return copied


def copy_data(dupes, all_data, target_base, read_paths, copy_threads=8,
              extensions=None, path_rules=None, ignore=None,
              progress_queue=None, no_copy=None, ignore_empty_files=False):
    """Queues up the copy work, waits for threads to finish"""
    stop_event = threading.Event()
    copy_queue = Queue.Queue()
    workers = []
    copied = no_copy
    progress_queue.put((HIGH_PRIORITY, 'message',
                        'Starting {0} copy workers'.format(copy_threads)))
    for _ in range(copy_threads):
        c = CopyThread(copy_queue, target_base, read_paths, stop_event,
                       extensions, path_rules=path_rules,
                       progress_queue=progress_queue)
        workers.append(c)
        c.start()
    progress_queue.put((HIGH_PRIORITY, 'message',
                        'Copying to {0}'.format(target_base)))
    # copied is passed to here so we don't try to copy "comparison" manifests
    # copied is a dict-like, so it's update in place
    queue_copy_work(copy_queue, dupes, progress_queue,
                    copied, ignore=ignore,
                    ignore_empty_files=ignore_empty_files)
    queue_copy_work(copy_queue, all_data, progress_queue,
                    copied, ignore=ignore,
                    ignore_empty_files=ignore_empty_files)
    stop_event.set()
    for c in workers:
        c.join()
    progress_queue.put((HIGH_PRIORITY, 'message',
                        'Processed {0} unique items'.format(len(copied))))


def _clean_extensions(extensions):
    clean = []
    if extensions is not None:
        for ext in extensions:
            ext = ext.strip().lower()
            if ext.startswith('.') and len(ext) > 1:
                ext = ext[1:]
            clean.append('*.{0}'.format(ext))
    return clean


def _build_path_rules(rule_pairs):
    """Create the rule applying function for path rule pairs"""
    rules = defaultdict(list)
    for rule in rule_pairs:
        extension, rule = rule.split(':')
        extension = _clean_extensions([extension])[0]
        if rule not in PATH_RULES:
            raise ValueError("Unexpected path rule: {0}".format(rule))
        rules[extension].append(rule)
    return functools.partial(_path_rules_parser, rules)


class Manifest(object):

    """Storage of manifest data. Presents the hash dict but tracks the
    read files in a separate structure"""

    cache_size = 10000

    def __init__(self, manifest_paths, save_path=None, temp_directory=None,
                 save_event=None):
        self.temp_directory = temp_directory
        self.path = save_path or os.path.join(temp_directory,
                                              'temporary_{0}.dict'.format(
                                                  random.getrandbits(16)))
        self.md5_data = {}
        self.read_sources = {}
        self.save_event = save_event
        if manifest_paths:
            if not isinstance(manifest_paths, list):
                self.load(manifest_paths)
            else:
                self._load_manifest_list(manifest_paths)
        else:
            sources_path = '{0}.read'.format(self.path)
            # no data yet
            if os.path.exists(self.path):
                print 'Removing old manifest file at: {}'.format(
                    repr(self.path))
                os.unlink(self.path)
            if os.path.exists(sources_path):
                print 'Removing old manifest sources file at: {}'.format(
                    repr(sources_path))
                os.unlink(sources_path)
            print 'creating manifests {0} / {1}'.format(self.path,
                                                        sources_path)
            self.md5_data = DefaultCacheDict(list, db_file=self.path,
                                             max_size=self.cache_size)
            self.read_sources = CacheDict(db_file=sources_path,
                                          max_size=self.cache_size)

    def __contains__(self, key):
        return key in self.md5_data

    def __getitem__(self, key):
        return self.md5_data[key]

    def __setitem__(self, key, value):
        self.md5_data[key] = value

    def __delitem__(self, key):
        del self.md5_data[key]

    def __len__(self):
        return len(self.md5_data)

    def save(self, path=None, keys=None):
        if self.save_event:
            self.save_event.set()
        path = path or self.path
        try:
            self._write_manifest(path=path, keys=keys)
            self.md5_data.save(db_file=path)
            self.read_sources.save(db_file='{0}.read'.format(path))
        finally:
            if self.save_event:
                self.save_event.clear()

    def load(self, path=None):
        path = path or self.path
        self.md5_data, self.read_sources = self._load_manifest(path=path)

    def iteritems(self):
        return self.md5_data.iteritems()

    def _write_manifest(self, path=None, keys=None):
        path = path or self.path
        print 'Writing manifest of {0} hashes to {1}'.format(
            len(self.md5_data), path)
        print 'Writing sources of {0} files to {1}'.format(
            len(self.read_sources), '{0}.read'.format(path))
        if not keys:
            dict_iter = self.md5_data.iteritems()
        else:
            dict_iter = ((k, self.md5_data[k]) for k in keys)
        for _, info in dict_iter:
            for file_data in info:
                src = file_data[0]
                if src not in self.read_sources:
                    self.read_sources[src] = None

    def hash_set(self):
        return set(self.md5_data.keys())

    def _load_manifest(self, path=None):
        path = path or self.path
        print 'Reading manifest from {0}...'.format(repr(path))
        # Would be nice to just get the fd, but backends require a path
        md5_data = DefaultCacheDict(list, db_file=path,
                                    max_size=self.cache_size)
        print '... read {0} hashes'.format(len(md5_data))
        read_sources = CacheDict(db_file='{0}.read'.format(path),
                                 max_size=self.cache_size)
        print '... in {0} files'.format(len(read_sources))
        return md5_data, read_sources

    def _combine_manifests(self, manifests):
        base, read = manifests[0]
        for m, r in manifests[1:]:
            for key, files in m.iteritems():
                for info in files:
                    if info not in base[key]:
                        base[key].append(info)
            for key in r:
                read[key] = None
        return base, read

    def _load_manifest_list(self, manifests):
        assert isinstance(manifests, list)
        read_manifest_data, read_sources = self._load_manifest(manifests[0])
        loaded = [(read_manifest_data, read_sources)]
        for src in manifests[1:]:
            loaded.append(self._load_manifest(src))
        self.md5_data, self.read_sources = self._combine_manifests(loaded)

    def convert_manifest_paths(self, paths_from, paths_to,
                               temp_directory=None):
        """Replaces all prefixes for all paths in the manifest with a new prefix
        """
        temp_directory = temp_directory or self.temp_directory
        for key, val in self.md5_data.iteritems():
            new_values = list()
            for file_data in val:
                new_values.append(
                    [file_data[0].replace(paths_from, paths_to, 1)] + file_data[1:])
            self.md5_data[key] = new_values
        # build a new set of values and move into place
        # XXX replace w/ persistent set?
        db_file = self.read_sources.db_file_path()
        new_sources = CacheDict(db_file=os.path.join(temp_directory,
                                                     'temp_convert.dict'),
                                max_size=self.cache_size)
        for key in self.read_sources:
            new_sources[key.replace(paths_from, paths_to, 1)] = None
        del self.read_sources
        new_sources.save(db_file=db_file)
        self.read_sources = new_sources
        self.md5_data.save()
        self.read_sources.save()


def run_dupe_copy(read_from_path=None, extensions=None,
                  manifests_in_paths=None, manifest_out_path=None,
                  path_rules=None, copy_to_path=None,
                  ignore_old_collisions=False, ignored_patterns=None,
                  csv_report_path=None, walk_threads=4,
                  read_threads=8, copy_threads=8, convert_manifest_paths_to='',
                  convert_manifest_paths_from='', no_walk=False, no_copy=None,
                  keep_empty=False, compare_manifests=None):
    """For external callers this is the entry point for dedupe + copy"""
    temp_directory = tempfile.mkdtemp(suffix='dedupe_copy')

    save_event = threading.Event()
    manifest = Manifest(manifests_in_paths, save_path=manifest_out_path,
                        temp_directory=temp_directory, save_event=save_event)
    compare = Manifest(compare_manifests, save_path=None,
                       temp_directory=temp_directory)

    if no_copy:
        for item in no_copy:
            compare[item] = None

    if no_walk and not manifest:
        raise ValueError("If --no-walk is specified, a manifest must be "
                         "supplied.")
    if read_from_path and not isinstance(read_from_path, list):
        read_from_path = [read_from_path]
    if path_rules:
        path_rules = _build_path_rules(path_rules)
    all_stop = threading.Event()
    work_queue = Queue.Queue()
    result_queue = Queue.Queue()
    progress_queue = Queue.PriorityQueue()
    walk_queue = Queue.Queue()
    progress_thread = ProgressThread(work_queue, result_queue,
                                     progress_queue, walk_queue, all_stop,
                                     save_event)
    progress_thread.start()
    collisions = None
    if (manifest and
            (convert_manifest_paths_to or convert_manifest_paths_from)):
        manifest.convert_manifest_paths(convert_manifest_paths_from,
                                        convert_manifest_paths_to)

    # storage for hash collisions
    collisions_file = os.path.join(temp_directory, 'collisions.db')
    collisions = DefaultCacheDict(list, db_file=collisions_file,
                                  max_size=10000)
    if manifest and not ignore_old_collisions:
        # rebuild collision list
        for md5, info in manifest.iteritems():
            if len(info) > 1:
                collisions[md5] = info
    if no_walk:
        progress_queue.put((HIGH_PRIORITY, 'message',
                            'Not walking file system. Using stored manifests'))
        all_data = manifest
        dupes = collisions
    else:
        progress_queue.put((HIGH_PRIORITY, 'message',
                            'Running the duplicate search, generating reports'))
        dupes, all_data = find_duplicates(read_from_path, work_queue,
                                          result_queue, manifest, collisions,
                                          result_src=csv_report_path,
                                          extensions=extensions,
                                          ignore=ignored_patterns,
                                          progress_queue=progress_queue,
                                          walk_threads=walk_threads,
                                          read_threads=read_threads,
                                          keep_empty=keep_empty,
                                          save_event=save_event,
                                          walk_queue=walk_queue)
    total_size = _extension_report(all_data)
    print 'Total Size of accepted: {0} bytes'.format(total_size)
    if manifest_out_path:
        progress_queue.put((HIGH_PRIORITY, 'message',
                            "Saving complete manifest from search"))
        all_data.save(path=manifest_out_path)
    if copy_to_path is not None:
        # Warning: strip dupes out of all data, this assumes dupes correctly
        # follows handling of keep_empty (not a dupe even if md5 is same for
        # zero byte files)
        for md5 in dupes:
            if md5 in all_data:
                del all_data[md5]
        # copy the duplicate files first and then ignore them for the full pass
        progress_queue.put((HIGH_PRIORITY, 'message',
                            'Running copy to {0}'.format(repr(copy_to_path))))
        copy_data(dupes, all_data, copy_to_path, read_from_path,
                  copy_threads=copy_threads, extensions=extensions,
                  path_rules=path_rules, ignore=ignored_patterns,
                  progress_queue=progress_queue, no_copy=compare,
                  ignore_empty_files=keep_empty)
    all_stop.set()
    while progress_thread.is_alive():
        progress_thread.join(5)
    del collisions
    try:
        time.sleep(1)
        shutil.rmtree(temp_directory)
    except Exception as err:
        print 'Failed to cleanup the collisions file: {0} with err: {1}'.format(
            collisions_file, err)
