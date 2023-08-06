# -*- coding: utf-8 -*-
"""
A helper module for testing, introducing some helper functions. Inspired by
the jedi helper module for their testing package
"""
import os
import functools
import platform
from os.path import abspath
from os.path import dirname
from pyqode.core.api import CodeEdit
from pyqode.core import modes
from pyqode.core import panels
from pyqode.core.qt.QtTest import QTest


test_dir = dirname(abspath(__file__))


# -------------------
# Decorators
# -------------------
def cwd_at(path):
    """
    Decorator to run function at `path`.

    :type path: str
    :arg path: relative path from repository root (e.g., 'pyqode' or 'test').
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            try:
                oldcwd = os.getcwd()
                repo_root = os.path.dirname(test_dir)
                os.chdir(os.path.join(repo_root, path))
                return func(*args, **kwds)
            finally:
                os.chdir(oldcwd)
        return wrapper
    return decorator


def editor_open(path):
    if not os.path.exists(path):
        try:
            with open(path, 'w') as dst:
                with open(__file__, 'r') as src:
                    dst.write(src.read())
        except OSError:
            pass

    def decorator(func):
        @functools.wraps(func)
        def wrapper(editor, *args, **kwds):
            editor.file.open(path)
            return func(editor, *args, **kwds)
        return wrapper
    return decorator


def preserve_settings(func):
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        editor.save_on_focus_out = False
        editor.modes.get(modes.FileWatcherMode).auto_reload = False
        try:
            ret = func(editor, *args, **kwds)
        finally:
            assert isinstance(editor, CodeEdit)
            editor.save_on_focus_out = False
            editor.modes.get(modes.FileWatcherMode).auto_reload = False
        return ret
    return wrapper


def preserve_style(func):
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        try:
            ret = func(editor, *args, **kwds)
        finally:
            editor.font_name = ''
            editor.font_size = 10
        return ret
    return wrapper


def preserve_editor_config(func):
    @functools.wraps(func)
    def wrapper(editor, *args, **kwds):
        ret = None
        try:
            ret = func(editor, *args, **kwds)
        finally:
            editor.modes.clear()
            editor.panels.clear()
            setup_editor(editor)
            if not editor.backend.connected:
                editor.backend.start(editor, server_path())
                wait_for_connected(editor)
        return ret
        # return func(editor, *args, **kwds)
    return wrapper


def preserve_visiblity(func):
    # todo: decorator to preserve editor visibility
    pass


def require_python2():
    """
    Skips the test if there is no python2 interpreter.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            if os.path.exists(python2_path()):
                return func(*args, **kwds)
        return wrapper
    return decorator


def log_test_name(func):
    @functools.wraps(func)
    def wrapper(*args, **kwds):
        import logging
        logging.info('---------------- %s ----------------' % func.__name__)
        return func(*args, **kwds)
    return wrapper



# -------------------
# Helper functions
# -------------------
def wait_for_connected(editor):
    while not editor.backend.connected:
        QTest.qWait(100)


def python2_path():
    """
    Returns the path to the python2 interpreter.

    The expected python2 path is '/usr/bin/python' on Linux and
    'c:\Python27\python.exe' on Windows.
    """
    return '/usr/bin/python' if platform.system() == 'Linux' else \
        'c:\\Python27\\python.exe'


def server_path():
    return os.path.join(os.path.dirname(__file__), 'server.py')


def setup_editor(code_edit):
        # append panels
    p = panels.LineNumberPanel()
    code_edit.panels.append(p)
    p.show()
    p = panels.MarkerPanel()
    code_edit.panels.append(p)
    p.show()
    p = panels.SearchAndReplacePanel()
    code_edit.panels.append(p, p.Position.BOTTOM)
    p.show()

    # append modes
    code_edit.modes.append(modes.AutoCompleteMode())
    code_edit.modes.append(modes.CaseConverterMode())
    code_edit.modes.append(modes.FileWatcherMode())
    code_edit.modes.append(modes.CaretLineHighlighterMode())
    code_edit.modes.append(modes.RightMarginMode())
    code_edit.modes.append(modes.PygmentsSyntaxHighlighter(
        code_edit.document()))
    code_edit.modes.append(modes.ZoomMode())
    code_edit.modes.append(modes.CodeCompletionMode())
    code_edit.modes.append(modes.AutoIndentMode())
    code_edit.modes.append(modes.IndenterMode())
    code_edit.modes.append(modes.SymbolMatcherMode())
    code_edit.modes.append(modes.WordClickMode())
    code_edit.modes.get(modes.FileWatcherMode).auto_reload = True
