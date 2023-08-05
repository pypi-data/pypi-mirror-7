#!/usr/bin/env python
import argparse

from dedupe_copy import _clean_extensions, run_dupe_copy, PATH_RULES


DESCRIPTION = 'Find duplicates / copy and restructure file layout tool'
EPILOGUE = '''
Examples:

  Generate a duplicate file report for a path:
      dedupecopy.py -p /Users/ -r dupes.csv -m manifest

  Copy all *.jpg files from multiple paths to a /YYYY_MM/*.jpg structure
      dedupecopy.py -p C:\pics -p D:\pics -e jpg -R jpg:mtime -c X:\pics

  Copy all files from two drives to a single target, preserving the path for
  all extensions:
      dedupecopy.py -p C:\ -p D:\ -c X:\ -m X:\manifest -R *:no_change

  Resume an interrupted run (assuming "-m manifest" used in prior run):
    dedupecopy.py -p /Users/ -r dupes_2.csv -i manifest -m manifest

  Sequentially copy different sources into the same target, not copying
  duplicate files (2 sources and 1 target):
    1.) First record manifests for all devices
        dedupecopy.py -p \\target\share -m target_manifest
        dedupecopy.py -p \\source1\share -m source1_manifest
        dedupecopy.py -p \\source2\share -m source2_manifest

    2.) Copy each source to the target (specifying --compare so manifests from
        other sources are loaded but not used as part of the set to copy and
        --no-walk to skip re-scan of the source):
        dedupecopy.py -p \\source1\share -c \\target\share -i source1_manifest
            --compare source2_manifest --compare target_manifest  --no-walk
        dedupecopy.py -p \\source2\share -c \\target\share -i source2_manifest
            --compare source1_manifest --compare target_manifest --no-walk
'''


def _create_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     epilog=EPILOGUE,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    walk_group = parser.add_mutually_exclusive_group(required=True)
    walk_group.add_argument('-p', '--read-path',
                            help='Path (s) to start walk for dupes',
                            required=False, action='append')
    walk_group.add_argument('--no-walk',
                            help='Use paths from a loaded manifest, '
                            'do not re-scan the file system',
                            required=False, default=False,
                            action='store_true')

    parser.add_argument('-r', '--result-path',
                        help='Path for result output', required=False,
                        default=None)

    parser.add_argument('-c', '--copy-path',
                        help='Path to copy to', required=False, default=None)
    parser.add_argument('--compare',
                        help='Path to existing manifest, used to prevent '
                        'duplicates from being copied to a target, but these '
                        'items are not themselves copied',
                        required=False, default=None, dest='compare',
                        action='append')
    parser.add_argument('-m', '--manifest-dump-path',
                        help='Where to write the manifest dump', required=False,
                        default=None, dest='manifest_out')
    parser.add_argument('-i', '--manifest-read-path',
                        help='Where to read an existing the manifest dump',
                        required=False,
                        default=None, dest='manifest_in', action='append')
    parser.add_argument('-e', '--extensions',
                        help='extension (s) to record/copy (may include ?/*)',
                        required=False,
                        default=None, action='append')
    parser.add_argument('--ignore',
                        help='file patterns (s) to ignore during record/copy '
                        '(may include ?/*). For example: using fred*.jpg '
                        'excludes fred_1.jpg from from being copied and/or '
                        'reported as a dupe',
                        required=False, default=None, action='append')
    parser.add_argument('-R', '--path-rules',
                        help='extension:rule_name pair(s) For example: '
                        'png:mtime. These rules are cumulative, so '
                        '-R png:extension -R png:mtime results in a structure '
                        'like  /copy_path/png/2012_08/file.png Rules available: '
                        '{rules}'.format(rules=PATH_RULES),
                        required=False, default=None, action='append')
    parser.add_argument('--ignore-old-collisions',
                        help='Only find collisions with un-scanned files',
                        required=False,
                        default=False, action='store_true')
    parser.add_argument('--keep-empty',
                        help='Do not count empty files as duplicates',
                        required=False,
                        default=False, action='store_true')

    performance = parser.add_argument_group('Performance Related')
    performance.add_argument('--walk-threads',
                             help='Number of threads to use in the file '
                             'system walk',
                             required=False, default=4, type=int)
    performance.add_argument('--read-threads',
                             help='Number of threads to read with',
                             required=False, default=8, type=int)
    performance.add_argument('--copy-threads',
                             help='Number of threads to use for copying files',
                             required=False, default=8, type=int)

    group = parser.add_argument_group('Path conversion')
    group.add_argument('--convert-manifest-paths-from',
                       help='Prefix of paths stored in the input manifest to '
                       'replace', required=False, default='')
    group.add_argument('--convert-manifest-paths-to',
                       help='Replacement prefix (replaces the prefix found in '
                       '--convert-manifest-paths-from)', required=False,
                       default='')
    return parser


def _handle_arguments(args):
    """Take the cli args and process them in prep for calling run_dedupe_copy
    """
    if args.read_path:
        print 'Reading from {0}'.format(args.read_path)
    # strip, lower, remove leading dot from extensions for both path rules and
    # specific extension includes
    extensions = _clean_extensions(args.extensions)
    read_paths = None
    if args.read_path:
        read_paths = [p.decode('utf-8') for p in args.read_path]
    if args.copy_path:
        copy_path = args.copy_path.decode('utf-8')
    else:
        copy_path = None
    return dict(read_from_path=read_paths, extensions=extensions,
                manifests_in_paths=args.manifest_in,
                manifest_out_path=args.manifest_out, path_rules=args.path_rules,
                copy_to_path=copy_path,
                ignore_old_collisions=args.ignore_old_collisions,
                ignored_patterns=args.ignore, csv_report_path=args.result_path,
                walk_threads=args.walk_threads, read_threads=args.read_threads,
                copy_threads=args.copy_threads,
                convert_manifest_paths_to=args.convert_manifest_paths_to,
                convert_manifest_paths_from=args.convert_manifest_paths_from,
                no_walk=args.no_walk, no_copy=None, keep_empty=args.keep_empty,
                compare_manifests=args.compare)


def run_cli():
    parser = _create_parser()
    args = parser.parse_args()
    print 'Running with arguments: {0}'.format(args)
    processed_args = _handle_arguments(args)
    return run_dupe_copy(**processed_args)


if __name__ == '__main__':
    run_cli()
