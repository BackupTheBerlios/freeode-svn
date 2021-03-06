#***************************************************************************
#    Copyright (C) 2006 by Eike Welk                                       *
#    eike.welk@post.rwth-aachen.de                                         *
#                                                                          *
#    Inspiration came from:                                                *
#    'fourFn.py', an example program, by Paul McGuire                      *
#    and the 'Spark' library by John Aycock                                *
#                                                                          *
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

__doc__ = \
'''
Parser for the SIML simulation language.
'''
#TODO: usage (above)


#import pprint #pretty printer
#import pdb    #debuber

from pyparsing import Literal,CaselessLiteral,Keyword,Word,Combine,Group,Optional, \
    ZeroOrMore,OneOrMore,Forward,nums,alphas,restOfLine,ParseResults,  \
    ParseFatalException, StringEnd # ParseException,

from ast import *


#pp = pprint.PrettyPrinter(indent=4) 



class ParseActionException(Exception):
    '''Exception raised by the parse actions of the parser'''
    pass



class ParseStage(object):
    '''
    The syntax definition (BNF) resides here.
    Mainly a wrapper for the Pyparsing library and therefore combines lexer
    and parser. The Pyparsing library generates a ParseResult object which is
    modfied through parse actions by this class.

    The program is entered as a string.
    The parse* methods return a tree of Node objects; the abstract syntax 
    tree (AST)

    Usage:
    parser = ParseStage()
    result = parser.parseExpression('0+1+2+3+4')
    result = parser.parseProgram(inString)
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
        self._expressionParser = None
        '''The parser object from pyParsing'''
        self._defineLanguageSyntax() #Create parser object


    def defineKeyword(self, inString):
        '''
        Store keyword (in ParseStage.keywords) and create parser for it.
        Use this function (in _defineLanguageSyntax(...)) instead of using the
        Keyword class directly.
        '''
        ParseStage.keywords.add(inString)
        return Keyword(inString)


#------------- Parse Actions -------------------------------------------------*
    def _actionDebug(self, str, loc, toks):
        '''Parse action for debuging.'''
        print '------debug action'
        print str
        print loc
        print toks
        print '-------------------'
        return toks


    def _actionCheckIdentifier(self, str, loc, toks):
        '''
        Parse action to check an identifier.
        Tries to see wether it is equal to a keyword.
        Does not change any parse results
        '''
        #toks is structured like this: ['a1']
        if toks[0] in self.keywords:
            #print 'found keyword', toks[0], 'at loc: ', loc
            #raise ParseException(str, loc, 'Identifier same as keyword: %s' % toks[0])
            raise ParseFatalException(
                str, loc, 'Identifier same as keyword: %s' % toks[0] )


    def _actionBuiltInValue(self, str, loc, toks):
        '''
        Create AST node for a built in value: pi, time
        tokList has the following structure:
        [<identifier>]
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        #create AST node
        nCurr = NodeBuiltInVal()
        nCurr.loc = loc #Store position 
        nCurr.dat = tokList[0] #Store the built in value's name
        return nCurr
    
    
    def _actionNumber(self, str, loc, toks):
        '''
        Create node for a number: 5.23
        tokList has the following structure:
        [<number>]
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeNum()
        nCurr.loc = loc #Store position 
        nCurr.dat = tokList[0] #Store the number
        return nCurr    
    
    
    def _actionFunctionCall(self, str, loc, toks):
        '''
        Create node for function call: sin(2.1)
        tokList has the following structure:
        [<function dentifier>, '(', <expression>, ')']
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeBuiltInFuncCall()
        nCurr.loc = loc #Store position 
        nCurr.dat = tokList[0]  #function dentifier
        nCurr.kids=[tokList[2]] #child expression
        return nCurr


    def _actionParenthesesPair(self, str, loc, toks):
        '''
        Create node for a pair of parentheses that enclose an expression: (...)
        tokList has the following structure:
        ['(', <expression>, ')']
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeParentheses()
        nCurr.loc = loc #Store position 
        nCurr.kids = [tokList[1]] #store child expression
        return nCurr


    def _actionPrefixOp(self, str, loc, toks):
        '''
        Create node for math prefix operators: -
        tokList has the following structure:
        [<operator>, <expression_l>]
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeOpPrefix1()
        nCurr.loc = loc #Store position 
        nCurr.dat = tokList[0]  #Store operator
        nCurr.kids=[tokList[1]] #Store child tree
        return nCurr


    def _actionInfixOp(self, str, loc, toks):
        '''
        Create node for math infix operators: + - * / ^
        tokList has the following structure:
        [<expression_l>, <operator>, <expression_r>]
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeOpInfix2()
        nCurr.loc = loc #Store position 
        #create children and store operator
        lhsTree = tokList[0]   #child lhs
        nCurr.dat = tokList[1] #operator
        rhsTree = tokList[2]   #child rhs
        nCurr.kids=[lhsTree, rhsTree]
        return nCurr


    def _actionAttributeAccess(self, str, loc, toks):
        '''
        Create node for acces to a variable or parameter: bb.ccc.dd
        tokList has the following structure:
        [<part1>, <part2>, <part3>, ...]
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeAttrAccess()
        nCurr.loc = loc #Store position 
        #Look if there is a '$' that indicates time derivatives
        if tokList[0] == '$':
            nCurr.deriv = ('time',)
            del tokList[0]
        #The remaining tokens are the dot separated name
        nCurr.attrName = tuple(tokList)
        return nCurr


    def _actionIfStatement(self, str, loc, toks):
        '''
        Create node for if - then - else statement.
        BNF:
        ifStatement = Group(
                    kw('if') + boolExpression + kw('then') +
                    statementList +
                    Optional(kw('else') + statementList) +
                    kw('end'))
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeIfStmt()
        nCurr.loc = loc #Store position 
        #if ... then ... end
        if len(tokList) == 5:
            condition = tokList[1]
            thenStmts = tokList[3]
            nCurr.kids=[condition, thenStmts]
        #if ... then ... else ... end
        elif len(tokList) == 7:
            condition = tokList[1]
            thenStmts = tokList[3]
            elseStmts = tokList[5]
            nCurr.kids=[condition, thenStmts, elseStmts]
        else:
            raise ParseActionException('Broken >if< statement! loc: ' + str(nCurr.loc))
        return nCurr


    def _actionAssignment(self, str, loc, toks):
        '''
        Create node for assignment: a := 2*b
        BNF:
        assignment = Group(valAccess + ':=' + expression + ';')
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeAssignment()
        nCurr.loc = loc #Store position 
        #create children and store operator
        lhsTree = tokList[0]   #child lhs
        nCurr.dat = tokList[1] #operator
        rhsTree = tokList[2]   #child rhs
        nCurr.kids=[lhsTree, rhsTree]
        return nCurr


    def _createBlockExecute(self, str, loc, toks):
        '''
        Create node for execution of a block (insertion of the code): run foo
        BNF:
        blockName = kw('run') | kw('init') #| kw('insert')
        blockExecute = Group(blockName + subModelName + ';')
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeBlockExecute()
        nCurr.loc = loc #Store position 
        nCurr.blockName = tokList[0]    #block name - operator
        nCurr.subModelName = tokList[1] #Name of model from where block is taken
        return nCurr


    def _actionStatementList(self, str, loc, toks):
        '''
        Create node for list of statements: a:=1; b:=2; ...
        BNF:
        statementList << Group(OneOrMore(statement))
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeStmtList()
        nCurr.loc = loc #Store position 
        #create children - each child is a statement
        for tok in tokList:
            nCurr.kids.append(tok)
        return nCurr


    def _actionAttrDefinition(self, str, loc, toks):
        '''
        Create node for defining parameterr, variable or submodel: var foo;
        BNF:
        defRole = kw('par') | kw('var') | kw('sub') 
        attributeDef = Group(defRole + identifier + 
                             Optional(kw('as') + identifier + ';'))
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeAttrDef()
        nCurr.loc = loc #Store position 
        #These are aways present
        roleStr = tokList[0]                    #var, par, sub
        #TODO: change attrName into tuple(tokList[1]) ?
        nCurr.attrName = tokList[1] #identifier; name of the attribute
        #attribute is a submodel
        if roleStr == 'sub':
            nCurr.className = tokList[3]
            nCurr.isSubmodel = True
            nCurr.role = None
        #attribute is a variable or parameter
        else:
            nCurr.className = 'Real'
            nCurr.isSubmodel = False
            nCurr.isStateVariable = False
            nCurr.role = roleStr
        return nCurr


    def _actionBlockDefinition(self, str, loc, toks):
        '''
        Create node for definition of a block: block run a:=1; end
        BNF:
        runBlock = Group(   kw('block') + blockName +
                            OneOrMore(statement) + 
                            kw('end'))
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeBlockDef()
        nCurr.loc = loc #Store position 
        #store name of block 
        nCurr.name = tokList[1]
        #create children - each child is a statement
        for tok in tokList[2:len(tokList)-1]:
            nCurr.kids.append(tok)
        return nCurr


    def _actionClassDef(self, str, loc, toks):
        '''
        Create node for definition of a class: model foo ... end
        BNF:
        classRole = kw('process') | kw('model') #| kw('paramset')
        classDef = Group(   classRole + identifier +
                            OneOrMore(attributeDef) +
                            Optional(runBlock) +
                            Optional(initBlock)  +
                            kw('end'))
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeClassDef()
        nCurr.loc = loc #Store position 
        #store role and class name - these are always present
        nCurr.role = tokList[0]
        nCurr.className = tokList[1]
        #create children (may or may not be present):  definitions, run block, init block
        for tok in tokList[2:len(tokList)-1]:
            nCurr.kids.append(tok)
        return nCurr


    def _actionProgram(self, str, loc, toks):
        '''
        Create the root node of a program.
        BNF:
        program = Group(OneOrMore(classDef))
        '''
        if self.noTreeModification:
            return None #No parse result modifications for debuging
        tokList = toks.asList()[0] #asList() ads an extra pair of brackets
        nCurr = NodeProgram()
        nCurr.loc = loc #Store position 
        #create children - each child is a class
        for tok in tokList:
            nCurr.kids.append(tok)
        return nCurr


#------------------- BNF --------------------------------------------------------*
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
        #TODO: this should be a for loop and a list (attribute)!
        builtInValue = Group( kw('pi') | kw('time'))                .setParseAction(self._actionBuiltInValue)\
                                                                    .setName('builtInValue')#.setDebug(True)

        #Functions that are built into the language
        #TODO: this should be a for loop and a list (attribute)!
        builtInFuncName = (  kw('sin') | kw('cos') | kw('tan') |
                             kw('sqrt') | kw('exp') | kw('ln')   )  .setName('builtInFuncName')#.setDebug(True)

        #Integer (unsigned).
        uInteger = Word(nums)                                       .setName('uInteger')#.setDebug(True)
        #Floating point number (unsigned).
        eE = CaselessLiteral( 'E' )
        uNumber = Group( Combine(
                    uInteger +
                    Optional('.' + Optional(uInteger)) +
                    Optional(eE + Word('+-'+nums, nums))))          .setParseAction(self._actionNumber)\
                                                                    .setName('uNumber')#.setDebug(True)

        # .............. Mathematical expression .............................................................
        #'Forward declarations' for recursive rules
        expression = Forward()
        term =  Forward()
        factor = Forward()
        signedAtom = Forward()
        valAccess = Forward() #For PDE: may also contain expressions for slices: a.b.c(2.5:3.5)

        #Basic building blocks of mathematical expressions e.g.: (1, x, e,
        #sin(2*a), (a+2), a.b.c(2.5:3.5))
        #Function call, parenthesis and memory access can however contain
        #expressions.
        funcCall = Group( builtInFuncName + '(' + expression + ')') .setParseAction(self._actionFunctionCall) \
                                                                    .setName('funcCall')#.setDebug(True)
        parentheses = Group('(' + expression + ')')                 .setParseAction(self._actionParenthesesPair) \
                                                                    .setName('parentheses')#.setDebug(True)
        atom = (    uNumber | builtInValue | funcCall |
                    valAccess | parentheses               )         .setName('atom')#.setDebug(True)

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
        #FIXME: expressions with ond, or, ... don't work
        relop = L('<') | L('>') | L('<=') | L('>=') | L('==')
        boolExpression = Group(expression + relop + expression) .setParseAction(self._actionInfixOp) \
                                                                .setName('expression2')#.setDebug(True)
        #................ End mathematical expression ................................................---

        #................ Identifiers ...................................................................
        #TODO: check for keywods -  .setParseAction(self.actionCheckIdentifier) \
        identifier = Word(alphas, alphas+nums+'_')              .setName('identifier')#.setDebug(True)

        #Compound identifiers for variables or parameters 'aaa.bbb'.
        #TODO: add slices: aaa.bbb(2:3)
        dotSup = Literal('.').suppress()
        valAccess << Group( Optional('$') +
                            identifier +
                            ZeroOrMore(dotSup  + identifier) )  .setParseAction(self._actionAttributeAccess) \
                                                                .setName('valAccess')#.setDebug(True)

        #..................... Statements ..............................................................
        statementList = Forward()
        #Flow control - if then else
        ifStatement = Group(
                        kw('if') + boolExpression + kw('then') +
                        statementList +
                        Optional(kw('else') + statementList) +
                        kw('end'))                                  .setParseAction(self._actionIfStatement)\
                                                                    .setName('ifStatement')#.setDebug(True)
        #compute expression and assign to value
        assignment = Group(valAccess + ':=' + expression + ';')     .setParseAction(self._actionAssignment)\
                                                                    .setName('assignment')#.setDebug(True)
        #execute a block - insert code of a child model
        blockName = kw('run') | kw('init') #| kw('insert')
        blockExecute = Group(blockName + identifier + ';')          .setParseAction(self._createBlockExecute)\
                                                                    .setName('blockExecute')#.setDebug(True)

        statement = (blockExecute | ifStatement | assignment)       .setName('statement')#.setDebug(True)
        statementList << Group(OneOrMore(statement))                .setParseAction(self._actionStatementList)\
                                                                    .setName('statementList')#.setDebug(True)

#---------- Class Def ---------------------------------------------------------------------*
        #define parameters, variables and submodels
        defRole = kw('par') | kw('var') | kw('sub') 
        attributeDef = Group(defRole + identifier + 
                             Optional(kw('as') + identifier) + ';') .setParseAction(self._actionAttrDefinition)\
                                                                    .setName('attributeDef')#.setDebug(True)
        #Note: For the AST this is also a statementList-'stmtList'
#        definitionList = Group(OneOrMore(attributeDef))             .setParseAction(AddMetaDict('stmtList'))\
#                                                                    .setName('definitionList')#.setDebug(True)

        #The statements (equations) that determine the system dynamics go here
        runBlock = Group(   kw('block') + kw('run') +
                            #statementList +
                            OneOrMore(statement) + 
                            kw('end'))                              .setParseAction(self._actionBlockDefinition)\
                                                                    .setName('runBlock')#.setDebug(True)

        #The initialization code goes here
        initBlock = Group(  kw('block') + kw('init') +
                            #statementList +
                            OneOrMore(statement) + 
                            kw('end'))                              .setParseAction(self._actionBlockDefinition)\
                                                                    .setName('initBlock')#.setDebug(True)

        classRole = kw('process') | kw('model') #| kw('paramset')
        classDef = Group(   classRole + identifier +
                            #Optional(definitionList) +
                            OneOrMore(attributeDef) +
                            Optional(runBlock) +
                            Optional(initBlock)  +
                            #TODO: Optional(finalBlock)  + #Method where graphs are displayed and vars are stored
                            kw('end'))                              .setParseAction(self._actionClassDef)\
                                                                    .setName('classDef')#.setDebug(True)

        program = Group(OneOrMore(classDef))                        .setParseAction(self._actionProgram)\
                                                                    .setName('program')#.setDebug(True)
        
        #special rule against incomplete parsing and faillure without error message
        file = program + StringEnd()
        #................ End of language definition ..................................................

        #determine start symbol
        startSymbol = file
        #set up comments
        singleLineCommentCpp = '//' + restOfLine
        singleLineCommentPy = '#' + restOfLine
        startSymbol.ignore(singleLineCommentCpp)
        startSymbol.ignore(singleLineCommentPy)
        #store parsers
        self._parser = startSymbol
        self._expressionParser = expression
        
    
    def parseExpression(self, inString):
        '''Parse a single expression. Example: 2*a+b'''
        return self._expressionParser.parseString(inString).asList()[0]


    def parseProgram(self, inString):
        '''Parse a whole program. The program is entered as a string.'''
        result = self._parser.parseString(inString).asList()[0]
        #TODO: store loc of last parsed statement; for error message generation.
        return result



#class AddMetaDict(object):
#    '''
#    Functor class to add a dict to a ParseResults object in a semantic action.
#    The meta dict contains (at least) the result's type and the location in the
#    input string:
#    {'typ':'foo', 'loc':23}
#
#    Additionally adds type string to a central list
#    (ParseStage.nodeTypes - really a set) for checking the consistency
#    '''
#    def __init__(self, typeString):
#        '''typeString : string to identify the node.'''
#        object.__init__(self)
#        self.typeString = typeString
#         #add to set of known type strings
#        ParseStage.nodeTypes.add(typeString)
#
#
#    def __call__(self,str, loc, toks):
#        '''The parse action that adds the dict.'''
#        #debug code-----------------
#        if   ParseStage.noTreeModification == 2:
#            return None
#        elif ParseStage.noTreeModification == 1:
#            return toks.copy()
#
#        #toks is structured like this [['pi']]
#        newToks = ParseResults([{'typ':self.typeString, 'loc':loc}]) #create dict
#        newToks += toks[0].copy() #add original contents
#        return ParseResults([newToks]) #wrap in []; return.



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
        
        #populate self.classes and self.processes 
        self.findClassesInAst()

    
    def findClassesInAst(self):
        '''
        Extract all class definitions from the ast and put them into self.classes.
        Additionally the process definitions go into self.processes.
        '''
        for classDef in self.astRoot:
            self.astClasses[classDef.className] = classDef
                

    def addBuiltInParameters(self):
        '''
        Some parameters exist without beeing defined; create them here.
        
        -In a later stage they could be inherited from a base class.
        -This method could be expanded into a more general mechanism for 
         built-in values, like pi.
        '''
        #Put solutionparameters as first attribute into the process
        solParAttr = NodeAttrDef(loc=0, attrName='solutionParameters', 
                                 className='solutionParametersClass',
                                 isSubmodel=True)
        self.astProcess.insertChild(0, solParAttr)
        
        
    def findAttributesRecursive(self, astClass, namePrefix):
        '''
        Find all of the process' attributes (recursing into the sub-models)
        and put then into self.astProcessAttributes.
        
        Attributes are: parameters, variables, sub-models, and functions.
        The definition in the AST is searched NOT the new process.
        
        Arguments:
            astClass   : class definition from the AST
            namePrefix : tuple of strings. Prefix for the dotted name of the 
                         class' attributes.
        Output: 
            self.astProcessAttributes : dict: {('mod1', 'var1'):NodeAttrDef} 
        '''
        #each of the class' children is a definition
        for attrDef in astClass:
            #get attribute name
            if isinstance(attrDef, NodeAttrDef): #definition of data attribute or submodel
                attrName = attrDef.attrName
            elif isinstance(attrDef, NodeBlockDef): #definition of block (function)
                attrName = attrDef.name
            else:
                raise ILTGenException('Unknown Node.' + repr(attrDef))
            #prepend prefix to attribute name 
            longAttrName = namePrefix + (attrName,)
            #Check redefinition
            if longAttrName in self.astProcessAttributes:
                raise UserException('Redefinition of: ' + makeDotName(longAttrName), attrDef.loc)
            #put new attribute into dict.
            self.astProcessAttributes[longAttrName] = attrDef
            
            #recurse into submodel, if definition of submodel 
            if isinstance(attrDef, NodeAttrDef) and attrDef.isSubmodel:                
                #User visible error if class does not exist
                if not attrDef.className in self.astClasses:
                    raise UserException('Undefined class: ' + attrDef.className, attrDef.loc)
                subModel = self.astClasses[attrDef.className]
                self.findAttributesRecursive(subModel, longAttrName)
        
        
    def copyDataAttributes(self):
        '''
        Copy variables and parameters from all submodels into the procedure
        Additionaly puts all attributes into self.processAttributes
        arguments:
        '''
        #Iterate over the (variable, parameter, submodel, function) definitions
        for longName, defStmt in self.astProcessAttributes.iteritems():
            #we only care for data attributes
            if (not isinstance(defStmt, NodeAttrDef)) or defStmt.isSubmodel:
                continue
            newAttr = defStmt.copy() #copy definition, 
            newAttr.attrName = longName #exchange name with long name (a.b.c)
            self.process.appendChild(newAttr) #put new attribute into ILT process
            self.processAttributes[longName] = newAttr #and into quick access dict
        return
       
       
    def copyBlockRecursive(self, block, namePrefix, newBlock, allowedBlocks):
        '''
        Copy block into newBlock recursively. 
        Copies all statements of block and all statements of blocks that are 
        executed in this block, recursively.
            block          : A block definition 
            namePrefix     : a list of strings. prefix for all variable names.
            newBlock       : the statements are copied here
            allowedBlocks  : ['run'] or ['init']
        '''
        for statement in block:
            #Block execution statement: include the called blocks variables
            if isinstance(statement, NodeBlockExecute):
                subModelName = namePrefix + [statement.subModelName]
                subBlockName = subModelName + [statement.blockName]
                #Error if submodel or method does not exist
                if not tuple(subModelName) in self.astProcessAttributes:
                    raise UserException('Undefined submodel: ' + 
                                        str(subModelName), statement.loc)
                if not tuple(subBlockName) in self.astProcessAttributes:
                    raise UserException('Undefined method: ' + 
                                        str(subBlockName), statement.loc)
                #Check if executing (inlining) this block is allowed
                if not (statement.blockName in allowedBlocks):
                    raise UserException('Method can not be executed here: ' + 
                                        str(statement.blockName), statement.loc)
                #find definition of method, and recurse into it.
                subBlockDef = self.astProcessAttributes[tuple(subBlockName)] 
                self.copyBlockRecursive(subBlockDef, subModelName, newBlock, allowedBlocks)
            #Any other statement: copy statement
            else:
                newStmt = statement.copy()
                #put prefix before all varible names in new Statement
                for var in newStmt.iterDepthFirst():
                    if not isinstance(var, NodeAttrAccess):
                        continue
                    newAttrName = tuple(namePrefix) + var.attrName
                    var.attrName = tuple(newAttrName)
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
                                    makeDotName(node.attrName), node.loc)



    def findStateVariables(self, dynamicMethod):
        '''
        Search for variables with a $ and mark them:
            1.: in their definition set isStateVariable = True
            2.: put them into self.stateVariables.
        Arguments:
            dynamicMethod : method definition that is searched (always the 
                            dynamic/run method)
        output:
            self.stateVariables    : dict: {('a','b'):NodeAttrDef(...)}
            definition of variable : isStateVariable = True if variable is 
                                     state variable
        '''
        #iterate over all nodes in the syntax tree and search for variable accesses
        for node in dynamicMethod.iterDepthFirst():
            if not isinstance(node, NodeAttrAccess):
                continue
            #State variables are those that have time derivatives
            if node.deriv != ('time',):
                continue
            
            #get definition of variable 
            stateVarDef = self.processAttributes[node.attrName]
            #Check conceptual constraint: no $parameter allowed
            if stateVarDef.role == 'par':
                raise UserException('Parameters can not be state variables: ' +
                              makeDotName(node.attrName), node.loc)
            #remember: this is a state variable; in definition and in dict
            stateVarDef.isStateVariable = True
            self.stateVariables[node.attrName] = stateVarDef
    
    
    
    def findParameters(self):
        '''Search for parameters (in the new procress) and return a dict'''
        #attrDef = NodeAttrDef()
        paramDict = {}
        #iterate over all nodes in the syntax tree and search for variable accesses
        for name, attrDef in self.processAttributes.iteritems():
            #we only want to see parameters
            if attrDef.role != 'par':
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
            tail   : tuple of strings
            bigSeq : tuple of strings
        Return:
            True if the last elements of bigSeq are equal to tail. 
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
            #we want to look at assignments
            if not isinstance(assignStmt, NodeAssignment):
                continue
            #those assignments must assign values to parameters
            accPar = assignStmt.lhs()
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
                msg = 'Uninitialized prameter: %s' % makeDotName(parameters[nPar].attrName)
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
        for i in range(len(self.process)-1, -1, -1):
            defPar = self.process[i]
            if not isinstance(defPar, NodeAttrDef):
                continue
            parName = defPar.attrName
            if not parName in paramReplaceDict:
                continue
            self.process.delChild(i)
    
    
    
    def checkRunMethodConstraints(self, block):
        '''See if the method is a valid run method.'''
        #iterate over all nodes in the syntax tree and search for assignments
        for node in block.iterDepthFirst():
            if not isinstance(node, NodeAssignment):
                continue
            lVal = node.lhs() #must be NodeValAccess
            lValDef = self.processAttributes[lVal.attrName]
            #No assignment to parameters 
            if lValDef.role == 'par':
                raise UserException('Illegal assignment to parameter: ' + 
                                    makeDotName(lVal.attrName), lVal.loc)
            #No assignment to state variables - only to their time derivatives
            if lValDef.isStateVariable and (lVal.deriv != ('time',)):
                raise UserException('Illegal assignment to state variable: ' + 
                                    makeDotName(lVal.attrName) + 
                                    '. You must however assign to its time derivative. ($' + 
                                    makeDotName(lVal.attrName) +')', lVal.loc)

    
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
        #TODO: All state variables must get initial values
        #TODO: All parameters must get values
    
    
    def createProcess(self, inAstProc):
        '''generate ILT subtree for one process'''
        #store original process
        self.astProcess = inAstProc.copy()
        #init new process
        self.process = NodeClassDef()
        self.process.className = self.astProcess.className
        self.process.role = self.astProcess.role
        #init quick reference dicts
        self.processAttributes = {}
        self.astProcessAttributes = {}
        self.stateVariables = {}
        
        #add some built in attributes to the process
        self.addBuiltInParameters()
        #discover all attributes 
        self.findAttributesRecursive(self.astProcess, tuple())
        #create the new process' data attributes
        self.copyDataAttributes()
        #create the new process' blocks (methods)
        runBlock, initBlock, blockCount = None, None, 0
        for block in self.astProcess:
            if not isinstance(block, NodeBlockDef):
                continue
            #create the new method (block) definition
            newBlock = NodeBlockDef() 
            newBlock.name = block.name
            blockCount += 1 #count the number of blocks
            #determine which methods can be executed in this method
            if block.name == 'run':
                allowedBlocks = ['run'] #list of compatible methods
                runBlock = newBlock     #remember which block is which
            elif block.name == 'init':
                allowedBlocks = ['init']
                initBlock = newBlock
            else:
                raise UserException('Illegal method: ' + str(block.name), 
                                    block.loc)
            #copy the statements, and put new method into new procedure
            self.copyBlockRecursive(block, [], newBlock, allowedBlocks) 
            self.process.kids.append(newBlock) #put new block into process
        
        if (not runBlock) or (not initBlock) or (blockCount != 2):
            raise UserException('Process must contain exactly one run method ' + 
                                'and one init method.', self.astProcess.loc)
        self.checkUndefindedReferences(self.process) #Check undefined refference
        self.findStateVariables(runBlock) #Mark state variables
        self.propagateParameters(initBlock) #rename some parameters
        self.checkRunMethodConstraints(runBlock)
        self.checkInitMethodConstraints(initBlock)
        
        #TODO: Check correct order of assignments (or initialization).
        #TODO: Propagate parameters - only replace those that have not been explicitly initialized.
        #TODO: Check if all parameters and state vars have been initialized.
        
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
        solPars = NodeClassDef(loc=0, name='solutionParametersClass', 
                               role='model')
        solPars.appendChild(NodeAttrDef(loc=0, attrName='simulationTime', 
                                        className='Real', role='par'))
        solPars.appendChild(NodeAttrDef(loc=0, attrName='reportingInterval', 
                                        className='Real', role='par'))
        #add solutionparameTers to AST, and update class dict
        astRoot.insertChild(0, solPars) 


    def createIntermediateTree(self, astRoot):
        '''generate ILT tree from AST tree'''
        #add built ins to AST
        self.addBuiltInClasses(astRoot)
        #create ILT root node
        iltRoot = NodeProgram()
        
        procGen = ILTProcessGenerator(astRoot)
        #searc for processes in the AST and instantiate them in the ILT
        for processDef in astRoot:
            if ((not isinstance(processDef, NodeClassDef)) or 
                (not processDef.role == 'process')):
                continue
            newProc = procGen.createProcess(processDef)
            iltRoot.appendChild(newProc)
        return iltRoot
    
    
    
