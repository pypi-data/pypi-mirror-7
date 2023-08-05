#!/usr/bin/env python

# Copyright (C) 2013 Steven Myint
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Formats Python code to follow a consistent style."""

from __future__ import print_function
from __future__ import unicode_literals

import io
import signal
import sys

import autoflake
import autopep8
import docformatter
import unify


__version__ = '0.5.5'


try:
    unicode
except NameError:
    unicode = str


def formatters(aggressive):
    """Return list of code formatters."""
    if aggressive:
        yield autoflake.fix_code
        autopep8_options = autopep8.parse_args(
            [''] + int(aggressive) * ['--aggressive'])
        try:
            # For old autopep8. Remove this once autopep8 1.0 is released.
            autopep8_options = autopep8_options[0]
        except TypeError:  # pragma: no cover
            pass
    else:
        autopep8_options = None

    yield lambda code: autopep8.fix_code(code, options=autopep8_options)
    yield docformatter.format_code
    yield unify.format_code


def format_code(source, aggressive=False):
    """Return formatted source code."""
    formatted_source = source

    for fix in formatters(aggressive):
        formatted_source = fix(formatted_source)

    return formatted_source


def format_file(filename, args, standard_out):
    """Run format_code() on a file."""
    encoding = autopep8.detect_encoding(filename)
    with autopep8.open_with_encoding(filename,
                                     encoding=encoding) as input_file:
        source = input_file.read()

    if not source:
        return

    formatted_source = format_code(source,
                                   aggressive=args.aggressive)

    if source != formatted_source:
        if args.in_place:
            with autopep8.open_with_encoding(filename, mode='w',
                                             encoding=encoding) as output_file:
                output_file.write(formatted_source)
        else:
            diff = autopep8.get_diff_text(
                io.StringIO(source).readlines(),
                io.StringIO(formatted_source).readlines(),
                filename)
            standard_out.write(''.join(diff))


def _format_file(parameters):
    """Helper function for optionally running format_file() in parallel."""
    (filename, args, _, standard_error) = parameters

    standard_error = standard_error or sys.stderr

    if args.verbose:
        print('[file:{0}]'.format(filename),
              file=standard_error)
    try:
        format_file(*parameters[:-1])
    except IOError as exception:
        print(unicode(exception), file=standard_error)


def format_multiple_files(filenames, args, standard_out, standard_error):
    """Format files.

    Optionally format files recursively.

    """
    filenames = autopep8.find_files(list(filenames),
                                    args.recursive,
                                    args.exclude_patterns)
    if args.jobs > 1:
        import multiprocessing
        pool = multiprocessing.Pool(args.jobs)
        pool.map(_format_file,
                 [(name, args,
                   None, None)  # multiprocessing cannot serialize io.
                  for name in filenames])
    else:
        for name in filenames:
            _format_file((name, args, standard_out, standard_error))


def parse_args(argv):
    """Return parsed arguments."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, prog='pyformat')
    parser.add_argument('-i', '--in-place', action='store_true',
                        help='make changes to files instead of printing diffs')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='drill down directories recursively')
    parser.add_argument('-a', '--aggressive', action='count', default=0,
                        help='use more aggressive formatters')
    parser.add_argument('-j', '--jobs', type=int, metavar='n', default=1,
                        help='number of parallel jobs; '
                             'match CPU count if value is less than 1')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print verbose messages')
    parser.add_argument('--exclude', action='append',
                        dest='exclude_patterns', default=[], metavar='pattern',
                        help='exclude files this pattern; '
                             'specify this multiple times for multiple '
                             'patterns')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='+',
                        help='files to format')

    args = parser.parse_args(argv[1:])

    if args.jobs < 1:
        import multiprocessing
        args.jobs = multiprocessing.cpu_count()

    return args


def _main(argv, standard_out, standard_error):
    """Internal main entry point.

    Return exit status. 0 means no error.

    """
    args = parse_args(argv)

    if args.jobs > 1 and not args.in_place:
        print('parallel jobs requires --in-place',
              file=standard_error)
        return 1

    format_multiple_files(set(args.files), args, standard_out, standard_error)


def main():
    """Main entry point."""
    try:
        # Exit on broken pipe.
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except AttributeError:  # pragma: no cover
        # SIGPIPE is not available on Windows.
        pass

    try:
        return _main(sys.argv,
                     standard_out=sys.stdout,
                     standard_error=sys.stderr)
    except KeyboardInterrupt:  # pragma: no cover
        return 2  # pragma: no cover


if __name__ == '__main__':
    sys.exit(main())
