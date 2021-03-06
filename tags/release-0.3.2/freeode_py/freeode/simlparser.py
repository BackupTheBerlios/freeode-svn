# -*- coding: utf-8 -*-
#***************************************************************************
#    Copyright (C) 2008 by Eike Welk                                       *
#    eike.welk@post.rwth-aachen.de                                         *
#                                                                          *
#    Inspiration came from:                                                *
#    'fourFn.py', an example program, by Paul McGuire,                     *
#    and the 'Spark' library by John Aycock.                               *
#    Many thanks for their exelent contributions to publicly available     *
#    knowledge.                                                            *
#                                                                          #
#    License: GPL                                                          #
#                                                                          *
#    This program is free software; you can redistribute it and/or modify  *
#    it under the terms of the GNU General Public License as published by  *
#    the Free Software Foundation; either version 2 of the License, or     *
#    (at your option) any later version.                                   *
#                                                                          *
#    This program is distributed in the hope that it will be useful,       *
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#    GNU General Public License for more details.                          *
#                                                                          *
#    You should have received a copy of the GNU General Public License     *
#    along with this program; if not, write to the                         *
#    Free Software Foundation, Inc.,                                       *
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#***************************************************************************
'''
Parser for the SIML simulation language.
'''


#TODO: write unit tests that exercise every error message of simlparser.py

#TODO: Implement namespaces. Usefull would be: 
#TODO: - Global namespace for: classes, global functions.
#TODO: - Function local namespace for: data attrbutes, function attributes


from __future__ import division

__version__ = "$Revision: $"


#import debugger
#import pdb
#import operation system stuff
#import sys
import os
#import parser library
import pyparsing
from pyparsing import ( _ustr, Literal, CaselessLiteral, Keyword, Word,  
    ZeroOrMore, OneOrMore, Forward, nums, alphas, alphanums, restOfLine,  
    StringEnd, sglQuotedString, MatchFirst, Combine, Group, Optional,
    ParseException, ParseFatalException, ParseElementEnhance )
#import our own syntax tree classes
from freeode.ast import *



#Enable a fast parsing mode with caching. May not always work.
pyparsing.ParserElement.enablePackrat()



#Took code from pyparsing.Optional as a template
class ErrStop(ParseElementEnhance):
    """Parser that prevents backtracking.
       The parser tries to match the given expression (wich consists of other 
       parsers). If this expression does not match the parser raises a 
       ParseFatalException and parsing stops.
       Otherwise, if the given expression matches, its parse results are returned 
       and the ErrStop has no effect on the parse results.
    """
    #TODO: implement setErrorAction( callableObject )
    #TODO: implement setErrorMessage( errorMsgStr )
    def __init__(self, expr):
        super(ErrStop, self).__init__(expr, savelist=False)
        self.mayReturnEmpty = True
        #Additional string, that will be put in front of the error message.
        self.errMsgStart = '' 

    def parseImpl(self, instring, loc, doActions=True):
        try:
            loc, tokens = self.expr._parse(instring, loc, doActions, callPreParse=False)
        except IndexError:
            raise ParseFatalException(instring, loc, 'Index error: ', self.expr)
        except ParseException, theError:
            errMsg = self.errMsgStart + theError.msg
            raise ParseFatalException(instring, theError.loc, errMsg, self.expr)
        return loc, tokens

    def setErrMsgStart(self, msg):
        """Set additional error message. 
           This string will be put in front of the error message of the given 
           parser.
        """
        self.errMsgStart = msg
        return self
        
    def __str__(self):
        if hasattr(self,"name"):
            return self.name

        if self.strRepr is None:
            self.strRepr = "[" + _ustr(self.expr) + "]"

        return self.strRepr



class ParseActionException(Exception):
    '''Exception raised by the parse actions of the parser'''
    pass



class ParseStage(object):
    '''
    The syntax definition (BNF) resides here.
    
    The parsing is done by the pyparsing libraryy which combines 
    lexer and parser. The Pyparsing library generates a tree of 
    ParseResult objects. These objects
    are replaced by objects inheriting from ast.Node
    in the parse actions of this class.

    Normally a file name is given to the class, and a tree of ast.Node ojects is
    returned. The program can also be entered as a string.
    Additionally the class can parse parts of a program: expressions.

    The parse* methods return a tree of Node objects; the abstract syntax
    tree (AST)

    Usage:
    parser = ParseStage()
    ast1 = parser.parseExpressionStr('0+1+2+3+4')
    ast2 = parser.parseProgramFile('foo-bar.siml')
    '''

    noTreeModification = 0
    '''
    Define how much the parse result is modified, for easier debuging.
    0: normal operation. Compilaton does not work otherwise.
    1: Do not modify parse result (from pyParsing library).

    ParseResult objects are printed as nested lists: ['1', '+', ['2', '*', '3']]
    '''

    keywords = set([])
    '''
    List of all keywords (filled by _defineLanguageSyntax() and defineKeyword).
    '''


    def __init__(self):
        object.__init__(self)
        self._parser = None
        '''The parser object for the whole program (from pyParsing).'''
        self._expressionParser = None
        '''The parser for expressions'''
        #self._lastStmtLocator = StoreLoc(self)
        self._locLastStmt = TextLocation()
        '''Object to remember location of last parsed statement; for
           error message creation.'''
        self.progFileName = None
        '''Name of SIML program file, that will be parsed'''
        self.inputString = None
        '''String that will be parsed'''
        self._builtInFunc = {}
        '''Names of built in functions and some info about them.
           Format: {'function_name':number_of_function_arguments}
           Example: {'sin':1, 'max':2}'''
        #Create parser objects
        self._defineLanguageSyntax()


    def defineKeyword(self, inString):
        '''
        Store keyword (in ParseStage.keywords) and create parser for it.
        Use this function (in _defineLanguageSyntax(...)) instead of using the
        Keyword class directly.
        '''
        ParseStage.keywords.add(inString)
        return Keyword(inString)


    def createTextLocation(self, atChar):
        '''Create a text location object at the given char'''
        return TextLocation(atChar, self.inputString, self.progFileName)


#------------- Parse Actions -------------------------------------------------*
    def _actionDebug(self, str, loc, toks):
        '''Parse action for debuging.'''
        print '------debug action'
        print str
        print loc
        print toks
        print '-------------------'
        return None


    def _actionCheckIdentifier(self, str, loc, toks):
        '''
        Tests wether an identifier is legal.
        If the identifier is equal to any keyword the parse action raises
        an exception.
        Does not change any parse results
        
        tokList is structured like this: ['a1']
        '''
        #
        tokList = toks.asList() #asList() this time ads *no* extra pair of brackets
        identier = tokList[0]
        if identier in ParseStage.keywords:
            #print 'found keyword', toks[0], 'at loc: ', loc
            raise ParseException(str, loc, 
                                 'Keyword can not be used as an identifier: ' + identier)
            #raise ParseFatalException(
            #    str, loc, 'Identifier same as keyword: %s' % toks[0] )
