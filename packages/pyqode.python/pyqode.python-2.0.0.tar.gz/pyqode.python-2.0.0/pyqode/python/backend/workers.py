#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains the worker classes/functions executed on the server side.
"""
import logging
import os
import jedi
# pylint: disable=C0103, global-variable-not-assigned


def _logger():
    """
     Returns the module's logger
    """
    return logging.getLogger(__name__)


def calltips(request_data):
    """
    Worker that returns a list of calltips.

    A calltips is a tuple made of the following parts:
      - module_name: name of the module of the function invoked
      - call_name: name of the function that is being called
      - params: the list of parameter names.
      - index: index of the current parameter
      - bracket_start

    :returns tuple(module_name, call_name, params)
    """
    code = request_data['code']
    line = request_data['line']
    column = request_data['column']
    path = request_data['path']
    # encoding = request_data['encoding']
    encoding = 'utf-8'
    # use jedi to get call signatures
    script = jedi.Script(code, line, column, path, encoding)
    signatures = script.call_signatures()
    for sig in signatures:
        results = (str(sig.module_name), str(sig.name),
                   [p.description for p in sig.params], sig.index,
                   sig.bracket_start, column)
        # todo: add support for multiple signatures
        return True, results
    return False, []


def goto_assignments(request_data):
    """
    Go to assignements worker.
    """
    code = request_data['code']
    line = request_data['line']
    column = request_data['column']
    path = request_data['path']
    # encoding = request_data['encoding']
    encoding = 'utf-8'
    script = jedi.Script(code, line, column, path, encoding)
    try:
        definitions = script.goto_assignments()
    except jedi.NotFoundError:
        pass
    else:
        ret_val = [(d.module_path, d.line, d.column, d.full_name)
                   for d in definitions]
        return True, ret_val


_old_definitions = {}


class Definition(object):
    """
    Represents a defined name in a python source code (import, function, class,
    method). Definition usually form a tree limited to 2 levels (we stop at the
    method level).
    """
    def __init__(self, name='', icon='', line=1, column=0, full_name=''):
        #: Icon resource name associated with the definition, can be None
        self.icon = icon
        #: Definition name (name of the class, method, variable)
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

    def to_dict(self):
        """
        Serialises a definition to a dictionary, ready for json.

        Children are serialised recursively.
        """
        ddict = {'name': self.name, 'icon': self.icon,
                 'line': self.line, 'column': self.column,
                 'full_name': self.full_name, 'children': []}
        for child in self.children:
            ddict['children'].append(child.to_dict())
        return ddict

    def from_dict(self, ddict):
        """
        Deserialise the definition from a simple dict.
        """
        self.name = ddict['name']
        self.icon = ddict['icon']
        self.line = ddict['line']
        self.column = ddict['column']
        self.full_name = ddict['full_name']
        self.children[:] = []
        for child_dict in ddict['children']:
            self.children.append(Definition().from_dict(child_dict))
        return self

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


def defined_names(request_data):
    """
    Returns the list of defined names for the document.
    """
    def _compare_definitions(a, b):
        """
        Compare two definition lists.

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

    global _old_definitions
    code = request_data['code']
    path = request_data['path']
    # encoding = request_data['encoding']
    encoding = 'utf-8'
    ret_val = []
    toplvl_definitions = jedi.defined_names(code, path, encoding)
    for d in toplvl_definitions:
        d_line, d_column = d.start_pos
        # use full name for import type
        definition = Definition(d.name, icon_from_typename(d.name, d.type),
                                d_line, d_column, d.full_name)
        # check for methods in class
        if d.type == "class" or d.type == 'function':
            try:
                sub_definitions = d.defined_names()
                for sub_d in sub_definitions:
                    icon = icon_from_typename(sub_d.name, sub_d.type)
                    line, column = sub_d.start_pos
                    if sub_d.full_name == "":
                        sub_d.full_name = sub_d.name
                    sub_definition = Definition(sub_d.name, icon, line, column,
                                                sub_d.full_name)
                    definition.add_child(sub_definition)
            except AttributeError:
                pass
        if d.type != 'import':
            ret_val.append(definition)
    try:
        old_definitions = _old_definitions["%s_definitions" % path]
    except KeyError:
        old_definitions = []
    status = False
    if ret_val:
        if not _compare_definitions(ret_val, old_definitions):
            ret_val = None
            _logger().debug("No changes detected")
        else:
            _old_definitions["%s_definitions" % path] = ret_val
            _logger().debug("Document structure changed")
            status = True
            ret_val = [d.to_dict() for d in ret_val]
    return status, ret_val


def quick_doc(request_data):
    """
    Worker that returns the documentation of the symbol under cursor.
    """
    code = request_data['code']
    line = request_data['line']
    column = request_data['column']
    path = request_data['path']
    # encoding = 'utf-8'
    encoding = 'utf-8'
    script = jedi.Script(code, line, column, path, encoding)
    try:
        definitions = script.goto_definitions()
    except jedi.NotFoundError:
        return []
    else:
        ret_val = [d.doc for d in definitions]
        return True, ret_val


