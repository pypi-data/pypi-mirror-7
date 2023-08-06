#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module contains the definition of the SDL symbols,
    including geometry and specific symbol behaviour when needed.

    All symbols inherit the generic Vertical- and Horizontal-
    Symbol classes defined in the "genericSymbols.py" module.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__all__ = ['Input', 'Output', 'State', 'Task', 'ProcedureCall', 'Label',
           'Decision', 'DecisionAnswer', 'Join', 'Start', 'TextSymbol',
           'Procedure', 'ProcedureStart', 'ProcedureStop', 'ASN1Viewer',
           'StateStart', 'Process']

#import traceback
import logging

from PySide.QtCore import Qt, QPoint, QRect, QRectF
from PySide.QtGui import(QPainterPath, QBrush, QColor, QRadialGradient, QPen)

from genericSymbols import HorizontalSymbol, VerticalSymbol, Comment
from Connectors import Connection, JoinConnection, Channel

import ogParser
import ogAST


LOG = logging.getLogger('sdlSymbols')


# SDL-specific: reserved keywords, to be highlighted in textboxes
# Two kind of formatting are possible: black bold, and red bold
SDL_BLACKBOLD = ['\\b{word}\\b'.format(word=word) for word in (
                'DCL', 'CALL', 'ELSE', 'IF', 'THEN', 'MANTISSA', 'BASE',
                'EXPONENT', 'TRUE', 'FALSE', 'MOD', 'FI', 'WRITE', 'WRITELN',
                'LENGTH', 'PRESENT', 'FPAR', 'TODO', 'FIXME', 'XXX',
                'CHECKME', 'PROCEDURE', 'EXTERNAL', 'IN', 'OUT', 'TIMER',
                'SET_TIMER', 'RESET_TIMER', 'VIA', 'ENTRY', 'EXIT',
                'SYNTYPE', 'ENDSYNTYPE', 'CONSTANTS',
                'NEWTYPE', 'ENDNEWTYPE', 'ARRAY', 'STRUCT', 'SYNONYM')]

SDL_REDBOLD = ['\\b{word}\\b'.format(word=word) for word in (
              'INPUT', 'OUTPUT', 'STATE', 'DECISION', 'NEXTSTATE',
              'TASK', 'PROCESS', 'LABEL', 'JOIN', 'CONNECTION')]


# pylint: disable=R0904
class Input(HorizontalSymbol):
    ''' SDL INPUT Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                             'Input', 'Label', 'Connect']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    completion_list = set()

    common_name = 'input_part'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def __init__(self, parent=None, ast=None):
        ''' Create the INPUT symbol '''
        ast = ast or ogAST.Input()
        self.branch_entrypoint = None
        if not ast.pos_y and parent:
            # Make sure the item is placed below its parent
            ast.pos_y = parent.y() + parent.boundingRect().height() + 10
        super(Input, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        gradient = QRadialGradient(50, 50, 50, 50, 50)
        gradient.setColorAt(0, QColor(255, 240, 170))
        gradient.setColorAt(1, Qt.white)
        self.setBrush(QBrush(gradient))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def insert_symbol(self, parent, x, y):
        ''' Insert Input symbol - propagate branch Entry point '''
        # Make sure that parent is a state, not a sibling input
        item_parent = (parent if not isinstance(parent, Input)
                       else parent.parentItem())
        self.branch_entrypoint = item_parent.branch_entrypoint
        super(Input, self).insert_symbol(item_parent, x, y)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.lineTo(width, 0)
        path.lineTo(width - 11, height / 2)
        path.lineTo(width, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Input, self).set_shape(width, height)


class Connect(Input):
    ''' Connect point below a nested state '''
    common_name = 'connect_part'
    auto_expand = False
    resizeable = False
    # Symbol must not use antialiasing, otherwise the middle line is too thick
    _antialiasing = False

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        self.setPen(QPen(Qt.blue))
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(0, height)
        #path.moveTo(0, height / 2)
        #path.lineTo(width, height / 2)
        self.setPath(path)
        super(Input, self).set_shape(width, height)

    def resize_item(self, rect):
        ''' Symbol cannot be resized '''
        return


# pylint: disable=R0904
class Output(VerticalSymbol):
    ''' SDL OUTPUT Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'output'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output()
        super(Output, self).__init__(parent=parent,
                text=ast.inputString, x=ast.pos_x, y=ast.pos_y,
                hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)

        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.lineTo(width - 11, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width - 11, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Output, self).set_shape(width, height)


