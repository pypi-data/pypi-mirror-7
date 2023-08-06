# Copyright 2013 Hynek Schlawack
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

import sys

from structlog._loggers import (
    PrintLogger,
    PrintLoggerFactory,
    ReturnLogger,
    ReturnLoggerFactory,
)


def test_return_logger():
    obj = ['hello']
    assert obj is ReturnLogger().msg(obj)


class TestPrintLogger(object):
    def test_prints_to_stdout_by_default(self, capsys):
        PrintLogger().msg('hello')
        out, err = capsys.readouterr()
        assert 'hello\n' == out
        assert '' == err

    def test_prints_to_correct_file(self, tmpdir, capsys):
        f = tmpdir.join('test.log')
        fo = f.open('w')
        PrintLogger(fo).msg('hello')
        out, err = capsys.readouterr()
        assert '' == out == err
        fo.close()
        assert 'hello\n' == f.read()

    def test_repr(self):
        assert repr(PrintLogger()).startswith(
            "<PrintLogger(file="
        )


class TestPrintLoggerFactory(object):
    def test_does_not_cache(self):
        """
        Due to doctest weirdness, we must not re-use PrintLoggers.
        """
        f = PrintLoggerFactory()
        assert f() is not f()

    def test_passes_file(self):
        """
        If a file is passed to the factory, it get passed on to the logger.
        """
        l = PrintLoggerFactory(sys.stderr)()
        assert sys.stderr is l._file

    def test_ignores_args(self):
        """
        PrintLogger doesn't take positional arguments.  If any are passed to
        the factory, they are not passed to the logger.
        """
        PrintLoggerFactory()(1, 2, 3)


class TestReturnLoggerFactory(object):
    def test_builds_returnloggers(self):
        f = ReturnLoggerFactory()
        assert isinstance(f(), ReturnLogger)

    def test_caches(self):
        """
        There's no need to have several loggers so we return the same one on
        each call.
        """
        f = ReturnLoggerFactory()
        assert f() is f()

    def test_ignores_args(self):
        """
        ReturnLogger doesn't take positional arguments.  If any are passed to
        the factory, they are not passed to the logger.
        """
        ReturnLoggerFactory()(1, 2, 3)
