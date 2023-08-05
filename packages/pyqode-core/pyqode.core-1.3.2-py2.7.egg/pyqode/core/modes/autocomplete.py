#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
""" Contains the AutoCompleteMode """
from pyqode.qt import QtGui
from pyqode.core.mode import Mode


class AutoCompleteMode(Mode):
    """
    Generic auto complete mode that automatically completes the following
    symbols:

        - " -> "
        - ' -> '
        - ( -> )
        - [ -> ]
        - { -> }
    """
    #: Mode identifier
    IDENTIFIER = "autoCompleteMode"
    #: Mode description
    DESCRIPTION = "Automatically complete symbols"
    #: Auto complete mapping, maps input key with completion text.
    MAPPING = {'"': '"', "'": "'", "(": ")", "{": "}", "[": "]"}

    def _onStateChanged(self, state):
        if state:
            self.editor.postKeyPressed.connect(self._onPostKeyPressed)
            self.editor.keyPressed.connect(self._onKeyPressed)
        else:
            self.editor.postKeyPressed.disconnect(self._onPostKeyPressed)
            self.editor.keyPressed.disconnect(self._onKeyPressed)

    def _onPostKeyPressed(self, e):
        if e.isAccepted():
            return
        txt = e.text()
        tc = self.editor.textCursor()
        tc.movePosition(QtGui.QTextCursor.WordRight,
                        QtGui.QTextCursor.KeepAnchor)
        next_char = tc.selectedText()
        if len(next_char):
            next_char = next_char[0]
        else:
            next_char = None
        if txt in self.MAPPING:
            toInsert = self.MAPPING[txt]
            if (not next_char or next_char in self.MAPPING.keys() or
                    next_char in self.MAPPING.values() or
                    next_char.isspace()):
                tc = self.editor.textCursor()
                p = tc.position()
                tc.insertText(toInsert)
                tc.setPosition(p)
                self.editor.setTextCursor(tc)

    def _onKeyPressed(self, e):
        txt = e.text()
        tc = self.editor.textCursor()
        tc.movePosition(QtGui.QTextCursor.Right,
                        QtGui.QTextCursor.KeepAnchor)
        try:
            next_char = tc.selectedText()[0]
        except IndexError:
            next_char = ''
        if txt and next_char == txt and next_char in self.MAPPING:
            e.accept()
            tc.clearSelection()
            self.editor.setTextCursor(tc)
            return
        if e.text() == ')' or e.text() == ']' or e.text() == '}':
            tc = self.editor.textCursor()
            tc.movePosition(tc.Right, tc.KeepAnchor, 1)
            if (tc.selectedText() == ')' or tc.selectedText() == ']' or
                    tc.selectedText() == '}'):
                tc.clearSelection()
                self.editor.setTextCursor(tc)
                e.accept()