#            raise UserException(
#                'Keyword can not be used as an identifier: ' + identier,
#                 self.createTextLocation(loc))


    def _actionStoreStmtLoc(self, str, loc, toks):
        '''
        Remember location of last parsed statement. Useful for error
        error message creation, since the locations of pyparsing's
        syntax errors are frequenly quit off.
        '''
        self._locLastStmt = self.createTextLocation(loc)


    def _actionBuiltInValue(self, str, loc, toks):
        '''
        Create AST node for a built in value: pi, time
        tokList has the following structure:
        [<identifier>]
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        #create AST node
        nCurr = NodeBuiltInVal()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.dat = tokList #Store the built in value's name
        return nCurr


    def _actionNumber(self, str, loc, toks):
        '''
        Create node for a number: 5.23
        tokList has the following structure:
        [<number>]
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeNum()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.dat = tokList[0] #Store the number
        return nCurr


    def _actionString(self, str, loc, toks):
        '''
        Create node for a string: 'qwert'
        tokList has the following structure:
        [<string>]
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeString()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #nCurr.dat = tokList #Store the string
        nCurr.dat = tokList[1:-1] #Store the string; remove quotes
        return nCurr


    def _actionBuiltInFunction(self, str, loc, toks):
        '''
        Create node for function call: sin(2.1)
        
        Definition:
        funcCall = Group(builtInFuncName         .setResultsName('funcName')
                         + '(' + expressionList  .setResultsName('arguments')
                         + ')' )                 .setParseAction(self._actionBuiltInFunction) \
                                                 .setName('funcCall')#.setDebug(True)
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        #tokList = toks.asList()[0] #there always seems to be
        toks = toks[0]             #an extra pair of brackets
        nCurr = NodeBuiltInFuncCall()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.dat = toks.funcName #function dentifier
        nCurr.kids = toks.arguments.asList() #child expression(s)
        #check if number of function arguments is correct
        if len(nCurr.kids) != self._builtInFunc[nCurr.dat]:
            msg = ('Illegal number of function arguments. \n' + 
                   'Function: %s, required number of arguments: %d, ' + 
                   'given arguments: %d.') % \
                  (nCurr.dat, self._builtInFunc[nCurr.dat], len(nCurr.kids))
            raise UserException(msg, self.createTextLocation(loc))
        return nCurr


    def _actionParenthesesPair(self, str, loc, toks):
        '''
        Create node for a pair of parentheses that enclose an expression: (...)
        tokList has the following structure:
        ['(', <expression>, ')']
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeParentheses()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.kids = [tokList[1]] #store child expression
        return nCurr


    def _actionPrefixOp(self, str, loc, toks):
        '''
        Create node for math prefix operators: -
        tokList has the following structure:
        [<operator>, <expression_l>]
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeOpPrefix1()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.operator = tokList[0]  #Store operator
        nCurr.kids=[tokList[1]] #Store child tree
        return nCurr


    def _actionInfixOp(self, str, loc, toks):
        '''
        Create node for math infix operators: + - * / ^
        tokList has the following structure:
        [<expression_l>, <operator>, <expression_r>]
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeOpInfix2()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #create children and store operator
        lhsTree = tokList[0]   #child lhs
        nCurr.operator = tokList[1] #operator
        rhsTree = tokList[2]   #child rhs
        nCurr.kids=[lhsTree, rhsTree]
        return nCurr


    def _actionAttributeAccess(self, str, loc, toks):
        '''
        Create node for acces to a variable or parameter: bb.ccc.dd
        tokList has the following structure:
        [<part1>, <part2>, <part3>, ...]
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeAttrAccess()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #Look if there is a '$' that indicates time derivatives
        if tokList[0] == '$':
            nCurr.deriv = ('time',)
            del tokList[0]
        #The remaining tokens are the dot separated name
        nCurr.attrName = DotName(tokList)
        return nCurr


    def _actionIfStatement(self, str, loc, toks):
        '''
        Create node for if ... : ... else: ... statement.
        BNF:
        ifStatement = Group(kw('if') + boolExpression + ':'
                            + statementList
                            + Optional(kw('else') +':' + statementList)
                            + kw('end'))
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeIfStmt()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #if ... then ... end
        if len(tokList) == 5:
            condition = tokList[1]
            thenStmts = tokList[3]
            nCurr.kids=[condition, thenStmts]
        #if ... then ... else ... end
        elif len(tokList) == 8:
            condition = tokList[1]
            thenStmts = tokList[3]
            elseStmts = tokList[6]
            nCurr.kids=[condition, thenStmts, elseStmts]
        else:
            raise ParseActionException('Broken >if< statement! loc: ' + str(nCurr.loc))
        return nCurr


    def _actionAssignment(self, str, loc, toks):
        '''
        Create node for assignment: a = 2*b
        BNF:
        assignment = Group(valAccess + '=' + expression + ';')
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeAssignment()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #create children and store operator
        lhsTree = tokList[0]   #child lhs
        nCurr.operator = tokList[1] #operator
        rhsTree = tokList[2]   #child rhs
        nCurr.kids=[lhsTree, rhsTree]
        return nCurr


    def _actionFuncExecute(self, str, loc, toks):
        '''
        Create node for execution of a function (insertion of the code):
            call foo.init()
        BNF:
        funcExecute = Group(kw('call')
                             + dotIdentifier    .setResultsName('funcName')
                             + '(' + ')'
                             + ';')             .setParseAction(self._createBlockExecute)\
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        #tokList = toks.asList()[0] #there always seems to be
        toks = toks[0]             #an extra pair of brackets
        nCurr = NodeFuncExecute()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.funcName = DotName(toks.funcName)    #full (dotted) function name
        return nCurr


    def _actionPrintStmt(self, str, loc, toks):
        '''
        Create node for print statement:
            print 'hello', foo.x
        BNF:
        printStmt = Group(kw('print') + exprList  .setResultsName('argList')
                          + Optional(',')         .setResultsName('trailComma')
                          + ';')                  .setParseAction(self._actionPrintStmt)\
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        #tokList = toks.asList()[0] #there always seems to be
        toks = toks[0]             #an extra pair of brackets
        nCurr = NodePrintStmt()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.kids = toks.argList.asList()
        if toks.trailComma:
            nCurr.newline = False
        return nCurr


    def _actionGraphStmt(self, str, loc, toks):
        '''
        Create node for graph statement:
            graph foo.x, foo.p
        BNF:
        graphStmt = Group(kw('graph') + exprList  .setResultsName('argList')
                          + ';')                  .setParseAction(self._actionDebug)\
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        #tokList = toks.asList()[0] #there always seems to be
        toks = toks[0]             #an extra pair of brackets
        nCurr = NodeGraphStmt()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.kids = toks.argList.asList()
        return nCurr


    def _actionStoreStmt(self, str, loc, toks):
        '''
        Create node for graph statement:
            graph foo.x, foo.p
        BNF:
        graphStmt = Group(kw('graph') + exprList  .setResultsName('argList')
                          + ';')                  .setParseAction(self._actionDebug)\
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        #tokList = toks.asList()[0] #there always seems to be
        toks = toks[0]             #an extra pair of brackets
        nCurr = NodeStoreStmt()
        nCurr.loc = self.createTextLocation(loc) #Store position
        nCurr.kids = toks.argList.asList()
        return nCurr


    def _actionStatementList(self, str, loc, toks):
        '''
        Create node for list of statements: a=1; b=2; ...
        BNF:
        statementList << Group(OneOrMore(statement))
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeStmtList()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #create children - each child is a statement
        for tok in tokList:
            nCurr.kids.append(tok)
        return nCurr


    def _actionAttrDefinition(self, str, loc, toks):
        '''
        Create node for defining parameter, variable or submodel:
            'data foo, bar: baz.boo parameter;
        One such statement can define multiple parmeters; and an individual
        NodeAttrDef is created for each. They are returned together inside a
        list node of type NodeStmtList.
        BNF:
        attrNameList = Group( identifier +
                                ZeroOrMore(',' + identifier))
        attrRole = kw('parameter') | kw('variable')
        #parse 'data foo, bar: baz.boo parameter;
        attributeDef = Group(kw('data')
                             + attrNameList                          .setResultsName('attrNameList')
                             + ':' + dotIdentifier                   .setResultsName('className')
                             + Optional(attrRole)                    .setResultsName('attrRole')
                             + ';')
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        #tokList = toks.asList()[0] #there always seems to be
        toks = toks[0]             #an extra pair of brackets
        #multiple attributes can be defined in a single statement
        #Create a node for each of them and put them into a statemnt list
        attrDefList = NodeStmtList(loc=self.createTextLocation(loc))
        nameList = toks.attrNameList.asList()
        for name in nameList:
            if name in self.keywords:
                errMsg = 'Keyword can not be used as an identifier: ' + name
                raise ParseFatalException(str, loc, errMsg)
            attrDef = NodeAttrDef(loc=self.createTextLocation(loc))
            attrDef.attrName = DotName(name) #store attribute name
            attrDef.className = DotName(toks.className.asList())  #store class name
            #store the role
            if toks.attrRole == 'parameter':
                attrDef.role = RoleParameter
            else:
                #we do not know if variable or parameter; submodels will be
                #labled variables even thoug these categories don't apply
                #to them.
                attrDef.role = RoleVariable
            attrDefList.appendChild(attrDef)
        #Special case: only one attribute defined
        if len(attrDefList) == 1:
            return attrDefList[0] #take it out of the list and return it
        else:
            return attrDefList #return list with multiple definitions


    def _actionFuncDefinition(self, str, loc, toks):
        '''
        Create node for definition of a (member) function:
            func init(): a=1; end
        BNF:
        memberFuncDef = Group(kw('func')
                              + identifier                           .setResultsName('funcName')
                              + '(' + ')' + ':'
                              + ZeroOrMore(statement)                .setResultsName('funcBody', True)
                              + kw('end'))        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        #tokList = toks.asList()[0] #there always seems to be
        toks = toks[0]             #an extra pair of brackets
        nCurr = NodeFuncDef()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #store name of block
        nCurr.name = DotName(toks.funcName)
        #create children - each child is a statement
        statements = []
        if len(toks.funcBody) > 0:
            statements = toks.funcBody.asList()[0]
        for stmt1 in statements:
            nCurr.appendChild(stmt1)
        return nCurr


    def _actionClassDef(self, str, loc, toks):
        '''
        Create node for definition of a class:
            class foo(Model): ... end
        BNF:
        classDef = Group(kw('class')
                         + identifier                 .setResultsName('className')
                         + '(' + dotIdentifier        .setResultsName('superName')
                         + ')' + ':'
                         + OneOrMore(attributeDef)    .setResultsName('attributeDef', True)
                         + ZeroOrMore(memberFuncDef)  .setResultsName('memberFuncDef', True)
                         + kw('end'))
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        #tokList = toks.asList()[0] #there always seems to be
        toks = toks[0]             #an extra pair of brackets
        nCurr = NodeClassDef()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #store class name and name of super class
        nCurr.className = DotName(toks.className)
        nCurr.superName = DotName(toks.superName)
        #create children (may or may not be present):  data, functions
        data, funcs = [], [] #special cases for empty edinitions necessary
        if len(toks.attributeDef) > 0:
            data = toks.attributeDef.asList()[0]
        if len(toks.memberFuncDef) > 0:
            funcs =  toks.memberFuncDef.asList()[0]
        for stmt1 in data + funcs:
            nCurr.appendChild(stmt1)
        return nCurr


    def _actionProgram(self, str, loc, toks):
        '''
        Create the root node of a program.
        BNF:
        program = Group(OneOrMore(classDef))
        '''
        if ParseStage.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeProgram()
        nCurr.loc = self.createTextLocation(loc) #Store position
        #create children - each child is a class
        for tok in tokList:
            nCurr.kids.append(tok)
        return nCurr


