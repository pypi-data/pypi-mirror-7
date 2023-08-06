# -*- coding: utf-8 -*-
"""
This module contains the symbol matcher mode
"""
from pyqode.core.api.decoration import TextDecoration
from pyqode.core.api.mode import Mode
from pyqode.core.api.syntax_highlighter import TextBlockUserData
from pyqode.core.qt import QtGui


class SymbolMatcherMode(Mode):
    """
    Do symbols matches highlighting (parenthesis, braces, ...).

    .. note:: This mode requires the document to be filled with
        :class:`pyqode.core.api.TextBlockUserData`, i.e. a
        :class:`pyqode.core.api.SyntaxHighlighter` must be installed on
        the editor instance.

    """
    @property
    def match_background(self):
        """
        Background color of matching symbols.
        """
        return self._match_background

    @match_background.setter
    def match_background(self, value):
        # pylint: disable=missing-docstring
        self._match_background = value
        self._refresh_decorations()

    @property
    def match_foreground(self):
        """
        Foreground color of matching symbols.
        """
        return self._match_foreground

    @match_foreground.setter
    def match_foreground(self, value):
        # pylint: disable=missing-docstring
        self._match_foreground = value
        self._refresh_decorations()

    @property
    def unmatch_background(self):
        """
        Background color of non-matching symbols.
        """
        return self._unmatch_background

    @unmatch_background.setter
    def unmatch_background(self, value):
        # pylint: disable=missing-docstring
        self._unmatch_background = value
        self._refresh_decorations()

    @property
    def unmatch_foreground(self):
        """
        Foreground color of matching symbols.
        """
        return self._unmatch_foreground

    @unmatch_foreground.setter
    def unmatch_foreground(self, value):
        # pylint: disable=missing-docstring
        self._unmatch_foreground = value
        self._refresh_decorations()

    def __init__(self):
        super().__init__()
        self._decorations = []
        self._match_background = QtGui.QBrush(QtGui.QColor('#B4EEB4'))
        self._match_foreground = QtGui.QColor('red')
        self._unmatch_background = QtGui.QBrush(QtGui.QColor('transparent'))
        self._unmatch_foreground = QtGui.QColor('red')

    def _clear_decorations(self):  # pylint: disable=missing-docstring
        for deco in self._decorations:
            self.editor.decorations.remove(deco)
        self._decorations[:] = []

    def symbol_pos(self, cursor, character='(', symbol_type=0):
        """
        Find the corresponding symbol position (line, column).
        """
        retval = None, None
        original_cursor = self.editor.textCursor()
        self.editor.setTextCursor(cursor)
        block = cursor.block()
        mapping = {0: block.userData().parentheses,
                   1: block.userData().square_brackets,
                   2: block.userData().braces}
        self._match_braces(mapping[symbol_type], block.position())
        for deco in self._decorations:
            if deco.character == character:
                retval = deco.line, deco.column
                break
        self.editor.setTextCursor(original_cursor)
        self._clear_decorations()
        return retval

    def _refresh_decorations(self):  # pylint: disable=missing-docstring
        for deco in self._decorations:
            self.editor.decorations.remove(deco)
            if deco.match:
                deco.set_foreground(self._match_foreground)
                deco.set_background(self._match_background)
            else:
                deco.set_foreground(self._unmatch_foreground)
                deco.set_background(self._unmatch_background)
            self.editor.decorations.append(deco)

    def on_state_changed(self, state):  # pylint: disable=missing-docstring
        if state:
            self.editor.cursorPositionChanged.connect(self.do_symbols_matching)
        else:
            self.editor.cursorPositionChanged.disconnect(
                self.do_symbols_matching)

    def _match_parentheses(self, parentheses, cursor_pos):
        # pylint: disable=missing-docstring
        for i, info in enumerate(parentheses):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "(" and info.position == pos:
                self._create_decoration(
                    cursor_pos + info.position,
                    self._match_left_parenthesis(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == ")" and info.position == pos - 1:
                self._create_decoration(
                    cursor_pos + info.position,
                    self._match_right_parenthesis(
                        self.editor.textCursor().block(), i - 1, 0))

    def _match_left_parenthesis(self, current_block, i, cpt):
        # pylint: disable=missing-docstring
        try:
            data = current_block.userData()
            parentheses = data.parentheses
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "(":
                    cpt += 1
                    continue
                if info.character == ")" and cpt == 0:
                    self._create_decoration(current_block.position() +
                                            info.position)
                    return True
                elif info.character == ")":
                    cpt -= 1
            current_block = current_block.next()
            if current_block.isValid():
                return self._match_left_parenthesis(current_block, 0, cpt)
            return False
        except RuntimeError:
            # recursion limit exceeded when working with big files
            return False

    def _match_right_parenthesis(self, current_block, i, nb_right_paren):
        # pylint: disable=missing-docstring
        try:
            data = current_block.userData()
            parentheses = data.parentheses
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == ")":
                    nb_right_paren += 1
                    continue
                if info.character == "(":
                    if nb_right_paren == 0:
                        self._create_decoration(
                            current_block.position() + info.position)
                        return True
                    else:
                        nb_right_paren -= 1
            current_block = current_block.previous()
            if current_block.isValid():
                data = current_block.userData()
                parentheses = data.parentheses
                return self._match_right_parenthesis(
                    current_block, len(parentheses) - 1, nb_right_paren)
            return False
        except RuntimeError:
            # recursion limit exceeded when working in big files
            return False

    def _match_square_brackets(self, brackets, current_pos):
        # pylint: disable=missing-docstring
        for i, info in enumerate(brackets):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "[" and info.position == pos:
                self._create_decoration(
                    current_pos + info.position,
                    self._match_left_bracket(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == "]" and info.position == pos - 1:
                self._create_decoration(
                    current_pos + info.position, self._match_right_bracket(
                        self.editor.textCursor().block(), i - 1, 0))

    def _match_left_bracket(self, current_block, i, cpt):
        # pylint: disable=missing-docstring
        try:
            data = current_block.userData()
            parentheses = data.square_brackets
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "[":
                    cpt += 1
                    continue
                if info.character == "]" and cpt == 0:
                    self._create_decoration(
                        current_block.position() + info.position)
                    return True
                elif info.character == "]":
                    cpt -= 1
            current_block = current_block.next()
            if current_block.isValid():
                return self._match_left_bracket(current_block, 0, cpt)
            return False
        except RuntimeError:
            return False

    def _match_right_bracket(self, current_block, i, nb_right):
        # pylint: disable=missing-docstring
        try:
            data = current_block.userData()
            parentheses = data.square_brackets
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == "]":
                    nb_right += 1
                    continue
                if info.character == "[":
                    if nb_right == 0:
                        self._create_decoration(
                            current_block.position() + info.position)
                        return True
                    else:
                        nb_right -= 1
            current_block = current_block.previous()
            if current_block.isValid():
                data = current_block.userData()
                parentheses = data.square_brackets
                return self._match_right_bracket(
                    current_block, len(parentheses) - 1, nb_right)
            return False
        except RuntimeError:
            return False

    def _match_braces(self, braces, cursor_position):
        # pylint: disable=missing-docstring
        for i, info in enumerate(braces):
            pos = (self.editor.textCursor().position() -
                   self.editor.textCursor().block().position())
            if info.character == "{" and info.position == pos:
                self._create_decoration(
                    cursor_position + info.position,
                    self._match_left_brace(
                        self.editor.textCursor().block(), i + 1, 0))
            elif info.character == "}" and info.position == pos - 1:
                self._create_decoration(
                    cursor_position + info.position, self._match_right_brace(
                        self.editor.textCursor().block(), i - 1, 0))

    def _match_left_brace(self, current_block, i, cpt):
        # pylint: disable=missing-docstring
        try:
            data = current_block.userData()
            parentheses = data.braces
            for j in range(i, len(parentheses)):
                info = parentheses[j]
                if info.character == "{":
                    cpt += 1
                    continue
                if info.character == "}" and cpt == 0:
                    self._create_decoration(
                        current_block.position() + info.position)
                    return True
                elif info.character == "}":
                    cpt -= 1
            current_block = current_block.next()
            if current_block.isValid():
                return self._match_left_brace(current_block, 0, cpt)
            return False
        except RuntimeError:
            return False

    def _match_right_brace(self, current_block, i, nb_right):
        # pylint: disable=missing-docstring
        try:
            data = current_block.userData()
            parentheses = data.braces
            for j in range(i, -1, -1):
                if j >= 0:
                    info = parentheses[j]
                if info.character == "}":
                    nb_right += 1
                    continue
                if info.character == "{":
                    if nb_right == 0:
                        self._create_decoration(
                            current_block.position() + info.position)
                        return True
                    else:
                        nb_right -= 1
            current_block = current_block.previous()
            if current_block.isValid():
                data = current_block.userData()
                parentheses = data.braces
                return self._match_right_brace(
                    current_block, len(parentheses) - 1, nb_right)
            return False
        except RuntimeError:
            return False

    def do_symbols_matching(self):
        """
        Performs symbols matching.
        """
        self._clear_decorations()
        data = self.editor.textCursor().block().userData()
        if data and isinstance(data, TextBlockUserData):
            pos = self.editor.textCursor().block().position()
            self._match_parentheses(data.parentheses, pos)
            self._match_square_brackets(data.square_brackets, pos)
            self._match_braces(data.braces, pos)

    def _create_decoration(self, pos, match=True):
        # pylint: disable=missing-docstring
        cursor = self.editor.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(cursor.NextCharacter, cursor.KeepAnchor)
        deco = TextDecoration(cursor, draw_order=10)
        deco.line = cursor.blockNumber() + 1
        deco.column = cursor.columnNumber()
        deco.character = cursor.selectedText()
        deco.match = match
        if match:
            deco.set_foreground(self._match_foreground)
            deco.set_background(self._match_background)
        else:
            deco.set_foreground(self._unmatch_foreground)
            deco.set_background(self._unmatch_background)
        self._decorations.append(deco)
        self.editor.decorations.append(deco)
        return cursor