def doTests():
    '''Perform various tests.'''

    #t1 = Node('root', [Node('child1',[]),Node('child2',[])])
    #print t1

#------------ testProg1 -----------------------
    testProg1 = (
'''
model Test
    var V; var h;
    par A_bott; par A_o; par mu;
    par q; par g;
    
    block run
        h := V/A_bott;
        $V := q - mu*A_o*sqrt(2*g*h);
    end
    
    block init
        V := 0;
        A_bott := 1; A_o := 0.02; mu := 0.55;
        q := 0.05;
    end
end

process RunTest
    par g;
    sub test as Test;
    
    block run
        run test;
    end
    block init
        g := 9.81;
        init test;
        solutionParameters.simulationTime := 100;
        solutionParameters.reportingInterval := 1;
    end
end
''' )

#------------ testProg2 -----------------------
    testProg2 = (
'''
model Test
    var a;

    block run
        $a := 0.5;
    end
    block init
        a := 1;
    end
end

process RunTest
    sub test as Test;
    
    block run
        run test;
    end
    
    block init
        init test;
    end
end 
''' )
    #test the intermedite tree generator ------------------------------------------------------------------
    flagTestILTGenerator = True
    #flagTestILTGenerator = False
    if flagTestILTGenerator:
        parser = ParseStage()
        iltGen = ILTGenerator()
        
        astTree = parser.parseProgram(testProg1)
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

        print parser.parseProgram(testProg1)
        #print parser.parseProgram('if a==0 then b:=-1; else b:=2+3+4; a:=1; end')
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