#------------------- BNF --------------------------------------------------------
    def _defineLanguageSyntax(self):
        '''
        Here is Siml's BNF
        Creates the objects of the pyParsing library,
        that do all the work.
        '''
        #define short alias so they don't clutter the text
        kw = self.defineKeyword # Usage: test = kw('variable')
        L = Literal # Usage: L('+')

        #Values that are built into the language
        builtInValue = (kw('pi') | kw('time'))                      .setParseAction(self._actionBuiltInValue)\
                                                                    .setName('builtInValue')#.setDebug(True)

        #Functions that are built into the language
        #Dict: {'function_name':number_of_function_arguments}
        self._builtInFunc = {'sin':1, 'cos':1, 'tan':1, 
                             'sqrt':1, 'exp':1, 'log':1,
                             'min':2, 'max':2}
        builtInFuncName = MatchFirst(
            [kw(funcName) 
             for funcName in self._builtInFunc.keys()])             .setName('builtInFuncName')#.setDebug(True)

        #Integer (unsigned).
        uInteger = Word(nums)                                       .setName('uInteger')#.setDebug(True)
        #Floating point number (unsigned).
        eE = CaselessLiteral( 'E' )
        uNumber = Group( Combine(
                    uInteger +
                    Optional('.' + Optional(uInteger)) +
                    Optional(eE + Word('+-'+nums, nums))))          .setParseAction(self._actionNumber)\
                                                                    .setName('uNumber')#.setDebug(True)
        #string