def run_pep8(request_data):
    """
    Worker that run the pep8 tool on the current editor text.

    :returns a list of tuples (msg, msg_type, line_number)
    """
    import pep8
    from pyqode.python.backend.pep8utils import CustomChecker
    WARNING = 1
    code = request_data['code']
    path = request_data['path']
    # setup our custom style guide with our custom checker which returns a list
    # of strings instread of spitting the results at stdout
    pep8style = pep8.StyleGuide(parse_argv=False, config_file=True,
                                checker_class=CustomChecker)
    results = pep8style.input_file(path, lines=code.splitlines(True))
    messages = []
    # pylint: disable=unused-variable
    for line_number, offset, code, text, doc in results:
        messages.append((text, WARNING, line_number))
    return True, messages


def run_frosted(request_data):
    """
    Worker that run a frosted (the fork of pyflakes) code analysis on the
    current editor text.
    """
    from frosted import checker
    import _ast
    WARNING = 1
    ERROR = 2
    ret_val = []
    code = request_data['code']
    path = request_data['path']
    encoding = request_data['encoding']
    if not code or not encoding or not path:
        return False, ret_val
    # First, compile into an AST and handle syntax errors.
    try:
        tree = compile(code.encode(encoding), path, "exec",
                       _ast.PyCF_ONLY_AST)
    except SyntaxError as value:
        msg = value.args[0]
        # pylint: disable=unused-variable
        (lineno, offset, text) = value.lineno, value.offset, value.text
        # If there's an encoding problem with the file, the text is None
        if text is None:
            # Avoid using msg, since for the only known case, it
            # contains a bogus message that claims the encoding the
            # file declared was unknown.s
            _logger().warning("%s: problem decoding source", path)
        else:
            ret_val.append((msg, ERROR, lineno))
    else:
        # Okay, it's syntactically valid.  Now check it.
        # pylint: disable=no-value-for-parameter
        w = checker.Checker(tree, os.path.split(path)[1])
        w.messages.sort(key=lambda m: m.lineno)
        for warning in w.messages:
            msg = "%s: %s" % (warning.type.error_code, warning.message)
            line = warning.lineno
            status = (WARNING if warning.type.error_code.startswith('W') else
                      ERROR)
            ret_val.append((msg, status, line))
    return True, ret_val


def icon_from_typename(name, icon_type):
    """
    Returns the icon resource filename that corresponds to the given typename.

    :param name: name of the completion. Use to make the distinction between
        public and private completions (using the count of starting '_')
    :pram typename: the typename reported by jedi

    :returns: The associate icon resource filename or None.
    """
    # todo clean the types list for jedi 0.8.0
    ICONS = {'CLASS': ':/pyqode_python_icons/rc/class.png',
             'IMPORT': ':/pyqode_python_icons/rc/namespace.png',
             'STATEMENT': ':/pyqode_python_icons/rc/var.png',
             'FORFLOW': ':/pyqode_python_icons/rc/var.png',
             'MODULE': ':/pyqode_python_icons/rc/namespace.png',
             'KEYWORD': ':/pyqode_python_icons/rc/keyword.png',
             'PARAM': ':/pyqode_python_icons/rc/var.png',
             'INSTANCE': ':/pyqode_python_icons/rc/var.png',
             'PARAM-PRIV': ':/pyqode_python_icons/rc/var.png',
             'PARAM-PROT': ':/pyqode_python_icons/rc/var.png',
             'FUNCTION': ':/pyqode_python_icons/rc/func.png',
             'DEF': ':/pyqode_python_icons/rc/func.png',
             'FUNCTION-PRIV': ':/pyqode_python_icons/rc/func_priv.png',
             'FUNCTION-PROT': ':/pyqode_python_icons/rc/func_prot.png'}
    ret_val = None
    icon_type = icon_type.upper()
    # jedi 0.8 introduced NamedPart class, which have a string instead of being
    # one
    if hasattr(name, "string"):
        name = name.string
    if icon_type == "FORFLOW" or icon_type == "STATEMENT":
        icon_type = "PARAM"
    if icon_type == "PARAM" or icon_type == "FUNCTION":
        if name.startswith("__"):
            icon_type += "-PRIV"
        elif name.startswith("_"):
            icon_type += "-PROT"
    if icon_type in ICONS:
        ret_val = ICONS[icon_type]
    elif icon_type:
        _logger().warning("Unimplemented completion icon_type: %s", icon_type)
    return ret_val


class JediCompletionProvider:
    """
    Provides code completion using the awesome `jedi`_  library

    .. _`jedi`: https://github.com/davidhalter/jedi
    """
    # pylint: disable=no-init, unused-argument

    @staticmethod
    def complete(code, line, column, path, encoding, prefix):
        """
        Completes python code using `jedi`_.

        :returns: a list of completion.
        """
        ret_val = []
        try:
            script = jedi.Script(code, line, column, path, encoding)
            completions = script.completions()
            print('completions: %r' % completions)
        except jedi.NotFoundError:
            completions = []
        for completion in completions:
            ret_val.append({
                'name': completion.name,
                'icon': icon_from_typename(
                    completion.name, completion.type),
                'tooltip': completion.full_name})
        return ret_val