# pylint: disable=R0904
class Decision(VerticalSymbol):
    ''' SDL DECISION Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['DecisionAnswer', 'Task', 'ProcedureCall',
                             'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'decision'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD + ['\\b{}\\b'.format(word)
                                   for word in ('AND', 'OR')]
    redbold = SDL_REDBOLD
    completion_list = {'length', 'present'}

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Decision()
        # Define the point where all branches of the decision can join again
        self.connectionPoint = QPoint(ast.width / 2, ast.height + 30)
        super(Decision, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QColor(255, 255, 202))
        self.minDistanceToSymbolAbove = 0
        self.parser = ogParser
        self.text_alignment = Qt.AlignHCenter
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    @property
    def terminal_symbol(self):
        '''
            Compute dynamically if the item is terminal by checking
            if all its branches end with a terminator
        '''
        for branch in self.branches():
            if not branch.last_branch_item.terminal_symbol:
                return False
        return True

    def branches(self):
        ''' Return the list of decision answers (as a generator) '''
        return (branch for branch in self.childSymbols()
                if isinstance(branch, DecisionAnswer))

    def set_shape(self, width, height):
        ''' Define polygon points to draw the symbol '''
        path = QPainterPath()
        path.moveTo(width / 2, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width / 2, height)
        path.lineTo(0, height / 2)
        path.lineTo(width / 2, 0)
        self.setPath(path)
        super(Decision, self).set_shape(width, height)

    def resize_item(self, rect):
        ''' On resize event, make sure connection points are updated '''
        delta_y = self.boundingRect().height() - rect.height()
        super(Decision, self).resize_item(rect)
        self.connectionPoint.setX(self.boundingRect().center().x())
        self.connectionPoint.setY(self.connectionPoint.y() - delta_y)
        self.update_connections()

    def update_connections(self):
        ''' Redefined - update arrows shape below connection point '''
        super(Decision, self).update_connections()
        for branch in self.branches():
            for cnx in branch.last_branch_item.connections():
                cnx.reshape()

    def updateConnectionPointPosition(self):
        ''' Compute the joining point of decision branches '''
        new_y = 0
        new_x = self.boundingRect().width() / 2.0
        answers = False
        for branch in self.branches():
            answers = True
            last_cnx = None
            last = branch.last_branch_item
            try:
                # To compute the branch length, we must keep only the symbols,
                # so we must remove the last connection (if any)
                last_cnx, = (c for c in last.childItems() if
                    isinstance(c, Connection) and not
                    isinstance(c.child, (Comment, HorizontalSymbol)))
                # Don't set parent item to None to avoid Qt segfault
                last_cnx.setParentItem(self)
            except ValueError:
                pass
            branch_len = branch.y() + (
                    branch.boundingRect() |
                    branch.childrenBoundingRect()).height()
            try:
                last_cnx.setParentItem(last)
            except AttributeError:
                pass
            # If last item was a decision, use its connection point
            # position to get the length of the branch:
            try:
                branch_len = (last.connectionPoint.y() +
                        self.mapFromScene(0, last.scenePos().y()).y())
            except AttributeError:
                pass
            # Rounded with int() -> mandatory when view scale has changed
            new_y = int(max(new_y, branch_len))
        if not answers:
            new_y = int(self.boundingRect().height())
        new_y += 15
        delta = new_y - self.connectionPoint.y()
        self.connectionPoint.setY(new_y)
        self.connectionPoint.setX(new_x)
        if delta != 0:
            child = self.next_aligned_symbol()
            try:
                child.moveBy(0, delta)
            except AttributeError:
                pass
        self.update_connections()


# pylint: disable=R0904
class DecisionAnswer(HorizontalSymbol):
    ''' If Decision is a "switch", DecisionAnswer is a "case" '''
    _insertable_followers = ['DecisionAnswer', 'Task', 'ProcedureCall',
                        'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'alternative_part'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Answer()
        # temp, FIXME
        self.width, self.height = ast.width, ast.height
        self.terminal_symbol = False
        # last_branch_item is used to compute branch length
        # for the connection point positionning
        self.last_branch_item = self
        super(DecisionAnswer, self).__init__(parent,
                text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        #self.setPen(QColor(0, 0, 0, 0))
        self.branch_entrypoint = self
        self.parser = ogParser

    def insert_symbol(self, parent, x, y):
        ''' ANSWER-specific insersion behaviour: link to connection point '''
        if not parent:
            return
        # Make sure that parent is a state, not a sibling input
        item_parent = (parent if not isinstance(parent, DecisionAnswer)
                       else parent.parentItem())
        super(DecisionAnswer, self).insert_symbol(item_parent, x, y)
        self.last_branch_item.connectionBelow = \
                JoinConnection(self.last_branch_item, item_parent)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def set_shape(self, width, height):
        ''' ANSWER has round, disjoint sides - does not fit in a polygon '''
        self.width, self.height = width, height
        point = width / 2.85
        path = QPainterPath()
        left = QRect(0, 0, point, height)
        right = QRect(width - point, 0, point, height)
        path.arcMoveTo(left, 125)
        path.arcTo(left, 125, 110)
        path.arcMoveTo(right, -55)
        path.arcTo(right, -55, 110)
        path.moveTo(width, height)
        self.setPath(path)
        super(DecisionAnswer, self).set_shape(width, height)


# pylint: disable=R0904
class Join(VerticalSymbol):
    ''' JOIN symbol (GOTO) '''
    auto_expand = False
    arrow_head = 'simple'
    common_name = 'terminator_statement'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        if not ast:
            ast = ogAST.Terminator(defName='')
            ast.pos_y = 0
            ast.width = 35
            ast.height = 35
        super(Join, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setPen(QPen(Qt.blue))
        self.terminal_symbol = True
        self.parser = ogParser

    def resize_item(self, rect):
        ''' Redefinition of the resize item (block is a square) '''
        size = min(rect.width(), rect.height())
        rect.setWidth(size)
        rect.setHeight(size)
        super(Join, self).resize_item(rect)

    def set_shape(self, width, height):
        ''' Define the bouding rectangle of the JOIN symbol '''
        circ = min(width, height)
        path = QPainterPath()
        path.addEllipse(0, 0, circ, circ)
        self.setPath(path)
        super(Join, self).set_shape(width, height)


class ProcedureStop(Join):
    ''' Procedure STOP symbol - very similar to JOIN '''
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def __init__(self, parent=None, ast=None):
        if not ast:
            ast = ogAST.Terminator(defName='')
            ast.pos_y = 0
            ast.width = 35
            ast.height = 35
        super(ProcedureStop, self).__init__(parent, ast)
    completion_list = set()

    def set_shape(self, width, height):
        ''' Define the symbol shape '''
        circ = min(width, height)
        path = QPainterPath()
        path.addEllipse(0, 0, circ, circ)
        point1 = path.pointAtPercent(0.625)
        point2 = path.pointAtPercent(0.125)
        point3 = path.pointAtPercent(0.875)
        point4 = path.pointAtPercent(0.375)
        path.moveTo(point1)
        path.lineTo(point2)
        path.moveTo(point3)
        path.lineTo(point4)
        self.setPath(path)
        # call Join superclass, otherwise symbol will take Join shape
        super(Join, self).set_shape(circ, circ)


# pylint: disable=R0904
class Label(VerticalSymbol):
    ''' LABEL symbol '''
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    # Symbol must not use antialiasing, otherwise the middle line is too thick
    _antialiasing = False
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Label()
        super(Label, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setPen(QPen(Qt.blue))
        self.terminal_symbol = False
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        self.parser = ogParser

    @property
    def common_name(self):
        return 'label' if self.hasParent else 'floating_label'

    def set_shape(self, width, height):
        ''' Define the shape of the LABEL symbol '''
        #print traceback.print_stack()
        path = QPainterPath()
        path.addEllipse(0, height / 2, width / 4, height / 2)
        path.moveTo(width / 4, height * 3 / 4)
        path.lineTo(width / 2, height * 3 / 4)
        # Add arrow head
        path.moveTo(width / 2 - 5, height * 3 / 4 - 5)
        path.lineTo(width / 2, height * 3 / 4)
        path.lineTo(width / 2 - 5, height * 3 / 4 + 5)
        # Add vertical line in the middle of the symbol
        path.moveTo(width / 2, 0)
        path.lineTo(width / 2, height)
        # Make sure the bounding rect is withing specifications
        path.moveTo(width, height)
        self.setPath(path)
        super(Label, self).set_shape(width, height)


# pylint: disable=R0904
class Task(VerticalSymbol):
    ''' TASK symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'task'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ''' Initializes the TASK symbol '''
        ast = ast or ogAST.Task()
        super(Task, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)

        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.lineTo(width, 0)
        path.lineTo(width, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Task, self).set_shape(width, height)