#        stringConst = QuotedString(quoteChar='\'', escChar='\\')    .setParseAction(self._actionString)\
#                                                                    .setName('string')#.setDebug(True)
        stringConst = sglQuotedString                               .setParseAction(self._actionString)\
                                                                    .setName('string')#.setDebug(True)

        # .............. Mathematical expression .............................................................
        #'Forward declarations' for recursive rules
        expressionList = Forward() #For built in functions TODO: this should be a list of bool expressions
        boolExpression = Forward()
        expression = Forward()
        term =  Forward()
        factor = Forward()
        signedAtom = Forward()
        valAccess = Forward() #For PDE: may also contain expressions for slices: a.b.c(2.5:3.5)

        #Basic building blocks of mathematical expressions e.g.: (1, x, e,
        #sin(2*a), (a+2), a.b.c(2.5:3.5))
        #Function call, parenthesis and memory access can however contain
        #expressions.
        #TODO: funcCall should be unified with with call to member function
        funcCall = Group(builtInFuncName                            .setResultsName('funcName')
                         + '(' + expressionList                     .setResultsName('arguments')
                         + ')' )                                    .setParseAction(self._actionBuiltInFunction) \
                                                                    .setName('funcCall')#.setDebug(True)
        parentheses = Group('(' + expression + ')')                 .setParseAction(self._actionParenthesesPair) \
                                                                    .setName('parentheses')#.setDebug(True)
        atom = ( uNumber | stringConst | builtInValue |
                 funcCall | valAccess | parentheses     )           .setName('atom')#.setDebug(True)

        #The basic mathematical operations: -a+b*c^d.
        #All operations have right-to-left associativity; althoug this is only
        #required for exponentiation. Precedence decreases towards the bottom.
        #Unary minus: -a, not a;
        negop = '-' | kw('not')
        unaryMinus = Group(negop + signedAtom)          .setParseAction(self._actionPrefixOp) \
                                                        .setName('unaryMinus')#.setDebug(True)
        signedAtom << (atom | unaryMinus)               .setName('signedAtom')#.setDebug(True)

        #Exponentiation: a^b;
        factor1 = signedAtom                            .setName('factor1')#.setDebug(True)
        factor2 = Group(signedAtom + '**' + factor)     .setParseAction(self._actionInfixOp) \
                                                        .setName('factor2')#.setDebug(True)
        factor << (factor2 | factor1)                   .setName('factor')#.setDebug(True)

        #multiplicative operations: a*b; a/b
        multop = L('*') | L('/') | L('and')
        term1 = factor                                  .setName('term1')#.setDebug(True)
        term2 = Group(factor + multop + term)           .setParseAction(self._actionInfixOp) \
                                                        .setName('term2')#.setDebug(True)
        term << (term2 | term1)                         .setName('term')#.setDebug(True)

        #additive operations: a+b; a-b
        addop  = L('+') | L('-') | L('or')
        expression1 = term                              .setName('expression1')#.setDebug(True)
        expression2 = Group(term + addop + expression)  .setParseAction(self._actionInfixOp) \
                                                        .setName('expression2')#.setDebug(True)
        expression << (expression2 | expression1)       .setName('expression')#.setDebug(True)

        #Relational operators : <, >, ==, ...
        relop = L('<') | L('>') | L('<=') | L('>=') | L('==') | L('!=')
        boolExpr1 = expression
        boolExpr2 = Group(expression + relop + boolExpression)  .setParseAction(self._actionInfixOp) \
                                                                .setName('boolExpr2')#.setDebug(True)
        boolExpression << (boolExpr2 | boolExpr1)               .setName('boolExpression')#.setDebug(True)
        
        #expression list - sparse: 2, foo.bar, 3*sin(baz)
        commaSup = Literal(',').suppress()
        expressionList << Group(boolExpression
                                + ZeroOrMore(commaSup + boolExpression)).setName('exprList')
        #................ End mathematical expression ................................................---

        #................ Identifiers ...................................................................
        identifier = Word(alphas+'_', alphanums+'_')            .setName('identifier')#.setDebug(True)
        #Use this when defining new objects. The new identifier is checked if it is not a keyword
        newIdentifier = identifier.copy()                       .setParseAction(self._actionCheckIdentifier)
        #Compound identifiers for variables or parameters 'aaa.bbb'.
        dotSup = Literal('.').suppress()
        dotIdentifier = Group(identifier +
                              ZeroOrMore(dotSup + identifier))  .setName('dotIdentifier')#.setDebug(True)
        #Method to access a stored value: dotted name ('a.b.c'), 
        # with optional differentiation operator ('$a.b.c'), 
        # and optional partial access ('a.b.c[2:5]'). (partial access is currently not implemented)
        valAccess << Group( Optional('$') +
                            identifier +
                            ZeroOrMore(dotSup + identifier) )   .setParseAction(self._actionAttributeAccess) \
                                                                .setName('valAccess')#.setDebug(True)

#------------------- Statements ---------------------------------------------------------------
        statementList = Forward()
        #Flow control - if then else
        ifStatement = Group(kw('if') 
                            + ErrStop( boolExpression + ':'
                                       + statementList
                                       + Optional(kw('else') 
                                                  + ErrStop(':' + statementList))
                                       + kw('end'))
                            )                                        .setParseAction(self._actionIfStatement)\
                                                                     .setName('ifStatement')#.setDebug(True)
        #compute expression and assign to value
        assignment = Group(valAccess + '=' 
                           + ErrStop(boolExpression + ';')           .setErrMsgStart('Assignment statement: ')
                           )                                         .setParseAction(self._actionAssignment)\
                                                                     .setName('assignment')#.setDebug(True)
        #execute a block - insert code of a child model
        #function arguments are currently missing
        #TODO: Unify with builtin functions.
        funcExecute = Group(kw('call')
                             + ErrStop(dotIdentifier                 .setResultsName('funcName')
                                       + '(' + ')'
                                       + ';')                        .setErrMsgStart('Call statement: ')
                             )                                       .setParseAction(self._actionFuncExecute)\
                                                                     .setName('blockExecute')#.setDebug(True)
        #print something to stdout
        printStmt = Group(kw('print') 
                          + ErrStop(expressionList                   .setResultsName('argList')
                                    + Optional(',')                  .setResultsName('trailComma')
                                    + ';')                           .setErrMsgStart('Print statement: ')
                          )                                          .setParseAction(self._actionPrintStmt)\
                                                                     .setName('printStmt')#.setDebug(True)
        #show graphs
        graphStmt = Group(kw('graph') 
                          + ErrStop(expressionList                   .setResultsName('argList')
                                    + ';')                           .setErrMsgStart('Graph statement: ')
                          )                                          .setParseAction(self._actionGraphStmt)\
                                                                     .setName('graphStmt')#.setDebug(True)
        #store to disk
        storeStmt = Group(kw('save') 
                          + ErrStop(Group(Optional(stringConst))     .setResultsName('argList')
                                    + ';')                           .setErrMsgStart('Save statement: ')
                          )                                          .setParseAction(self._actionStoreStmt)\
                                                                     .setName('storeStmt')#.setDebug(True)

        statement = (storeStmt | graphStmt | printStmt |
                     funcExecute | ifStatement | assignment)         .setParseAction(self._actionStoreStmtLoc)\
                                                                     .setName('statement')#.setDebug(True)
        statementList << Group(OneOrMore(statement))                 .setParseAction(self._actionStatementList)\
                                                                     .setName('statementList')#.setDebug(True)

