""" Test tools module """
from __future__ import division, print_function

import os
from os.path import join as pjoin, split as psplit, abspath, dirname
import shutil

from ..tools import (back_tick, ensure_writable, zip2dir, dir2zip,
                     find_package_dirs)

from ..tmpdirs import InTemporaryDirectory

from nose.tools import assert_true, assert_false, assert_equal, assert_raises


def test_back_tick():
    cmd = 'python -c "print(\'Hello\')"'
    assert_equal(back_tick(cmd), "Hello")
    assert_equal(back_tick(cmd, ret_err=True), ("Hello", ""))
    assert_equal(back_tick(cmd, True, False), (b"Hello", b""))
    cmd = 'python -c "raise ValueError()"'
    assert_raises(RuntimeError, back_tick, cmd)


def test_ensure_writable():
    # Test ensure writable decorator
    with InTemporaryDirectory():
        with open('test.bin', 'wt') as fobj:
            fobj.write('A line\n')
        # Set to user rw, else r
        os.chmod('test.bin', 0o644)
        st = os.stat('test.bin')
        @ensure_writable
        def foo(fname):
            pass
        foo('test.bin')
        assert_equal(os.stat('test.bin'), st)
        # No-one can write
        os.chmod('test.bin', 0o444)
        st = os.stat('test.bin')
        foo('test.bin')
        assert_equal(os.stat('test.bin'), st)


def _write_file(filename, contents):
    with open(filename, 'wt') as fobj:
        fobj.write(contents)


def test_zip2():
    # Test utilities to unzip and zip up
    with InTemporaryDirectory():
        os.mkdir('a_dir')
        os.mkdir('zips')
        _write_file(pjoin('a_dir', 'file1.txt'), 'File one')
        s_dir = pjoin('a_dir', 's_dir')
        os.mkdir(s_dir)
        _write_file(pjoin(s_dir, 'file2.txt'), 'File two')
        zip_fname = pjoin('zips', 'my.zip')
        dir2zip('a_dir', zip_fname)
        zip2dir(zip_fname, 'another_dir')
        assert_equal(os.listdir('another_dir'), ['file1.txt', 's_dir'])
        assert_equal(os.listdir(pjoin('another_dir', 's_dir')), ['file2.txt'])
        # Try zipping from a subdirectory, with a different extension
        dir2zip(s_dir, 'another.ext')
        # Remove original tree just to be sure
        shutil.rmtree('a_dir')
        zip2dir('another.ext', 'third_dir')
        assert_equal(os.listdir('third_dir'), ['file2.txt'])


def test_find_package_dirs():
    # Test utility for finding package directories
    with InTemporaryDirectory():
        os.mkdir('to_test')
        a_dir = pjoin('to_test', 'a_dir')
        b_dir = pjoin('to_test', 'b_dir')
        c_dir = pjoin('to_test', 'c_dir')
        for dir in (a_dir, b_dir, c_dir):
            os.mkdir(dir)
        assert_equal(find_package_dirs('to_test'), set([]))
        _write_file(pjoin(a_dir, '__init__.py'), "# a package")
        assert_equal(find_package_dirs('to_test'), set([a_dir]))
        _write_file(pjoin(c_dir, '__init__.py'), "# another package")
        assert_equal(find_package_dirs('to_test'), set([a_dir, c_dir]))
        # Not recursive
        assert_equal(find_package_dirs('.'), set())
        _write_file(pjoin('to_test', '__init__.py'), "# base package")
        # Also - strips '.' for current directory
        assert_equal(find_package_dirs('.'), set(['to_test']))