# pylint: disable=R0904
class ProcedureCall(VerticalSymbol):
    ''' PROCEDURE CALL symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'procedure_call'
    # Define reserved keywords for the syntax highlighter
    blackbold = ['\\bWRITELN\\b', '\\bWRITE\\b',
                 '\\bSET_TIMER\\b', '\\bRESET_TIMER\\b']
    redbold = SDL_REDBOLD
    completion_list = {'set_timer', 'reset_timer', 'write', 'writeln'}

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output(defName='')
        super(ProcedureCall, self).__init__(parent,
                text=ast.inputString, x=ast.pos_x, y=ast.pos_y,
                hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRect(0, 0, width, height)
        path.moveTo(7, 0)
        path.lineTo(7, height)
        path.moveTo(width - 7, 0)
        path.lineTo(width - 7, height)
        self.setPath(path)
        super(ProcedureCall, self).set_shape(width, height)


# pylint: disable=R0904
class TextSymbol(HorizontalSymbol):
    ''' Text symbol - used to declare variables, etc. '''
    common_name = 'text_area'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, ast=None):
        ''' Create a Text Symbol '''
        ast = ast or ogAST.TextArea()
        super(TextSymbol, self).__init__(parent=None,
                text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(249, 249, 249)))
        self.terminal_symbol = False
        self.setPos(ast.pos_x, ast.pos_y)
        # Disable hyperlinks for Text symbols
        self._no_hyperlink = True
        # Text is not centered in the box - change default alignment:
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        self.parser = ogParser

    def update_completion_list(self, pr_text):
        ''' When text was entered, update TASK completion list '''
        # Get AST for the symbol
        ast, _, _, _, _ = self.parser.parseSingleElement('text_area', pr_text)
        Task.completion_list |= {dcl for dcl in ast.variables.keys()}

    def set_shape(self, width, height):
        ''' Define the polygon of the text symbol '''
        path = QPainterPath()
        path.moveTo(width - 10, 0)
        path.lineTo(0, 0)
        path.lineTo(0, height)
        path.lineTo(width, height)
        path.lineTo(width, 10)
        path.lineTo(width - 10, 10)
        path.lineTo(width - 10, 0)
        path.lineTo(width, 10)
        self.setPath(path)
        super(TextSymbol, self).set_shape(width, height)

    def resize_item(self, rect):
        ''' Text Symbol only resizes down or right '''
        if self.grabber.resize_mode.endswith('left'):
            return
        self.prepareGeometryChange()
        self.set_shape(rect.width(), rect.height())


class ASN1Viewer(TextSymbol):
    ''' Text symbol with dedicated text highlighting set of words for ASN.1 '''
    blackbold = ['\\b{}\\b'.format(word) for word in (
                 'DEFINITIONS', 'AUTOMATIC', 'TAGS', 'BEGIN', 'END', 'INTEGER',
                 'OCTET', 'STRING', 'BIT', 'REAL', 'SEQUENCE', 'OF', 'WITH',
                 'IMPORTS', 'FROM', 'SIZE', 'CHOICE', 'BOOLEAN')]


# pylint: disable=R0904
class State(VerticalSymbol):
    ''' SDL STATE Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['Input', 'Connect']
    arrow_head = 'simple'
    common_name = 'terminator_statement'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.State()
        ast.inputString = getattr(ast, 'via', None) or ast.inputString
        # Note: ast coordinates are in scene coordinates
        super(State, self).__init__(parent=parent,
                text=ast.inputString, x=ast.pos_x, y=ast.pos_y,
                hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 228, 213)))
        self.terminal_symbol = True
        if parent:
            try:
                # Map AST scene coordinates to get actual position
                self.setPos(self.pos()
                            + self.mapFromScene(ast.pos_x, ast.pos_y))
            except TypeError:
                self.update_position()
        else:
            # Use scene coordinates to position
            self.setPos(ast.pos_x, ast.pos_y)
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    @property
    def allow_nesting(self):
        ''' Redefinition - must be checked according to context '''
        result = not any(elem in unicode(self).lower().strip()
                       for elem in ('-', ',', '*'))
        return result

    @property
    def nested_scene(self):
        ''' Redefined - nested scene per state must be unique '''
        return self._nested_scene

    def double_click(self):
        ''' Catch a double click - Set nested scene '''
        for each, value in self.scene().composite_states.viewitems():
            if unicode(self).split()[0].lower() == unicode(each):
                self.nested_scene = value
                break
        else:
            self.nested_scene = None

    @nested_scene.setter
    def nested_scene(self, value):
        ''' Set the value of the nested scene '''
        self._nested_scene = value

    def update_completion_list(self, pr_text):
        ''' When text was entered, update state completion list '''
        # Get AST for the symbol
        ast, _, _, _, _ = self.parser.parseSingleElement('state', pr_text)
        State.completion_list |= set(ast.statelist)


    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, height / 4, height)

        if self.nested_scene and self.is_composite():
            # Distinguish composite states with dash line
            self.setPen(QPen(Qt.DashLine))
        else:
            self.setPen(QPen(Qt.SolidLine))
        self.setPath(path)
        super(State, self).set_shape(width, height)

    def get_ast(self, pr_text):
        ''' Redefinition of the get_ast function for the state '''
        ast, _, _, _, terminators = self.parser.parseSingleElement('state',
                                                                   pr_text)
        return ast, terminators