#---------- Define new objects ---------------------------------------------------------------------*
        #define parameters, variables and submodels
        #commaSup = Literal(',').suppress()
        #parse: 'foo, bar, baz 
        #Identifiers must not be keywords, check is done in _actionAttrDefinition
        newAttrList = Group(identifier
                            + ZeroOrMore(commaSup + identifier))     .setName('attrNameList')
        attrRole = kw('parameter') | kw('variable')
        #parse 'data foo, bar: baz.boo parameter;
        attributeDef = Group(kw('data')
                             + ErrStop(newAttrList                   .setResultsName('attrNameList')
                                       + ':' + dotIdentifier         .setResultsName('className')
                                       + Optional(attrRole)          .setResultsName('attrRole')
                                       + ';')                        .setErrMsgStart('Wrong syntax in data definition. ')
                             )                                       .setParseAction(self._actionAttrDefinition)\
                                                                     .setName('attributeDef')#.setDebug(True)
        #define member function (method) 
        #TODO: function arguments are currently missing
        #TODO: unify with built in functions
        funcDef = Group(kw('func')
                        + ErrStop(newIdentifier                      .setResultsName('funcName')
                                  + '(' + ')' + ':'
                                  + ZeroOrMore(statement)            .setResultsName('funcBody', True)
                                  + kw('end'))                       .setErrMsgStart('Wrong syntax in function definition. ')
                        )                                            .setParseAction(self._actionFuncDefinition)\
                                                                     .setName('memberFuncDef')#.setDebug(True)
        #definition of a class (process, model, type?)
        classDef = Group(kw('class')
                         + ErrStop(newIdentifier                     .setResultsName('className')
                                   + '(' + dotIdentifier             .setResultsName('superName')
                                   + ')' + ':'
                                   + ZeroOrMore(attributeDef)        .setResultsName('attributeDef', True)
                                   + ZeroOrMore(funcDef)             .setResultsName('memberFuncDef', True)
                                   + kw('end'))                      .setErrMsgStart('Wrong syntax in class definition. ')
                         )                                           .setParseAction(self._actionClassDef)\
                                                                     .setName('classDef')#.setDebug(True)

        program = (Group(OneOrMore(classDef)) + StringEnd())         .setParseAction(self._actionProgram)\
                                                                     .setName('program')#.setDebug(True)

        #................ End of language definition ..................................................

        #determine start symbol
        startSymbol = program
        #set up comments
        singleLineCommentCpp = '//' + restOfLine
        singleLineCommentPy = '#' + restOfLine
        startSymbol.ignore(singleLineCommentCpp)
        startSymbol.ignore(singleLineCommentPy)
        #no tab expansion
        startSymbol.parseWithTabs()
        #store parsers
        self._parser = startSymbol
        self._expressionParser = boolExpression


    def parseExpressionStr(self, inString):
        '''Parse a single expression. Example: 2*a+b'''
        self.inputString = inString
        return self._expressionParser.parseString(inString).asList()[0]


    def parseProgramStr(self, inString):
        '''Parse a whole program. The program is entered as a string.'''
        self.inputString = inString
        result = self._parser.parseString(inString).asList()[0]
        return result


    def parseProgramFile(self, fileName):
        '''Parse a whole program. The program's file name is supplied.'''
        self.progFileName = os.path.abspath(fileName)
        #open and read the file
        try:
            inputFile = open(self.progFileName, 'r')
            inputFileContents = inputFile.read()
            inputFile.close()
        except IOError, theError:
            message = 'Could not read input file.\n' + str(theError)
            raise UserException(message, None)
        #parse the program
        try:
            astTree = self.parseProgramStr(inputFileContents)
        except (ParseException, ParseFatalException), theError:
            #add additional information to the pyparsing exceptions.
            msgPyParsing = str(theError) + '\n'
            #see if there is the loc of a successfully parsed statement
            if self._locLastStmt.isValid():
                msgLastStmt = 'Last parsed statement was: \n' \
                              + str(self._locLastStmt)
            else:
                msgLastStmt = ''
            #make UserException that will be visible to the user
            loc =  TextLocation(theError.loc, theError.pstr, self.progFileName)
            raise UserException(msgPyParsing + msgLastStmt, loc)
        return astTree



#class StoreLoc(object):
#    '''
#    Functor class to store the location of a parsed pattern.
#    The location is stored in the data member:
#        self.loc
#
#    An instance of this class is given to a parser as a parse action.
#    every time the parser succeeds the __call__ method is executed, and
#    the location of the parser's match is stored.
#    '''
#    def __init__(self, parser):
#        super(StoreLoc, self).__init__()
#        self.loc = None
#        '''The stored location or None, if parse action is never executed.'''
#        self.parser = parser
#        '''Parser for which this class works'''
#
#    def __call__(self, str, loc, toks):
#        '''The parse action that stores the location.'''
#        self.loc = TextLocation(loc, self.parser.inputString,
#                                self.parser.progFileName)



class ILTGenException(Exception):
    '''Exception thrown by the ILT-Process Generator (Compiler internal error)'''
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)



