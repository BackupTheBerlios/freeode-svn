# -*- coding: utf-8 -*-
#***************************************************************************
#    Copyright (C) 2009 by Eike Welk                                       *
#    eike.welk@post.rwth-aachen.de                                         *
#                                                                          *
#                                                                          *
#    License: GPL                                                          *
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

"""
Optimizer for the output of the interpreter.
"""

from __future__ import division
from __future__ import absolute_import              #IGNORE:W0410

#import copy
import weakref
from weakref import ref
#import math

from freeode.ast import *
from freeode.interpreter import InterpreterObject


#TODO: rename DataFlowDecorator
class DataflowDiscovery(object):
    '''
    Create sets of input and output variables, 
    for all statements and all function calls.
    '''
    
    def __init__(self):
        object.__init__(self)
        self.all_inputs = set()
        self.all_outputs = set()
        
        
        
    def discover_expr_input_variables(self, expr):
        '''Go through an expression, find all input variables'''
        #A variable in an expression is always an input
        if isinstance(expr, InterpreterObject):
            return set([expr])
        #if its a function call recurse for each of its arguments
        elif isinstance(expr, (NodeFuncCall, NodeOpInfix2, NodeOpPrefix1, 
                               NodeParentheses)):
            inputs = set()
            for arg in list(expr.arguments) + expr.keyword_arguments.values():
                arg_inputs = self.discover_expr_input_variables(arg)
                #create set union of all arguments' inputs
                inputs.update(arg_inputs)
            #decorate call with discovered inputs
            expr.inputs = inputs
            return inputs
        else:
            raise Exception('Unexpected type of argument '
                            'for Siml function. type: %s; value: %s' 
                            % (str(type(arg)), str(arg)))
        
    
    def decorate_assignment(self, assignment):
        '''Put sets of input and output variables on an assignment statement.'''
        assert isinstance(assignment, NodeAssignment)
        #compute sets of input and output objects
        inputs = self.discover_expr_input_variables(assignment.expression)
        outputs = set([assignment.target])
        #decorate the assignment
        assignment.inputs = inputs
        assignment.outputs = outputs
#        #create sets of all used inputs and outputs
#        self.all_inputs.update(inputs)
#        self.all_outputs.update(outputs)
        return (inputs, outputs)
        
        
#    def decorate_if_clause(self, clause):
#        '''Find inputs and outputs of a single clause of the if statement'''
#        pass
    def decorate_if_statement(self, stmt):
        '''Find inputs and outputs of an 'if' statement.'''
        assert isinstance(stmt, NodeIfStmt)
        inputs, outputs = set(), set()
        for clause in stmt.clauses:
            assert isinstance(clause, NodeClause)
            cond_inp = self.discover_expr_input_variables(clause.condition)
            stmt_inp, out = self.decorate_statement_list(clause.statements)
            inp = cond_inp | stmt_inp
            #decorate the clause
            clause.inputs = inp
            clause.outputs = out
            #compute inputs and outputs of whole 'if' statement
            inputs.update(inp)
            outputs.update(out)
        #decorate the 'if' statement
        stmt.inputs = inputs
        stmt.outputs = outputs
        return (inputs, outputs)
        
            
    def decorate_statement_list(self, stmt_list):  
        '''
        Find inputs and outputs of a list of statements.
        '''  
        inputs, outputs = set(), set()
        for stmt in stmt_list:
            if isinstance(stmt, NodeAssignment):
                inp, out = self.decorate_assignment(stmt)
                inputs.update(inp)
                outputs.update(out)
            elif isinstance(stmt, NodeIfStmt):
                inp, out = self.decorate_if_statement(stmt)
                inputs.update(inp)
                outputs.update(out)
            else:
                raise Exception('Unexpected type of statement '
                                'type: %s; value: %s' 
                                % (str(type(stmt)), str(stmt)))
        #Correct for data flow inside the statement list.
        #If some outputs are used as inputs by subsequent statements,
        #these outputs should not appear in the inputs too.
        inputs = inputs - outputs
        return inputs, outputs
    
    
    def decorate_main_function(self, main_function):
        '''Put input and output decorations on all statements'''
        inputs, outputs = self.decorate_statement_list(main_function.statements)
        main_function.inputs = inputs
        main_function.outputs = outputs
        return inputs, outputs
        
    
#TODO: test: the methods of a flat object must not use any data from 
#      outside of the flat_object.

#TODO: test if all variables are assigned once (single assignment)     
#TODO: test if data flow is possible
#TODO: reorder statements

#TODO: remove unused variables
#TODO: remove assignments to unused variables from each branch of in 'if' statement separately.
#TODO: substitute away variables that are used only once