class Process(HorizontalSymbol):
    ''' Process symbol '''
    _unique_followers = ['Comment']
    _allow_nesting = True
    common_name = 'process_definition'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()
    is_singleton = True
    arrow_head = 'angle'
    arrow_tail = 'angle'

    def __init__(self, ast=None, subscene=None):
        ast = ast or ogAST.Process()
        super(Process, self).__init__(parent=None,
                                      text=ast.processName,
                                      x=ast.pos_x,
                                      y=ast.pos_y,
                                      hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)
        self.nested_scene = subscene
        self.input_signals = ast.input_signals
        self.output_signals = ast.output_signals
        self.insert_symbol(None, self.x(), self.y())

    def insert_symbol(self, parent, x, y):
        ''' Redefinition - adds connection line to env '''
        super(Process, self).insert_symbol(parent, x, y)
        self.connection = self.connect_to_parent()

    def connect_to_parent(self):
        ''' Redefinition: creates connection to env with a channel '''
        return Channel(self)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.moveTo(7, 0)
        path.lineTo(0, 7)
        path.lineTo(0, height - 7)
        path.lineTo(7, height)
        path.lineTo(width - 7, height)
        path.lineTo(width, height - 7)
        path.lineTo(width, 7)
        path.lineTo(width - 7, 0)
        path.lineTo(7, 0)
        self.setPath(path)
        super(Process, self).set_shape(width, height)