class ILTProcessGenerator(object):
    '''
    Generate process for the intermediate language tree (ILT).

    Takes a process from the AST and generates a new process. This new process
    contains the atributes of all submodels. The code of the submodels' blocks
    is inserted (imlined) into the new process' blocks.
    The new process is a 'flattened' version of the original structured process.
    '''
    def __init__(self, astRoot):
        self.astRoot = astRoot
        '''The AST'''
        self.astClasses = {}
        '''dict of classes in ast: {'mod1':NodeClassDef}'''
        self.astProcess = NodeClassDef() #dummy for pydev's completion
        '''the original process that is now instantiated'''
        self.astProcessAttributes = {}
        '''Atributes of the original process. Dict: {('mod1', 'var1'):NodeAttrDef}'''
        self.process = NodeClassDef() #dummy for pydev's completion
        '''The new process which is currently assembled'''
        self.processAttributes = {}
        '''Attributes of the new process: {('mod1', 'var1'):NodeAttrDef}'''
        self.stateVariables = {}
        '''State variables of the new process; {('mod1', 'var1'):NodeAttrDef}'''
        self.atomicClasses = set([('Real',),('Distribution',),('DistributionDomain',)])
        '''Classes that have no internal structure'''

        #populate self.classes and self.processes
        self.findClassesInAst()


    def findClassesInAst(self):
        '''
        Extract all class definitions from the ast and put them into self.classes.
        Additionally the process definitions go into self.processes.
        '''
        for classDef in self.astRoot:
            #check for duplicate classes
            if classDef.className in self.astClasses:
                raise UserException('Redefinition of class: %s'
                                    % str(classDef.className),
                                    classDef.loc)
            self.astClasses[classDef.className] = classDef


    def addBuiltInParameters(self):
        '''
        Some parameters exist without beeing defined; create them here.

        -In a later stage they could be inherited from a base class.
        -This method could be expanded into a more general mechanism for
         built-in values, like pi.
        '''
        #Put solutionparameters as first attribute into the process
        solParAttr = NodeAttrDef(loc=0, attrName=DotName('solutionParameters'),
                                 className=DotName('solutionParametersClass'))
        self.astProcess.insertChild(0, solParAttr)


    def findAttributesRecursive(self, astClass, namePrefix=DotName(), recursionDepth=0):
        '''
        Find all of the process' attributes (recursing into the sub-models)
        and put then into self.astProcessAttributes.

        Attributes are: parameters, variables, sub-models, and functions.
        The definition in the AST is searched NOT the new process.

        Arguments:
            astClass   : class definition from the AST (NodeClassDef),
                         or NodeAttrDefMulti, NodeStmtList
            namePrefix : tuple of strings. Prefix for the dotted name of the
                         class' attributes.
        Output:
            self.astProcessAttributes : dict: {('mod1', 'var1'):NodeAttrDef}
        '''
        #check recursion depth
        maxRecursionDepth = 100
        if recursionDepth > maxRecursionDepth:
            raise UserException('Maximum submodel nesting depth (%d) exeeded'
                                % maxRecursionDepth, astClass.loc)
        #each of the class' children is a definition or a list of definitions
        for attrDef in astClass:
            #inspect Node type
            #list of definitions - look into list: recurse
            if isinstance(attrDef, NodeStmtList):
                self.findAttributesRecursive(attrDef, namePrefix, #note same name prefix
                                             recursionDepth+1)
                continue #do not create an attribute for the list Node
            #definition of data attribute or submodel: get name, store attribute
            elif isinstance(attrDef, NodeAttrDef):
                attrName = attrDef.attrName
            #definition of method (function): get name, store attribute
            elif isinstance(attrDef, NodeFuncDef):
                attrName = attrDef.name
            else:
                raise ILTGenException('Unknown Node.' + repr(attrDef))

            #store attribute in dict
            #prepend prefix to attribute name
            longAttrName = namePrefix + attrName
            #Check redefinition
            if longAttrName in self.astProcessAttributes:
                raise UserException('Redefinition of: ' +
                                    str(longAttrName), attrDef.loc)
            #put new attribute into dict.
            self.astProcessAttributes[longAttrName] = attrDef

            #recurse into submodel, if definition of submodel
            if isinstance(attrDef, NodeAttrDef) and \
              (not attrDef.className in self.atomicClasses):
                #User visible error if class does not exist
                if not attrDef.className in self.astClasses:
                    raise UserException('Undefined class: '
                                        + str(attrDef.className),
                                        attrDef.loc)
                subModel = self.astClasses[attrDef.className]
                self.findAttributesRecursive(subModel, longAttrName,
                                             recursionDepth+1)


    def copyDataAttributes(self):
        '''
        Copy variables and parameters from all submodels into the procedure
        Additionaly puts all attributes into self.processAttributes
        arguments:
        '''
        #Iterate over the (variable, parameter, submodel, function) definitions
        for longName, defStmt in self.astProcessAttributes.iteritems():
            #we only want atomic data! No user defined classes, no methods
            if (not isinstance(defStmt, NodeAttrDef)) or \
               (not defStmt.className in self.atomicClasses):
                continue
            newAttr = defStmt.copy() #copy definition,
            newAttr.attrName = longName #exchange name with long name (a.b.c)
            self.process.appendChild(newAttr) #put new attribute into ILT process
            self.processAttributes[longName] = newAttr #and into quick access dict
        return


    def copyFuncRecursive(self, block, namePrefix, newBlock, illegalBlocks, recursionDepth=0):
        '''
        Copy block into newBlock recursively.
        Copies all statements of block and all statements of blocks that are
        executed in this block, recursively.
            block          : A block definition
            namePrefix     : a tuple of strings. prefix for all variable names.
            newBlock       : the statements are copied here
            illegalBlocks  : blocks (functions) that can not be called
                             (included) in this context.
        '''
        #Protect against infinite recursion
        maxRecursionDepth = 100
        if recursionDepth > maxRecursionDepth:
            raise UserException('Maximum function recursion depth (%d) exeeded'
                                % maxRecursionDepth, block.loc)
        for statement in block:
            #Block execution statement: insert the block's code
            if isinstance(statement, NodeFuncExecute):
                subBlockName = namePrefix + statement.funcName #dotted block name
                subModelName = subBlockName[:-1] #name of model, where block is defined
