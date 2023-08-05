# Copyright (c) 2003-2013 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
"""functional/non regression tests for pylint"""
from __future__ import with_statement

import collections
import contextlib
import functools
import sys
import re

from glob import glob
from os import linesep
from os.path import abspath, basename, dirname, isdir, join, splitext
from cStringIO import StringIO

from logilab.common import testlib

from pylint import checkers
from pylint.utils import PyLintASTWalker
from pylint.reporters import BaseReporter
from pylint.interfaces import IReporter
from pylint.lint import PyLinter


# Utils

SYS_VERS_STR = '%d%d%d' % sys.version_info[:3]
TITLE_UNDERLINES = ['', '=', '-', '.']
PREFIX = abspath(dirname(__file__))
PY3K = sys.version_info[0] == 3

def fix_path():
    sys.path.insert(0, PREFIX)

def get_tests_info(input_dir, msg_dir, prefix, suffix):
    """get python input examples and output messages

    We use following conventions for input files and messages:
    for different inputs:
        test for python  >= x.y    ->  input   =  <name>_pyxy.py
        test for python  <  x.y    ->  input   =  <name>_py_xy.py
    for one input and different messages:
        message for python >=  x.y ->  message =  <name>_pyxy.txt
        lower versions             ->  message with highest num
    """
    result = []
    for fname in glob(join(input_dir, prefix + '*' + suffix)):
        infile = basename(fname)
        fbase = splitext(infile)[0]
        # filter input files :
        pyrestr = fbase.rsplit('_py', 1)[-1] # like _26 or 26
        if pyrestr.isdigit(): # '24', '25'...
            if SYS_VERS_STR < pyrestr:
                continue
        if pyrestr.startswith('_') and  pyrestr[1:].isdigit():
            # skip test for higher python versions
            if SYS_VERS_STR >= pyrestr[1:]:
                continue
        messages = glob(join(msg_dir, fbase + '*.txt'))
        # the last one will be without ext, i.e. for all or upper versions:
        if messages:
            for outfile in sorted(messages, reverse=True):
                py_rest = outfile.rsplit('_py', 1)[-1][:-4]
                if py_rest.isdigit() and SYS_VERS_STR >= py_rest:
                    break
        else:
            # This will provide an error message indicating the missing filename.
            outfile = join(msg_dir, fbase + '.txt')
        result.append((infile, outfile))
    return result


class TestReporter(BaseReporter):
    """reporter storing plain text messages"""

    __implements____ = IReporter

    def __init__(self):
        self.message_ids = {}
        self.reset()

    def reset(self):
        self.out = StringIO()
        self.messages = []

    def add_message(self, msg_id, location, msg):
        """manage message of different type and in the context of path """
        fpath, module, obj, line, _ = location
        self.message_ids[msg_id] = 1
        if obj:
            obj = ':%s' % obj
        sigle = msg_id[0]
        if PY3K and linesep != '\n':
            # 2to3 writes os.linesep instead of using
            # the previosly used line separators
            msg = msg.replace('\r\n', '\n')
        self.messages.append('%s:%3s%s: %s' % (sigle, line, obj, msg))

    def finalize(self):
        self.messages.sort()
        for msg in self.messages:
            print >> self.out, msg
        result = self.out.getvalue()
        self.reset()
        return result

    def display_results(self, layout):
        """ignore layouts"""


class Message(collections.namedtuple('Message',
                                     ['msg_id', 'line', 'node', 'args'])):
    def __new__(cls, msg_id, line=None, node=None, args=None):
        return tuple.__new__(cls, (msg_id, line, node, args))


class UnittestLinter(object):
    """A fake linter class to capture checker messages."""

    def __init__(self):
        self._messages = []
        self.stats = {}

    def release_messages(self):
        try:
            return self._messages
        finally:
            self._messages = []

    def add_message(self, msg_id, line=None, node=None, args=None):
        self._messages.append(Message(msg_id, line, node, args))

    def is_message_enabled(self, *unused_args):
        return True

    def add_stats(self, **kwargs):
        for name, value in kwargs.iteritems():
            self.stats[name] = value
        return self.stats


def set_config(**kwargs):
    """Decorator for setting config values on a checker."""
    def _Wrapper(fun):
        @functools.wraps(fun)
        def _Forward(self):
            for key, value in kwargs.iteritems():
                setattr(self.checker.config, key, value)
            if isinstance(self, CheckerTestCase):
                # reopen checker in case, it may be interested in configuration change
                self.checker.open()
            fun(self)

        return _Forward
    return _Wrapper


