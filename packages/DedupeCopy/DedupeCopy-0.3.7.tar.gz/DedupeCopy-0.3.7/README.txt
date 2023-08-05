Find duplicates / copy and restructure file layout command-line tool.

This is a simple multi-threaded file copy tool designed for consolidating and
restructuring sprawling file systems.

The most common use case is for backing up data into a new layout, ignoring
duplicated files.

Other uses include:
  1. Getting a .csv file describing all duplicated files
  2. Comparing different file systems
  3. Restructuring existing sets of files into different layouts (such as
    sorted by extension or last modification time)

This tool is *NOT* a Robocopy or rsync replacement and does not try to fill
the role those play.

As with all code that walks a file tree, please use with caution and expect
absolutely no warranty! :)


Command examples:

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


Complete example:
    
    Assuming you start with a set of files laid out as follows:

    C:\
        pics
            some_photos
                photo1.jpg
                photo2.jpg
            photo3.jpg
    D:\
        pics
            copied_photo
                photo3.jpg
            photo4.jpg

    And you run the command:
    > dedupecopy.py -p C:\pics -p D:\pics -e jpg -R jpg:mtime -c X:\photos

    You would end up with the following (photo3.jpg was a true duplicate):

    X:\
        photos
            2012_08
                photo1.jpg
                photo2.jpg
                photo3.jpg
            2012_09
                photo4.jpg


This project is on bitbucket: http://www.bitbucket.org/othererik/dedupe_copy
This project is on pypi: http://pypi.python.org/pypi/DedupeCopy