#                #Error if submodel or method does not exist
#                if not subModelName in self.astProcessAttributes:
#                    raise UserException('Undefined submodel: ' +
#                                        str(subModelName), statement.loc)
                if not subBlockName in self.astProcessAttributes:
                    raise UserException('Undefined method: ' +
                                        str(subBlockName), statement.loc)
                #Check if executing (inlining) this block is allowed
                if statement.funcName in illegalBlocks:
                    raise UserException('Function can not be called here: ' +
                                        str(statement.funcName), statement.loc)
                #Find definition of function
                subBlockDef = self.astProcessAttributes[subBlockName]
                #Check if subBlockDef is really a function definition
                if not isinstance(subBlockDef, NodeFuncDef):
                    raise UserException('Only functions can be called', 
                                        statement.loc)
                #Recurse into the function definition. 
                #Insert its text in place of the call statement
                self.copyFuncRecursive(subBlockDef, subModelName, newBlock, 
                                       illegalBlocks, recursionDepth+1)
            #Any other statement: copy statement
            else:
                newStmt = statement.copy()
                #put prefix before all varible names in new Statement
                for var in newStmt.iterDepthFirst():
                    if not isinstance(var, NodeAttrAccess):
                        continue
                    newAttrName = namePrefix + var.attrName
                    var.attrName = newAttrName
                #put new statement into new block
                newBlock.appendChild(newStmt)


    def checkUndefindedReferences(self, tree):
        '''
        Look at all attribute accessors and see if the attributes exist in
        the new process.
        '''
        #iterate over all nodes in the syntax tree
        for node in tree.iterDepthFirst():
            if not isinstance(node, NodeAttrAccess):
                continue
            if not (node.attrName) in self.processAttributes:
                raise UserException('Undefined reference: ' +
                                    str(node.attrName), node.loc)



    def findStateVariables(self, dynamicMethod):
        '''
        Search for variables with a $ and mark them:
            1.: in their definition set role = RoleStateVariable;
            2.: put them into self.stateVariables.
        All other variables are considered algebraic variables and in their
        definition role = RoleAlgebraicVariable.
        Arguments:
            dynamicMethod : method definition that is searched (always the
                            dynamic/run method)
        output:
            self.stateVariables    : dict: {('a','b'):NodeAttrDef(...)}
            definition of variable : role = RoleStateVariable if variable is
                                     state variable;
                                     role = RoleAlgebraicVariable otherwise.
        '''
        #initialization: in all variable definitions set role = RoleAlgebraicVariable
        for varDef in self.processAttributes.itervalues():
            if varDef.role != RoleVariable:
                continue
            varDef.role = RoleAlgebraicVariable
        #iterate over all nodes in the syntax tree and search for variable accesses
        for node in dynamicMethod.iterDepthFirst():
            if not isinstance(node, NodeAttrAccess):
                continue
            #State variables are those that have time derivatives
            if node.deriv != ('time',):
                continue
            #OK, there is a '$' operator; the thing is a state variable
            #get definition of variable
            stateVarDef = self.processAttributes[node.attrName]
            #Check conceptual constraint: no $parameter allowed
            if stateVarDef.role == RoleParameter:
                raise UserException('Parameters can not be state variables: ' +
                              str(node.attrName), node.loc)
            #remember: this is a state variable; in definition and in dict
            stateVarDef.role = RoleStateVariable
            self.stateVariables[node.attrName] = stateVarDef



    def findParameters(self):
        '''Search for parameters (in the new procress) and return a dict'''
        #attrDef = NodeAttrDef()
        paramDict = {}
        #iterate over all nodes in the syntax tree and search for variable accesses
        for name, attrDef in self.processAttributes.iteritems():
            #we only want to see parameters
            if attrDef.role != RoleParameter:
                continue
            #put parameter definition in dict
            paramDict[name] = attrDef
        return paramDict



    def isPossibleParamPropagation(self, highParam, lowParam):
        '''
        Test for parameter propagation

        Example:
          propagate: mu   --> m1.mu, m2.mu
          propagate: m1.l --> m1.sm1.l, m1.sm2.l
          no       : m1.l --> m2.l, l

        Arguments:
            highParam : tuple of strings
            lowParam  : tuple of strings
        Return:
            True if propagation is possible.
            False otherwise.
        '''
        #name of high level parameter must be shorter (otherwise it
        #is not from higher level)
        if not (len(highParam) < len(lowParam)):
            return False
        #last parts of names must be same. (Propagate to parameters of same
        #name, but at lower level in hierarchy)
        if not (highParam[-1] == lowParam[-1]):
            return False
        #both parameters must start with same sequence
        #(both parameters must be from the same branch in the hierarchy)
        for i in range(0, len(highParam)-1):
            if not (highParam[i] == lowParam[i]):
                return False
        return True



    def propagateParameters(self, initMethod):
        '''
        Propagate parameter values from models high in the hierarchy to their
        sub-models. Both conditions must be true, for Parameter propagation to
        happen:
        1.: Both parameters have the same name (in high level model and in
            child model)
        2.: Parameter is not initialized in child model

        This is currently done by deleting parameters in the child models
        and accessing parameters in the high level models instead.

        Arguments:
            initMethod : Definition of init method in ILT; for identifying
                         those parameters that are initialized
        Output:
            Deletes parameters;
            changes attribute accessors, in whole process.
        '''
        parameters = self.findParameters()
        #classify parameters in: 1. explicitly initialized, 2. not initialized
        initedParams = set()
        for assignStmt in initMethod.iterDepthFirst():
            #we only want to look at assignments
            if not isinstance(assignStmt, NodeAssignment):
                continue
            #those assignments must assign values to parameters
            accPar = assignStmt.lhs
            if not accPar.attrName in parameters:
                continue
            #OK, this parameter is initialized, remember it
            initedParams.add(accPar.attrName)
        notInitedParams = set(parameters.keys()) - initedParams

        #for each initialized parametr: search for not initialized Parameter
        #to which the value can be propagated. (that has same name but is
        #deeper in the model hierarchy.)
        #Example:
        #  propagate: mu   --> m1.mu, m2.mu
        #  propagate: m1.l --> m1.sm1.l, m1.sm2.l
        #  no       : m1.l --> m2.l, l
        initedParams = list(initedParams)
        #start with the names with the most dots (defined deep in submodels)
        initedParams.sort(key=len, reverse=True)
        paramReplaceDict = {}
        for iPar in initedParams:
            for nPar in notInitedParams.copy():
                if self.isPossibleParamPropagation(iPar, nPar):
                    #we found parameter to rename
                    paramReplaceDict[nPar] = iPar #remember rename action
                    notInitedParams.remove(nPar)  #we cared for this parameter
        #print paramReplaceDict

        #raise error for all still uninitialized parameters
        if len(notInitedParams) > 0:
            msg = 'In process %s' % self.astProcess.className
            loc = self.astProcess.loc
            errList = [(msg, loc)]
            #mention all uninited params
            for nPar in notInitedParams:
                msg = 'Uninitialized prameter: %s' % str(parameters[nPar].attrName)
                loc = parameters[nPar].loc
                errList.append((msg, loc))
            raise MultiErrorException(errList)

        #rename all attribute accesses according to paramReplaceDict
        for accPar in self.process.iterDepthFirst():
            if not isinstance(accPar, NodeAttrAccess):
                continue
            oldParamName = accPar.attrName
            if not oldParamName in paramReplaceDict:
                continue
            accPar.attrName = paramReplaceDict[oldParamName]

        #delete replaced parameters
        for i in range(len(self.process)-1, -1, -1): #iterate backwards
            defPar = self.process[i]
            if not isinstance(defPar, NodeAttrDef):
                continue
            parName = defPar.attrName
            if not parName in paramReplaceDict:
                continue
            del self.process[i]
            self.processAttributes.pop(parName)


    def checkDynamicMethodConstraints(self, block):
        '''See if the method is a valid dynamic method.'''
        #iterate over all nodes in the syntax tree and search for assignments
        for node in block.iterDepthFirst():
            if not isinstance(node, NodeAssignment):
                continue
            lVal = node.lhs #must be NodeValAccess
            lValDef = self.processAttributes[lVal.attrName]
            #No assignment to parameters
            if lValDef.role == RoleParameter:
                raise UserException('Illegal assignment to parameter: ' +
                                    str(lVal.attrName), lVal.loc)
            #No assignment to state variables - only to their time derivatives
            if lValDef.role == RoleStateVariable and (lVal.deriv != ('time',)):
                raise UserException('Illegal assignment to state variable: ' +
                                    str(lVal.attrName) +
                                    '. You must however assign to its time derivative. ($' +
                                    str(lVal.attrName) +')', lVal.loc)


    def checkInitMethodConstraints(self, block):
        '''See if the method is a valid init method.'''
        #iterate over all nodes in the syntax tree and search for variable accesses
        for node in block.iterDepthFirst():
            if not isinstance(node, NodeAttrAccess):
                continue
            #$ operators are illegal in init method
            if node.deriv == ('time',):
                raise UserException('Time derivation illegal in init: ' +
                                    str(node.attrName), node.loc)


    def modifyInitMethod(self, method):
        '''
        Modify init function for parameter value overriding
        
        Assignments to parameters are changed. The built in 
        function 'overrideParam' is inserted:
        par1 = 5; ---> par1 = overrideParam('par1', 5);
        
        Override param looks into an overide dict and may return
        a new value for the parameter if it finds one in the 
        override dict. Otherwise it returns the original value.
        '''
        parameters = self.findParameters() 
        for assign in method.iterDepthFirst():
            #we only want to see assignments
            if not isinstance(assign, NodeAssignment):
                continue
            #the assignment must be to a parameter
            paramName = assign.lhs.attrName
            if not paramName in parameters:
                continue
            #OK: this is an assignment to a parameter
            loc = assign.loc
            #create the helper function for parameter overriding
            funcNode = NodeBuiltInFuncCall([], loc, 'overrideParam')
            paramNameNode = NodeString([], loc, str(paramName))
            origExprNode = assign.rhs
            funcNode.appendChild(paramNameNode)
            funcNode.appendChild(origExprNode)
            #use helper function as new rhs
            assign.rhs = funcNode
            
            
    def createProcess(self, inAstProc):
        '''generate ILT subtree for one process'''
        #store original process
        self.astProcess = inAstProc.copy()
        #init new process
        self.process = NodeClassDef()
        self.process.className = self.astProcess.className
        self.process.superName = self.astProcess.superName
        self.process.loc = self.astProcess.loc
        #init quick reference dicts
        self.processAttributes = {}
        self.astProcessAttributes = {}
        self.stateVariables = {}

        #add some built in attributes to the AST process
        #this will be gone once inheritance is implemented
        self.addBuiltInParameters()
        #discover all attributes
        self.findAttributesRecursive(self.astProcess, tuple())
        #create the new process' data attributes
        self.copyDataAttributes()

        #dynamic(...), init(...), final(...) are the prosess' main functions.
        #if they are not defined an empty function is created
        principalFuncs = set([DotName('dynamic'), DotName('init'),
                              DotName('final')])
        #create dynamic function
        dynamicFunc = NodeFuncDef(name=DotName('dynamic')) #create empty function
        self.process.appendChild(dynamicFunc) #put new function into process
        #if function is defined in the AST, copy it into the new ILT function
        if DotName('dynamic') in self.astProcessAttributes:
            #set of functions that should not appear in dynamic function
            illegalFuncs = principalFuncs - set([DotName('dynamic')]) \
                           | set([DotName('load'), DotName('store'), 
                                  DotName('graph',)])
            #copy the function's statements from AST to ILT; recursive
            self.copyFuncRecursive(self.astProcessAttributes[DotName('dynamic')],
                                   DotName(), dynamicFunc, illegalFuncs)
        #create init function
        initFunc = NodeFuncDef(name=DotName('init'))
        self.process.appendChild(initFunc) #put new block into process
        if DotName('init') in self.astProcessAttributes:
            illegalFuncs = principalFuncs - set([DotName('init')])
            self.copyFuncRecursive(self.astProcessAttributes[DotName('init')],
                                   DotName(), initFunc, illegalFuncs)
        #create final function
        finalFunc = NodeFuncDef(name=DotName('final'))
        self.process.appendChild(finalFunc) #put new block into process
        if DotName('final') in self.astProcessAttributes:
            illegalFuncs = principalFuncs - set([DotName('final')])
            self.copyFuncRecursive(self.astProcessAttributes[DotName('final')],
                                   DotName(), finalFunc, illegalFuncs)

        self.checkUndefindedReferences(self.process) #Check undefined refference
        self.findStateVariables(dynamicFunc) #Mark state variables
        self.propagateParameters(initFunc) #rename some parameters
        self.checkDynamicMethodConstraints(dynamicFunc)
        self.checkInitMethodConstraints(initFunc)

        #TODO: Check correct order of assignments (or initialization).
        #TODO: Check if all parameters and state vars have been initialized.
        #TODO: Check if any variable name is equal to a keyword. (in findAttributesRecursive)
        
        #Modify init function for parameter value overriding
        self.modifyInitMethod(initFunc)
        
        return self.process