class Procedure(Process):
    ''' Procedure declaration symbol - Very similar to Process '''
    _unique_followers = ['Comment']
    _allow_nesting = True
    common_name = 'procedure'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()
    is_singleton = False

    def __init__(self, ast=None, subscene=None):
        ast = ast or ogAST.Procedure()
        super(Process, self).__init__(parent=None,
                text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)
        self.nested_scene = subscene

    def insert_symbol(self, parent, x, y):
        ''' Redefinition - no connection line to env '''
        super(Process, self).insert_symbol(parent, x, y)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRect(7, 0, width - 14, height)
        path.moveTo(7, 0)
        path.lineTo(0, 7)
        path.lineTo(0, height - 7)
        path.lineTo(7, height)
        path.moveTo(width - 7, 0)
        path.lineTo(width, 7)
        path.lineTo(width, height - 7)
        path.lineTo(width - 7, height)
        self.setPath(path)
        super(Process, self).set_shape(width, height)

    def update_completion_list(self, **kwargs):
        ''' When text was entered, update completion list of ProcedureCall '''
        ProcedureCall.completion_list |= {unicode(self.text)}


# pylint: disable=R0904
class Start(HorizontalSymbol):
    ''' SDL START Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    # There cannot be more than one START symbol in a scene
    is_singleton = True
    common_name = 'start'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    has_text_area = False

    def __init__(self, ast=None):
        ''' Create the START symbol '''
        ast = ast or ogAST.Start()
        self.terminal_symbol = False
        super(Start, self).__init__(parent=None,
                                    text=ast.inputString[slice(0, -6)],
                                    x=ast.pos_x, y=ast.pos_y,
                                    hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 228, 213)))
        # No hyperlink for START symbol because it has no text
        self._no_hyperlink = True
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __unicode__(self):
        ''' User cannot enter text in the START symbol - Return dummy text '''
        return u'START'

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, height / 2, height / 2)
        self.setPath(path)
        super(Start, self).set_shape(width, height)


class ProcedureStart(Start):
    ''' Start symbol of a procedure - only shape differs from Start '''
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    common_name = 'proc_start'

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, height / 2, height / 2)
        path.moveTo(min(width / 2, height / 2), 0)
        path.lineTo(min(width / 2, height / 2), height)
        path.moveTo(max(width / 2, width - height / 2), 0)
        path.lineTo(max(width / 2, width - height / 2), height)
        self.setPath(path)
        super(Start, self).set_shape(width, height)


class StateStart(Start):
    ''' Composite states can have several named START symbols '''
    has_text_area = True
    is_singleton = False
    common_name = 'state_start'

    def __unicode__(self):
        ''' Return the state entry point '''
        return unicode(self.text)
