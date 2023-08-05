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
"""
Contains the quick documentation panel
"""
from docutils.core import publish_parts
import jedi
import pyqode.core
from pyqode.core import get_server
from pyqode.core.system import driftColor
from pyqode.qt import QtGui


class JediDocWorker(object):
    _slot = "jedi"

    def __init__(self, code, line, col, path, encoding):
        self.code = code
        self.line = line
        self.col = col
        self.path = path
        self.encoding = encoding

    def __call__(self, client, caller_id, *args, **kwargs):
        script = jedi.Script(self.code, self.line, self.col, self.path,
                             self.encoding)
        try:
            definitions = script.goto_definitions()
        except jedi.api.NotFoundError:
            return []
        else:
            ret_val = [d.doc for d in definitions]
            return ret_val


class QuickDocPanel(pyqode.core.Panel):
    """
    This panel quickly shows the documentation of the symbol under
    cursor.
    """
    STYLESHEET = """

    QTextEdit
    {
        background-color: %(tooltip)s;
        color: %(color)s;
    }

    QPushButton
    {
        color: %(color)s;
        background-color: transparent;
        padding: 5px;
        border: none;
    }

    QPushButton:hover
    {
        background-color: %(highlight)s;
        border: none;
        border-radius: 5px;
        color: %(color)s;
    }

    QPushButton:pressed, QCheckBox:pressed
    {
        border: 1px solid %(bck)s;
    }

    QPushButton:disabled
    {
        color: %(highlight)s;
    }
    """

    _KEYS = ["panelBackground", "background", "panelForeground",
             "panelHighlight"]

    #: Mode identifier
    IDENTIFIER = "quickDocPanel"

    #: Mode description
    DESCRIPTION = __doc__

    def __init__(self):
        super(QuickDocPanel, self).__init__()
        # layouts
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        child_layout = QtGui.QVBoxLayout()

        # A QTextEdit to show the doc
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setAcceptRichText(True)
        layout.addWidget(self.textEdit)

        # A QPushButton (inside a child layout for a better alignment)
        # to close the panel
        self.btClose = QtGui.QPushButton()
        self.btClose.setIcon(QtGui.QIcon.fromTheme(
            "application-exit", QtGui.QIcon(":/pyqode-icons/rc/close.png")))
        self.btClose.clicked.connect(self.hide)
        child_layout.addWidget(self.btClose)
        child_layout.addStretch()
        layout.addLayout(child_layout)

        # Action
        self.aQuickDoc = QtGui.QAction("Show documentation", self)
        self.aQuickDoc.setShortcut("Alt+Q")

        self.aQuickDoc.triggered.connect(self._onQuickDoc_triggered)

    def _resetStylesheet(self):
        highlight = driftColor(self.editor.palette().window().color())
        stylesheet = self.STYLESHEET % {
            "tooltip": self.editor.palette().toolTipBase().color().name(),
            "bck": self.editor.palette().window().color().name(),
            "color": self.editor.palette().windowText().color().name(),
            "highlight": highlight.name()}
        self.setStyleSheet(stylesheet)

    def _onInstall(self, editor):
        super(QuickDocPanel, self)._onInstall(editor)
        self._resetStylesheet()
        self.setVisible(False)

    def _onStateChanged(self, state):
        super(QuickDocPanel, self)._onStateChanged(state)
        srv = get_server()
        if state:
            if srv:
                srv.signals.workCompleted.connect(self._onWorkCompleted)
            if hasattr(self.editor, "codeCompletionMode"):
                self.editor.codeCompletionMode.preLoadStarted.connect(
                    self._onPreloadStarted)
                self.editor.codeCompletionMode.preLoadCompleted.connect(
                    self._onPreloadCompleted)
            self.editor.addAction(self.aQuickDoc)
        else:
            if srv:
                srv.signals.workCompleted.disconnect(self._onWorkCompleted)
            self.editor.removeAction(self.aQuickDoc)
            if hasattr(self.editor, "codeCompletionMode"):
                self.editor.codeCompletionMode.preLoadStarted.disconnect(
                    self._onPreloadStarted)
                self.editor.codeCompletionMode.preLoadCompleted.disconnect(
                    self._onPreloadCompleted)

    def _onPreloadStarted(self):
        self.aQuickDoc.setDisabled(True)

    def _onPreloadCompleted(self):
        self.aQuickDoc.setEnabled(True)

    def _onStyleChanged(self, section, key):
        super(QuickDocPanel, self)._onStyleChanged(section, key)
        if key in self._KEYS or not key:
            self._resetStylesheet()

    def _onQuickDoc_triggered(self):
        tc = self.editor.selectWordUnderCursor(selectWholeWord=True)
        assert isinstance(tc, QtGui.QTextCursor)
        w = JediDocWorker(self.editor.toPlainText(), tc.blockNumber() + 1,
                    tc.columnNumber(), self.editor.filePath, self.editor.fileEncoding)
        get_server().requestWork(self, w)

    def _onWorkCompleted(self, caller_id, worker, results):
        if caller_id == id(self) and isinstance(worker, JediDocWorker):
            self.setVisible(True)
            if results:
                if len(results) and results[0] != "":
                    string = "\n\n".join(results)
                    string = publish_parts(
                        string, writer_name='html',
                        settings_overrides={'output_encoding': 'unicode'})['html_body']
                    string = string.replace('colspan="2"', 'colspan="0"')
                    string = string.replace("<th ", '<th align="left" ')
                    string = string.replace('</tr>\n<tr class="field"><td>&nbsp;</td>',
                                            '')
                    if string:
                        self.textEdit.setText(string)

                else:
                    self.textEdit.setText("Documentation not found")
            else:
                self.textEdit.setText("Documentation not found")