class ILTGenerator(object):
    '''
    Generate a tree that represents the intermediate language.
    intermediate language tree (ILT)
    '''

    def __init__(self):
        super(ILTGenerator, self).__init__()


    def addBuiltInClasses(self, astRoot):
        '''
        Some classes exist without beeing defined; create them here.

        -This method could be expanded into a more general mechanism for
         built-in values and functions, like pi, sin(x).
        '''
        #Create the solution parameters' definition
        solPars = NodeClassDef(loc=0, 
                               className=DotName('solutionParametersClass'),
                               superName=DotName('Model'))
        solPars.appendChild(NodeAttrDef(loc=0, 
                                        attrName=DotName('simulationTime'),
                                        className=DotName('Real'), 
                                        role=RoleParameter))
        solPars.appendChild(NodeAttrDef(loc=0, 
                                        attrName=DotName('reportingInterval'),
                                        className=DotName('Real'), 
                                        role=RoleParameter))
        #add solutionparameTers to AST, and update class dict
        astRoot.insertChild(0, solPars)


    def createIntermediateTree(self, astRoot):
        '''generate ILT tree from AST tree'''
        #add built ins to AST
        self.addBuiltInClasses(astRoot)
#        #possible replacements in ech class of ast
#        self.replaceMultiAttributeDefinitions(astRoot)
#        print astRoot
        #create ILT root node
        iltRoot = NodeProgram()
        iltRoot.loc = astRoot.loc

        procGen = ILTProcessGenerator(astRoot)
        #search for processes in the AST and instantiate them in the ILT
        for processDef in astRoot:
            if ((not isinstance(processDef, NodeClassDef)) or
                (not processDef.superName == DotName('Process'))):
                continue
            newProc = procGen.createProcess(processDef)
            iltRoot.appendChild(newProc)
        #warnig if no code was generated
        if len(iltRoot) == 0:
            print 'Warnig: program contains no "Process" objects. ' + \
                  'No simulation code is generated.'    
        
        return iltRoot



def doTests():
    '''Perform various tests.'''

    #t1 = Node('root', [Node('child1',[]),Node('child2',[])])
    #print t1

#------------ testProg1 -----------------------
    testProg1 = (
'''
class Test(Model):
    data V, h: Real;
    data A_bott, A_o, mu, q, g: Real parameter;

    func dynamic():
        h = V/A_bott;
        $V = q - mu*A_o*sqrt(2*g*h);
        print 'h: ', h,;
    end

    func init():
        V = 0;
        A_bott = 1; A_o = 0.02; mu = 0.55;
        q = 0.05;
    end
end

class RunTest(Process):
    data g: Real parameter;
    data test: Test;

    func dynamic():
        call test.dynamic();
    end

    func init():
        g = 9.81;
        call test.init();
        solutionParameters.simulationTime = 100;
        solutionParameters.reportingInterval = 1;
    end
    func final():
        #store;
        graph test.V, test.h;
        print 'Simulation finished successfully.';
    end
end
''' )


    #test the intermedite tree generator ------------------------------------------------------------------
    flagTestILTGenerator = True
    #flagTestILTGenerator = False
    if flagTestILTGenerator:
        parser = ParseStage()
        iltGen = ILTGenerator()

        astTree = parser.parseProgramStr(testProg1)
        print 'AST tree:'
        print astTree

        iltTree = iltGen.createIntermediateTree(astTree)
        print 'ILT tree:'
        print iltTree


    #test the parser ----------------------------------------------------------------------
    #flagTestParser = True
    flagTestParser = False
    if flagTestParser:
        parser = ParseStage()
        #ParseStage.debugSyntax = 1
        #ParseStage.debugSyntax = 2
        #print parser.parseProgram('model test var a; par b; end')
        #print parser.parseProgram('model test par a; end')


        #print parser.parseProgram(testProg2)

        print parser.parseProgramStr(testProg1)
        #print parser.parseProgram('if a==0 then b=-1; else b=2+3+4; a=1; end')
        #print parser.parseExpression('0*1*2*3*4').asList()[0]
        #print parser.parseExpression('0^1^2^3^4')
        #print parser.parseExpression('0+1*2+3+4').asList()[0]
        #print parser.parseExpression('0*1^2*3*4')
        #print parser.parseExpression('0+(1+2)+3+4')
        #print parser.parseExpression('-0+1+--2*-3--4')
        #print parser.parseExpression('-aa.a+bb.b+--cc.c*-dd.d--ee.e+f').asList()[0]
        #print parser.parseExpression('time+0+sin(2+3*4)+5').asList()[0]
        #print parser.parseExpression('0+a1.a2+bb.b1.b2+3+4 #comment')
        #print parser.parseExpression('0.123+1.2e3')
        #parser.parseExpression('0+1*2^3^4+5+6*7+8+9')

        print 'keywords:'
        print parser.keywords


##    pdb.set_trace()


if __name__ == '__main__':
    # Self-testing code goes here.
    #TODO: add unit tests
    #TODO: add doctest tests. With doctest tests are embedded in the documentation

    doTests()
else:
    # This will be executed in case the
    #    source has been imported as a
    #    module.
    pass
