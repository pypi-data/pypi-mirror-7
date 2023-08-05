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
import pyqode.core
from pyqode.core import logger
from pyqode.core import get_server, start_server, Worker
from pyqode.python.modes.code_completion import iconFromType
from pyqode.qt import QtCore


class Definition(object):
    """
    A definition object defines a symbol definition in a python source code:
        - import
        - variable
        - class
        - method/function
    """
    def __init__(self, name, icon, line, column, full_name):
        #: Icon resource name associated with the definition, can be None
        self.icon = icon
        #: Definition name (name of the class, method, variable)
        if hasattr(name, "string"):
            name = name.string
        self.name = name
        #: The line of the definition in the current editor text
        self.line = line
        #: The column of the definition in the current editor text
        self.column = column
        #: Symbol name + parent name (for methods and class variables)
        self.full_name = full_name
        #: Possible list of children (only classes have children)
        self.children = []
        if self.full_name == "":
            self.full_name = self.name

    def add_child(self, definition):
        """
        Adds a child definition
        """
        self.children.append(definition)

    def __repr__(self):
        return 'Definition(%r, %r, %r, %r)' % (self.name, self.icon,
                                               self.line, self.column)

    def __eq__(self, other):
        if len(self.children) != len(other.children):
            return False
        for self_child, other_child in zip(self.children, other.children):
            if self_child != other_child:
                return False
        return (self.name == other.name and self.full_name == other.full_name
                and self.line == other.line and self.column == other.column)


def _compare_definitions(a, b):
    """
    Compare two definition list.

    Returns True if they are different.
    """
    if len(a) != len(b):
        return True
    else:
        # compare every definition. If one is different, break
        for def_a, def_b in zip(a, b):
            if def_a != def_b:
                return True
        return False


class DefinedNamesWorker(Worker):
    """
    Subprocess worker that analyses the document using *jedi.defined_names()*.
    """
    _slot = "jedi"

    def __init__(self, code, path, encoding):
        self.code = code
        self.path = path
        self.encoding = encoding

    def __call__(self, client, caller_id, **kwargs):
        import jedi
        ret_val = []
        toplvl_definitions = jedi.defined_names(self.code, self.path,
                                                self.encoding)
        for d in toplvl_definitions:
            d_line, d_column = d.start_pos
            definition = Definition(d.name, iconFromType(d.name, d.type),
                                    d_line, d_column, d.full_name)
            if d.type.upper() == "IMPORT":
                definition.name = definition.full_name
            if d.type == "class":
                sub_definitions = d.defined_names()
                for sub_d in sub_definitions:
                    icon = iconFromType(sub_d.name, sub_d.type)
                    line, column = sub_d.start_pos
                    sub_definition = Definition(
                        sub_d.name, icon, line, column, sub_d.full_name)
                    if sub_definition.full_name == "":
                        sub_definition.full_name = sub_d.name
                    definition.add_child(sub_definition)
            ret_val.append(definition)

        try:
            old_definitions = self.slotDict["%d_definitions" % caller_id]
        except KeyError:
            old_definitions = []

        if ret_val:
            if not _compare_definitions(ret_val, old_definitions):
                ret_val = None
                logger.debug("No changes detected")
            else:
                self.slotDict["%d_definitions" % caller_id] = ret_val
                logger.debug("Document structure %r" % ret_val)
        return ret_val


class DocumentAnalyserMode(pyqode.core.Mode, QtCore.QObject):
    """
    This mode analyses the structure of a document (a tree of
    :class:`pyqode.python.modes.document_analyser.Definition`.

    :attr:pyqode.python.DocumentAnalyserMode.documentChanged` is emitted
    whenever the document structure changed.

    To keep good performances, the analysis task is run when the application is
    idle for more than 1 second (by default).
    """
    IDENTIFIER = "documentAnalyserMode"
    DESCRIPTION = "Analysis the document structure on the fly"

    #: Signal emitted when the document structure changed.
    documentChanged = QtCore.Signal()

    def __init__(self, delay=1000):
        pyqode.core.Mode.__init__(self)
        QtCore.QObject.__init__(self)
        self._jobRunner = pyqode.core.DelayJobRunner(self, nbThreadsMax=1,
                                                     delay=delay)
        #: The list of results (elements might have children; this is actually a tree).
        self.results = []

    def _onStateChanged(self, state):
        if state:
            self.editor.blockCountChanged.connect(self._onLineCountChanged)
            self.editor.newTextSet.connect(self._runAnalysis)
            try:
                srv = get_server()
                if not srv:
                    srv = start_server()
                srv.signals.workCompleted.connect(self._onWorkCompleted)
            except (TypeError, AttributeError):
                pass
        else:
            self.editor.blockCountChanged.disconnect(self._onLineCountChanged)
            self.editor.newTextSet.disconnect(self._runAnalysis)
            try:
                srv = get_server()
                srv.signals.workCompleted.disconnect(self._onWorkCompleted)
            except (TypeError, AttributeError):
                pass

    def _onLineCountChanged(self, e):
        self._jobRunner.requestJob(self._runAnalysis, False)

    def _runAnalysis(self):
        try:
            srv = get_server()
        except AttributeError:
            pass
        else:
            if not self.editor:
                return
            if self.editor.toPlainText():
                worker = DefinedNamesWorker(self.editor.toPlainText(), "", "")
                srv.requestWork(self, worker)
            else:
                self.results = []
                self.documentChanged.emit()

    def _onWorkCompleted(self, caller_id, worker, results):
        if caller_id == id(self) and isinstance(worker, DefinedNamesWorker):
            if results is not None:
                self.results = results
                logger.debug("Document structure changed")
            else:
                self.results = []
            self.documentChanged.emit()

    @property
    def flattenedResults(self):
        """
        Flattens the document structure tree as a simple sequential list.
        """
        ret_val = []
        for d in self.results:
            ret_val.append(d)
            for sub_d in d.children:
                nd = Definition(sub_d.name, sub_d.icon, sub_d.line,
                                sub_d.column, sub_d.full_name)
                nd.name = "  " + nd.name
                nd.full_name = "  " + nd.full_name
                ret_val.append(nd)
        return ret_val