class CheckerTestCase(testlib.TestCase):
    """A base testcase class for unittesting individual checker classes."""
    CHECKER_CLASS = None
    CONFIG = {}

    def setUp(self):
        self.linter = UnittestLinter()
        self.checker = self.CHECKER_CLASS(self.linter) # pylint: disable=not-callable
        for key, value in self.CONFIG.iteritems():
            setattr(self.checker.config, key, value)
        self.checker.open()

    @contextlib.contextmanager
    def assertNoMessages(self):
        """Assert that no messages are added by the given method."""
        with self.assertAddsMessages():
            yield

    @contextlib.contextmanager
    def assertAddsMessages(self, *messages):
        """Assert that exactly the given method adds the given messages.

        The list of messages must exactly match *all* the messages added by the
        method. Additionally, we check to see whether the args in each message can
        actually be substituted into the message string.
        """
        yield
        got = self.linter.release_messages()
        msg = ('Expected messages did not match actual.\n'
               'Expected:\n%s\nGot:\n%s' % ('\n'.join(repr(m) for m in messages),
                                            '\n'.join(repr(m) for m in got)))
        self.assertEqual(list(messages), got, msg)

    def walk(self, node):
        """recursive walk on the given node"""
        walker = PyLintASTWalker(linter)
        walker.add_checker(self.checker)
        walker.walk(node)


# Init
test_reporter = TestReporter()
linter = PyLinter()
linter.set_reporter(test_reporter)
linter.config.persistent = 0
checkers.initialize(linter)
linter.global_set_option('required-attributes', ('__revision__',))

if linesep != '\n':
    LINE_RGX = re.compile(linesep)
    def ulines(string):
        return LINE_RGX.sub('\n', string)
else:
    def ulines(string):
        return string

INFO_TEST_RGX = re.compile(r'^func_i\d\d\d\d$')

def exception_str(self, ex):
    """function used to replace default __str__ method of exception instances"""
    return 'in %s\n:: %s' % (ex.file, ', '.join(ex.args))

# Test classes

class LintTestUsingModule(testlib.TestCase):
    INPUT_DIR = None
    DEFAULT_PACKAGE = 'input'
    package = DEFAULT_PACKAGE
    linter = linter
    module = None
    depends = None
    output = None
    _TEST_TYPE = 'module'

    def shortDescription(self):
        values = {'mode' : self._TEST_TYPE,
                  'input': self.module,
                  'pkg':   self.package,
                  'cls':   self.__class__.__name__}

        if self.package == self.DEFAULT_PACKAGE:
            msg = '%(mode)s test of input file "%(input)s" (%(cls)s)'
        else:
            msg = '%(mode)s test of input file "%(input)s" in "%(pkg)s" (%(cls)s)'
        return msg % values

    def test_functionality(self):
        tocheck = [self.package+'.'+self.module]
        if self.depends:
            tocheck += [self.package+'.%s' % name.replace('.py', '')
                        for name, file in self.depends]
        self._test(tocheck)

    def _check_result(self, got):
        self.assertMultiLineEqual(self._get_expected().strip()+'\n',
                                  got.strip()+'\n')

    def _test(self, tocheck):
        if INFO_TEST_RGX.match(self.module):
            self.linter.enable('I')
        else:
            self.linter.disable('I')
        try:
            self.linter.check(tocheck)
        except Exception, ex:
            # need finalization to restore a correct state
            self.linter.reporter.finalize()
            ex.file = tocheck
            print ex
            ex.__str__ = exception_str
            raise
        self._check_result(self.linter.reporter.finalize())

    def _has_output(self):
        return not self.module.startswith('func_noerror_')

    def _get_expected(self):
        if self._has_output() and self.output:
            with open(self.output, 'U') as fobj:
                return fobj.read().strip() + '\n'
        else:
            return ''

class LintTestUsingFile(LintTestUsingModule):

    _TEST_TYPE = 'file'

    def test_functionality(self):
        importable = join(self.INPUT_DIR, self.module)
        # python also prefers packages over simple modules.
        if not isdir(importable):
            importable += '.py'
        tocheck = [importable]
        if self.depends:
            tocheck += [join(self.INPUT_DIR, name) for name, _file in self.depends]
        self._test(tocheck)

class LintTestUpdate(LintTestUsingModule):

    _TEST_TYPE = 'update'

    def _check_result(self, got):
        if self._has_output():
            try:
                expected = self._get_expected()
            except IOError:
                expected = ''
            if got != expected:
                with open(self.output, 'w') as fobj:
                    fobj.write(got)

# Callback

def cb_test_gen(base_class):
    def call(input_dir, msg_dir, module_file, messages_file, dependencies):
        class LintTC(base_class):
            module = module_file.replace('.py', '')
            output = messages_file
            depends = dependencies or None
            tags = testlib.Tags(('generated', 'pylint_input_%s' % module))
            INPUT_DIR = input_dir
            MSG_DIR = msg_dir
        return LintTC
    return call

# Main function

def make_tests(input_dir, msg_dir, filter_rgx, callbacks):
    """generate tests classes from test info

    return the list of generated test classes
    """
    if filter_rgx:
        is_to_run = re.compile(filter_rgx).search
    else:
        is_to_run = lambda x: 1
    tests = []
    for module_file, messages_file in (
            get_tests_info(input_dir, msg_dir, 'func_', '')
    ):
        if not is_to_run(module_file):
            continue
        base = module_file.replace('func_', '').replace('.py', '')

        dependencies = get_tests_info(input_dir, msg_dir, base, '.py')

        for callback in callbacks:
            test = callback(input_dir, msg_dir, module_file, messages_file,
                dependencies)
            if test:
                tests.append(test)


    return tests
