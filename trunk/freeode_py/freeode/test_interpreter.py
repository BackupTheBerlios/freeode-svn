# -*- coding: utf-8 -*-
#***************************************************************************
#    Copyright (C) 2006 - 2009 by Eike Welk                                *
#    eike.welk@post.rwth-aachen.de                                         *
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
Test code for the interpreter module
"""

from __future__ import division
from __future__ import absolute_import              #IGNORE:W0410

#The py library is not standard. Preserve ability to use some test functions
# for debugging when the py library, and the py.test testing framework, are 
# not installed. 
try:                      
    import py
except:
    print 'No py library, many tests may fail!'



# -------- Test InterpreterObject class ----------------------------------------------------------------------
def test_InterpreterObject_1():
    print 'InterpreterObject: basic operation'
    from freeode.interpreter import (InterpreterObject, DotName, UndefinedAttributeError,
                                     DuplicateAttributeError, BoundMethod, CallableObject)

    o1 = InterpreterObject()
    attr1 = InterpreterObject()
    attr2 = InterpreterObject()
    
    #create small tree of objects:
    # o1
    #  +--- attr1
    #  +--- attr2
    o1.create_attribute('attr1', attr1)
    o1.create_attribute(DotName('attr2'), attr2)
    
    #test for existence of attributes
    assert o1.has_attribute(DotName('attr1'))
    assert o1.has_attribute(DotName('attr2'))
    assert not o1.has_attribute(DotName('foo')) 
    
    #retrieval of attributes
    assert o1.get_attribute(DotName('attr1')) == attr1
    assert o1.get_attribute(DotName('attr2')) == attr2
    
    #attempt to retrieve non-existing attribute
    try: 
        o1.get_attribute(DotName('foo'))
    except UndefinedAttributeError: 
        print 'Expected exception: undefined attribute'
    else:
        assert False, 'Code should raise exception'
    
    #attempt to create attribute with name that already exists
    try: 
        o1.create_attribute('attr1', attr1)
    except DuplicateAttributeError:
        print 'Expected exception: duplicate attribute'
    else:
        assert False, 'Code should raise exception'
    
    

def test_InterpreterObject_method_retrieval():
    print 'InterpreterObject: attributes are also searched in the class object'
    print 'If the attributes taken from the class are call-able they are wrapped in a bound method.'
    from freeode.interpreter import (InterpreterObject, DotName, UndefinedAttributeError,
                                     DuplicateAttributeError, BoundMethod, CallableObject, 
                                     ref)
    #the class
    cls = InterpreterObject()
    cls_attr1 = InterpreterObject()
    cls_func1 = CallableObject('cls_func1')
    cls.create_attribute('cls_attr1', cls_attr1)
    cls.create_attribute('cls_func1', cls_func1)
    
    #the tested object
    o1 = InterpreterObject()
    o1.type = ref(cls)
    o1_attr1 = InterpreterObject()
    o1_func1 = CallableObject('o1_func1')
    o1.create_attribute('o1_attr1', o1_attr1)
    o1.create_attribute('o1_func1', o1_func1)
    
    #test for existence of attributes
    assert o1.has_attribute(DotName('o1_attr1'))
    assert o1.has_attribute(DotName('o1_func1'))
    assert o1.has_attribute(DotName('cls_attr1'))
    assert o1.has_attribute(DotName('cls_func1'))
    assert not o1.has_attribute(DotName('foo')) 

    #retrieval of attributes 
    #attributes of the instance are retrieved without modifications
    assert o1.get_attribute(DotName('o1_attr1')) == o1_attr1
    assert o1.get_attribute(DotName('o1_func1')) == o1_func1
    #data attributes of the class are retrieved without modifications
    assert o1.get_attribute(DotName('cls_attr1')) == cls_attr1
    #method (callable) attributes are put into a wrapper object 
    assert o1.get_attribute(DotName('cls_func1')).function == cls_func1
    assert isinstance(o1.get_attribute(DotName('cls_func1')), BoundMethod)

    #attempt to retrieve non-existing attribute
    try: 
        o1.get_attribute(DotName('foo'))
    except UndefinedAttributeError: 
        print 'Expected exception: undefined attribute'
    else:
        assert False, 'Code should raise exception'



# -------- Test IntArgumentList class ------------------------------------------------------------------------
def test_IntArgumentList_1():
    print 'IntArgumentList: construction'
    from freeode.interpreter import (ArgumentList, NodeFuncArg, DotName, UserException, CLASS_FLOAT)
    
    #Test normal construction only positional argument: f(a, b)
    ArgumentList([NodeFuncArg(DotName('a')),
                  NodeFuncArg(DotName('b'))], None)
    #Test normal construction with keyword arguments: f(a, b=1)
    val_1 = CLASS_FLOAT()
    ArgumentList([NodeFuncArg(DotName('a')),
                  NodeFuncArg(DotName('b'), default_value=val_1)], None)
    #Names are automatically converted to DotName
    ArgumentList([NodeFuncArg('a'),
                  NodeFuncArg('b', default_value=val_1)], None)
    
    #argument list with two identical argument names: f(a, a)
    try:
        ArgumentList([NodeFuncArg(DotName('a')),
                      NodeFuncArg(DotName('a'))], None)
    except UserException, e:
        print 'Caught expected exception (argument names must be unique)'
        print e
    else:
        py.test.fail('This code should raise an exception (argument names must be unique).') #IGNORE:E1101
        
    #argument list with keyword argument before positional argument: f(a=1, b)
    try:
        val_1 = CLASS_FLOAT()
        ArgumentList([NodeFuncArg(DotName('a'), default_value=val_1),
                      NodeFuncArg(DotName('b'))], None)
    except UserException, e:
        print 'Caught expected exception (keyword argument before positional argument)'
        print e
    else:
        py.test.fail('This code should raise an exception (keyword argument before positional argument).') #IGNORE:E1101
#    assert 1==0
    
    
    
def test_IntArgumentList_2():
    print 'ArgumentList: test argument processing at call site'
    from freeode.interpreter import (ArgumentList, NodeFuncArg, DotName, UserException, CLASS_FLOAT)
    
    #argument list for testing
    al = ArgumentList([NodeFuncArg(DotName('a')),
                       NodeFuncArg(DotName('b'))], None)
    #some interpreter level values
    val_1 = CLASS_FLOAT()
    val_1.value = 1
    val_2 = CLASS_FLOAT()
    val_2.value = 2
    
    #call with correct number of positional arguments
    arg_vals = al.parse_function_call_args([val_1, val_2], {})
    assert arg_vals[DotName('a')].value == 1
    assert arg_vals[DotName('b')].value == 2
    
    #call with correct number of keyword arguments
    arg_vals = al.parse_function_call_args([], {DotName('a'):val_1,  
                                                DotName('b'):val_2})
    assert arg_vals[DotName('a')].value == 1
    assert arg_vals[DotName('b')].value == 2
    
    #call with too few arguments
    try:
        al.parse_function_call_args([], {})
    except UserException, e:
        print 'Caught expected exception (too few arguments)'
        print e
    else:
        py.test.fail('This code should raise an exception (too few arguments).') #IGNORE:E1101
        
    #call with too many positional arguments
    try:
        al.parse_function_call_args([val_1, val_2, val_2], {})
    except UserException, e:
        print 'Caught expected exception (too many positional arguments)'
        print e
    else:
        py.test.fail('This code should raise an exception (too many positional arguments).') #IGNORE:E1101
       
    #call with unknown keyword argument
    try:
        al.parse_function_call_args([], {DotName('a'):val_1,  
                                         DotName('c'):val_2})
    except UserException, e:
        print 'Caught expected exception (unknown keyword argument)'
        print e
    else:
        py.test.fail('This code should raise an exception (unknown keyword argument).') #IGNORE:E1101
        
    #call with duplicate keyword argument
    try:
        al.parse_function_call_args([val_1, val_2], {DotName('a'):val_1})
    except UserException, e:
        print 'Caught expected exception (duplicate keyword argument)'
        print e
    else:
        py.test.fail('This code should raise an exception (duplicate keyword argument).') #IGNORE:E1101
    #assert 1==0
    
    
    
def test_IntArgumentList_2_1():
    print 'ArgumentList: __init__: strings are converted to DotName, default argument for loc'
    from freeode.interpreter import (ArgumentList, NodeFuncArg, DotName, CLASS_FLOAT)
    
    #argument list for testing
    al = ArgumentList([NodeFuncArg('a'),
                       NodeFuncArg('b')])
    #some interpreter level values
    val_1 = CLASS_FLOAT()
    val_1.value = 1
    val_2 = CLASS_FLOAT()
    val_2.value = 2
    
    #call with correct number of positional arguments
    arg_vals = al.parse_function_call_args([val_1, val_2], {})
    assert arg_vals[DotName('a')].value == 1
    assert arg_vals[DotName('b')].value == 2
    
    #call with correct number of keyword arguments
    arg_vals = al.parse_function_call_args([], {DotName('a'):val_1,  
                                                DotName('b'):val_2})
    assert arg_vals[DotName('a')].value == 1
    assert arg_vals[DotName('b')].value == 2
    
    
    
def test_IntArgumentList_3():
    print 'ArgumentList: test calling with default arguments.'
    from freeode.interpreter import (ArgumentList, NodeFuncArg, DotName, CLASS_FLOAT)
    
    #some interpreter level values
    val_1 = CLASS_FLOAT()
    val_1.value = 1
    val_2 = CLASS_FLOAT()
    val_2.value = 2
    #argument list for testing: def f(a, b=2)
    al = ArgumentList([NodeFuncArg(DotName('a')),
                       NodeFuncArg(DotName('b'), default_value=val_2)], None)
    
    #call with one positional argument: f(1). For argument 'b' default value must be used.
    arg_vals = al.parse_function_call_args([val_1], {})
    assert arg_vals[DotName('a')].value == 1
    assert arg_vals[DotName('b')].value == 2
    
    
    
def test_IntArgumentList_4():
    print 'ArgumentList: test type compatibility testing.'
    from freeode.interpreter import (ArgumentList, NodeFuncArg, DotName,  
                                     CLASS_FLOAT, CLASS_STRING)
    
    #some interpreter level values
    val_1 = CLASS_FLOAT(1)
    val_hello = CLASS_STRING('hello')
    #argument list for testing: f(a:Float, b:String)
    al = ArgumentList([NodeFuncArg(DotName('a'), type=CLASS_FLOAT),
                       NodeFuncArg(DotName('b'), type=CLASS_STRING)], None)
    
    #call with correct positional arguments: f(1, 'hello')
    arg_vals = al.parse_function_call_args([val_1, val_hello], {})
    assert arg_vals[DotName('a')].value == 1
    assert arg_vals[DotName('b')].value == 'hello'
    
    #call with correct keyword arguments: f(a=1, b='hello')
    arg_vals = al.parse_function_call_args([], {DotName('a'):val_1, 
                                                DotName('b'):val_hello})
    assert arg_vals[DotName('a')].value == 1
    assert arg_vals[DotName('b')].value == 'hello'
    
    #call with mixed positional and keyword arguments: f(1, b='hello')
    arg_vals = al.parse_function_call_args([val_1], {DotName('b'):val_hello})
    assert arg_vals[DotName('a')].value == 1
    assert arg_vals[DotName('b')].value == 'hello'
    
 
 
# -------- Test wrapper object for Python functions ------------------------------------------------------------------------
def test_BuiltInFunctionWrapper_1():
    print 'BuiltInFunctionWrapper: test function call with known arguments, no Interpreter.'
    from freeode.interpreter import (BuiltInFunctionWrapper,
                                     ArgumentList, NodeFuncArg,   
                                     CLASS_FLOAT)
    import math
    
    #create sqrt function with named arguments
    sqrt = lambda x: math.sqrt(x) 
    #some interpreter level values
    val_2 = CLASS_FLOAT(2)

    #create a function object that wraps the sqrt function
    func = BuiltInFunctionWrapper('sqrt', 
                                  ArgumentList([NodeFuncArg('x', CLASS_FLOAT)], None), 
                                  return_type=CLASS_FLOAT, 
                                  py_function=sqrt)
    #call function: sqrt(2)
    siml_ret = func(val_2)
    assert siml_ret.value == sqrt(2) #IGNORE:E1103
    #assert False, 'implement me!'
    
    
                                      
def test_BuiltInFunctionWrapper_2():
    print 'BuiltInFunctionWrapper: test function call with unknown arguments, no Interpreter.'
    from freeode.interpreter import (BuiltInFunctionWrapper,
                                     ArgumentList, NodeFuncArg, DotName, ref,  
                                     CLASS_FLOAT, 
                                     NodeOpPrefix1, NodeOpInfix2, NodeFuncCall)
    import math
    
    #create sqrt function with named arguments
    sqrt = lambda x: math.sqrt(x) 
    #create unknown interpreter level values
    val_x = CLASS_FLOAT()
    val_y = CLASS_FLOAT()
    #create fragment of unknown expression
    binop_u = NodeOpInfix2()
    binop_u.type = ref(CLASS_FLOAT)
    #create a function object that wraps the sqrt function
    func = BuiltInFunctionWrapper('sqrt', 
                                  ArgumentList([NodeFuncArg('x', CLASS_FLOAT)]), 
                                  return_type=CLASS_FLOAT, 
                                  py_function=sqrt)
    #create a binary operator object - wraps nothing
    binop = BuiltInFunctionWrapper('__add__', 
                                   ArgumentList([NodeFuncArg('x', CLASS_FLOAT), 
                                                 NodeFuncArg('y', CLASS_FLOAT)]), 
                                   return_type=CLASS_FLOAT, 
                                   py_function=None,
                                   is_binary_op=True, op_symbol='+')
    #create a prefix operator object - wraps nothing
    prefix_op = BuiltInFunctionWrapper('__sign__', 
                                ArgumentList([NodeFuncArg('x', CLASS_FLOAT)]), 
                                return_type=CLASS_FLOAT, 
                                py_function=None,
                                is_prefix_op=True, op_symbol='-')
    
    #call function: sqrt( <unknown value> )
    siml_ret = func(val_x)
    assert isinstance(siml_ret, NodeFuncCall)
    assert siml_ret.type() == CLASS_FLOAT
    assert siml_ret.keyword_arguments[DotName('x')] == val_x
    assert siml_ret.function_object == func
    
    #call function: sqrt( <expression fragment> )
    siml_ret = func(binop_u)
    assert isinstance(siml_ret, NodeFuncCall)
    assert siml_ret.type() == CLASS_FLOAT
    assert siml_ret.keyword_arguments[DotName('x')] == binop_u
    assert siml_ret.function_object == func
    
    #call binary operator ( <unknown value x>,  <unknown value y>)
    siml_ret = binop(val_x, val_y)
    assert isinstance(siml_ret, NodeOpInfix2)
    assert siml_ret.type() == CLASS_FLOAT
    assert siml_ret.arguments[0] == val_x
    assert siml_ret.arguments[1] == val_y
    assert siml_ret.function_object == binop
    
    #call prefix operator ( <unknown value x> )
    siml_ret = prefix_op(val_x)
    assert isinstance(siml_ret, NodeOpPrefix1)
    assert siml_ret.type() == CLASS_FLOAT
    assert siml_ret.arguments[0] == val_x
    assert siml_ret.function_object == prefix_op
    
    #assert False, 'implement me!'
    
    
                                      
# -------- Test 2nd version of wrapper object for Python functions ------------------------------------------------------------------------
def test_BuiltInFunctionWrapper2_1():
    print 'BuiltInFunctionWrapper2: test 2nd version of function call with known arguments, no Interpreter.'
    from freeode.interpreter import (BuiltInFunctionWrapper2,
                                     ArgumentList, NodeFuncArg,   
                                     CLASS_FLOAT, )
    import math
    
    #create sqrt function with named arguments
    sqrt = lambda x: CLASS_FLOAT(math.sqrt(x.value))
    #some interpreter level values
    val_2 = CLASS_FLOAT(2)

    #create a function object that wraps the sqrt function
    func = BuiltInFunctionWrapper2('sqrt', 
                                  ArgumentList([NodeFuncArg('x', CLASS_FLOAT)], None), 
                                  return_type=CLASS_FLOAT, 
                                  py_function=sqrt)
    #call function: sqrt(2)
    siml_ret = func(val_2)
    assert siml_ret.value == math.sqrt(2) #IGNORE:E1103
    #assert False, 'implement me!'
    
    
                                      
# -------- Test user defined class object ------------------------------------------------------------------------
def test_SimlClass_1():
    #py.test.skip('Test expression evaluation (only immediate values)')
    print 'Test SimlClass: class without statements'
    from freeode.interpreter import SimlClass, Interpreter
    
    #The SimlClass object contains the interpreter as a class variable 
    #It uses its methods and terefore only functions after the interpreter 
    #was constructed
    intp = Interpreter()
    
    #construct a class with no statements and no base classes
    #class Test1:
    #    <nothing; impossible in Siml>
    c1=SimlClass('Test1', None, [], None)
    
    #create an instance of the class
    i1 = c1()
    
    assert i1.type() == c1
    


def test_SimlClass_2():
    #py.test.skip('Test expression evaluation (only immediate values)')
    print 'Test SimlClass: class with one data member'
    from freeode.interpreter import SimlClass, Interpreter
    from freeode.ast import NodeDataDef, NodeIdentifier, DotName
    
    #The SimlClass object contains the interpreter as a class variable 
    #It uses its methods and therefore only functions when there is an 
    #interpreter object.
    intp = Interpreter()
    #set up the built in library
    intp.create_test_module_with_builtins()
    
    #construct a class with no statements and no base classes
    #class Test1:
    #    Data a:Float
    #TODO: NodeDataDef needs nice constructor
    data_stmt = NodeDataDef('a1', NodeIdentifier('Float'))
    cls=SimlClass('Test1', None, 
                 [data_stmt], 
                 None)
    assert cls.has_attribute(DotName('a1'))
    
    #create an instance of the class
    inst = cls()
    
    assert inst.type() == cls
    assert inst.has_attribute(DotName('a1'))
    #the attributes must be copied, not identical
    cls_a1 = cls.get_attribute(DotName('a1'))
    inst_a1 = inst.get_attribute(DotName('a1'))
    assert id(cls_a1) != id(inst_a1)
    assert cls_a1.type() == inst_a1.type()
    

# -------- Test wrapper for built in classes ------------------------------------------------------------------
def test_BuiltInClassWrapper_1():
    #py.test.skip('Test BuiltInClassWrapper: construction, put into module')
    print 'Test BuiltInClassWrapper: construction, put into module'
    from freeode.interpreter import BuiltInClassWrapper, InterpreterObject
    from freeode.ast import DotName
    
    #test object construction 
    class Dummy(InterpreterObject):
        pass
    siml_dummy_class = BuiltInClassWrapper('Dummy')
    siml_dummy_class.py_class = Dummy
    
    dummy = siml_dummy_class()
    assert isinstance(dummy, Dummy)
    
    #test inclusion in module - convenience function
    mod = InterpreterObject()
    siml_dummy_class.put_into(mod)
    
    assert mod.get_attribute(DotName('Dummy')) is siml_dummy_class
    
    

# -------- Test Siml wrapper for float classes ------------------------------------------------------------------
def test_IFloat_1():
    #py.test.skip('Test IFloat: construction from Siml class')
    print 'Test IFloat: construction from Siml class'
    from freeode.interpreter import IFloat, CLASS_FLOAT, siml_isinstance
    #from freeode.ast import DotName
    
    #test construction from Siml class
    val = CLASS_FLOAT()
    assert isinstance(val, IFloat)
    assert siml_isinstance(val, CLASS_FLOAT)
    
    #test construction from Python class - Siml type must still be right
    val1 = IFloat()
    assert siml_isinstance(val1, CLASS_FLOAT)



def test_IFloat_2():
    #py.test.skip('Test IFloat: constructor')
    print 'Test IFloat: constructor'
    from freeode.interpreter import IFloat
    #from freeode.ast import DotName
    
    #no arguments
    val_none = IFloat()
    assert val_none.value is None
    
    #int argument
    val_1 = IFloat(1)
    assert val_1.value == 1.
    
    #float argument
    val_pi = IFloat(3.1415)
    assert val_pi.value == 3.1415
    
    #IFloat argument
    val_1_s = IFloat(val_1)
    assert  val_1_s.value == 1.

    try:
        IFloat('hello')
    except TypeError:
        print 'expected exception: number can not be constructed from string.'
    else:
        assert False, 'object was constructed with wrong init values'



def test_IFloat_3():
    #py.test.skip('Test IFloat: mathematical operators from Python') #IGNORE:E1101
    print 'Test IFloat: mathematical operators from Python'
    from freeode.interpreter import IFloat
    #from freeode.ast import DotName
    
    val_2 = IFloat(2)
    val_3 = IFloat(3)
    
    assert (val_2 + val_3).value == val_2.value + val_3.value
    assert (val_2 - val_3).value == val_2.value - val_3.value
    assert (val_2 * val_3).value == val_2.value * val_3.value
    #for division to work the class needs a __truediv__ function, 
    #which it does not have 
    #assert (val_2 / val_3).value == val_2.value / val_3.value
    assert (val_2 % val_3).value == val_2.value % val_3.value
    assert (val_2 ** val_3).value == val_2.value ** val_3.value
    
    #assert abs(val_2).value == abs(val_2.value)
    assert (-val_2).value == -val_2.value



def test_IFloat_4():
    #py.test.skip('Test IFloat: special functions for mathematical operators from Siml')
    print 'Test IFloat: special functions for mathematical operators from Siml'
    from freeode.interpreter import IFloat
    from freeode.ast import DotName
    
    val_2 = IFloat(2)
    val_3 = IFloat(3)
    
    #look the methods up and call them; then assert that the result is correct
    res = val_2.get_attribute(DotName('__add__'))(val_3)
    assert res.value == 2 + 3
    res = val_2.get_attribute(DotName('__sub__'))(val_3)
    assert res.value == 2 - 3
    res = val_2.get_attribute(DotName('__mul__'))(val_3)
    assert res.value == 2 * 3
    res = val_2.get_attribute(DotName('__div__'))(val_3)
    assert res.value == 2 / 3
    res = val_2.get_attribute(DotName('__mod__'))(val_3)
    assert res.value == 2 % 3
    res = val_2.get_attribute(DotName('__pow__'))(val_3)
    assert res.value == 2 ** 3
    res = val_2.get_attribute(DotName('__neg__'))()
    assert res.value == -2 



# -------- Test Siml wrapper for str classes ------------------------------------------------------------------
def test_IString_1():
    #py.test.skip('Test IString: construction from Siml class')
    print 'Test IString: construction from Siml class'
    from freeode.interpreter import IString, CLASS_STRING, siml_isinstance
    #from freeode.ast import DotName
    
    #test construction from Siml class
    val = CLASS_STRING()
    assert isinstance(val, IString)
    assert siml_isinstance(val, CLASS_STRING)
    
    #test construction from Python class - Siml type must still be right
    val1 = IString()
    assert siml_isinstance(val1, CLASS_STRING)



def test_IString_2():
    #py.test.skip('Test IString: constructor')
    print 'Test IString: constructor'
    from freeode.interpreter import IString
    #from freeode.ast import DotName
    
    #no arguments
    val_none = IString()
    assert val_none.value is None
    
    #int argument
    val_1 = IString(1)
    assert val_1.value == '1'
    
    #float argument
    val_pi = IString(3.1415)
    assert val_pi.value == '3.1415'
    
    #str argument
    val_a = IString('a')
    assert val_a.value == 'a'
    
    #IString argument
    val_a_s = IString(val_a)
    assert  val_a_s.value == 'a'

    try:
        IString([])
    except TypeError:
        print 'expected exception: wrong argument type.'
    else:
        assert False, 'object was constructed with wrong initial values'



def test_IString_3():
    #py.test.skip('Test IString: mathematical operators from Python') #IGNORE:E1101
    print 'Test IString: mathematical operators from Python'
    from freeode.interpreter import IString
    #from freeode.ast import DotName
    
    val_a = IString('a')
    val_b = IString('b')
    
    assert (val_a + val_b).value == val_a.value + val_b.value



def test_IString_4():
    #py.test.skip('Test IString: special functions for mathematical operators from Siml')
    print 'Test IString: special functions for mathematical operators from Siml'
    from freeode.interpreter import IString
    from freeode.ast import DotName
    
    val_a = IString('a')
    val_b = IString('b')
    
    #look the methods up and call them; then assert that the result is correct
    res = val_a.get_attribute(DotName('__add__'))(val_b)
    assert res.value == 'ab'



# -------- Test administrative functions ------------------------------------------------------------------------
def test_determine_result_role_1():
    #py.test.skip('Test IString: special functions for mathematical operators from Siml')
    print 'Test determine_result_role: '
    from freeode.interpreter import IFloat, determine_result_role
    from freeode.ast import RoleConstant, RoleParameter, RoleVariable
    
    #some constants
    c_1 = IFloat()
    c_1.role = RoleConstant
    c_2 = IFloat()
    c_2.role = RoleConstant
    #some parameters
    p_1 = IFloat()
    p_1.role = RoleParameter
    p_2 = IFloat()
    p_2.role = RoleParameter
    #some variables
    v_1 = IFloat()
    v_1.role = RoleVariable
    v_2 = IFloat()
    v_2.role = RoleVariable
    
    #determine the most variable role among the arguments
    assert determine_result_role((c_1, p_1, v_1), 
                                 {'a':c_2, 'b':p_2, 'c':v_2, }) == RoleVariable
    assert determine_result_role((c_1, p_1), 
                                 {'a':c_2, 'b':p_2}) == RoleParameter
    assert determine_result_role((c_1,), 
                                 {'a':c_2}) == RoleConstant
    


# -------- Test expression evaluation ------------------------------------------------------------------------
def test_operator_dispatch_1():
    #py.test.skip('Test ExpressionVisitor: handling of binary operators with Float values.')
    print 'Test ExpressionVisitor: handling of binary operators with Float values.'
    from freeode.interpreter import (IFloat, ExpressionVisitor)
    from freeode.ast import NodeOpInfix2, NodeOpPrefix1
    
    expr_visit = ExpressionVisitor(None)
    
    val_2 = IFloat(2)
    val_3 = IFloat(3)
    
    op_sub = NodeOpInfix2('-', [val_2, val_3])
    res = expr_visit.dispatch(op_sub)
    print res
    assert res.value == -1 
    
    op_neg = NodeOpPrefix1('-', [val_2])
    res = expr_visit.dispatch(op_neg)
    print res
    assert res.value == -2 
    


# -------- Test expression evaluation ------------------------------------------------------------------------
def test_operator_dispatch_2():
    #py.test.skip('Test ExpressionVisitor: handling of binary operators with unknown Float values.')
    print 'Test ExpressionVisitor: handling of binary operators with unknown Float values.'
    from freeode.interpreter import (IFloat, ExpressionVisitor)
    from freeode.ast import NodeOpInfix2, NodeOpPrefix1

    expr_visit = ExpressionVisitor(None)
    
    val_2 = IFloat()
    val_3 = IFloat()
    
    op_sub = NodeOpInfix2('-', [val_2, val_3])
    res = expr_visit.dispatch(op_sub)
    print res
    assert isinstance(res, NodeOpInfix2)
    
    op_neg = NodeOpPrefix1('-', [val_2])
    res = expr_visit.dispatch(op_neg)
    print res
    assert isinstance(res, NodeOpPrefix1)
    


def test_expression_evaluation_1():
    #py.test.skip('Test expression evaluation (only immediate values)')
    print 'Test expression evaluation (only immediate values)'
    from freeode.interpreter import ExpressionVisitor
    import freeode.simlparser as simlparser
    
    #parse the expression
    ps = simlparser.Parser()
    ex = ps.parseExpressionStr('0+1*2')
    print
    print 'AST (parser output): -----------------------------------------------------------'
    print ex
    
    #interpret the expression
    exv = ExpressionVisitor(None)
    res = exv.dispatch(ex)
    print
    print 'Result object: --------------------------------------------------------------'
    print res 
    assert res.value == 2.0
    
    

def test_expression_evaluation_2():
    #py.test.skip('Test expression evaluation (access to variables)')
    print 'Test expression evaluation (access to variables)'
    from freeode.interpreter import (IModule, CLASS_FLOAT, RoleConstant, 
                                     ExpressionVisitor, DotName, 
                                     ExecutionEnvironment)
    import freeode.simlparser as simlparser
    
    #parse the expression
    ps = simlparser.Parser()
    ex = ps.parseExpressionStr('1 + a * 2')
    print
    print 'AST (parser output): -----------------------------------------------------------'
    print ex
    
    #create module where name lives
    mod = IModule()
    val_2 = CLASS_FLOAT(2.0)
    val_2.role = RoleConstant
    mod.create_attribute(DotName('a'), val_2)
    print
    print 'Module where variable is located: --------------------------------------------'
    print mod
    
    #create environment for lookup of variables (stack frame)
    env = ExecutionEnvironment()
    env.global_scope = mod
    
    #interpret the expression
    exv = ExpressionVisitor(None)
    exv.environment = env
    res = exv.dispatch(ex)
    print
    print 'Result object: --------------------------------------------------------------'
    print res 
    assert res.value == 5.0
    
    

def test_expression_evaluation_2_1():
    #py.test.skip('Test expression evaluation (access to variables)')
    print 'Test expression evaluation (calling built in functions)'
    from freeode.interpreter import (simlparser, IModule, ExecutionEnvironment,
                                     ExpressionVisitor, DotName,
                                     BuiltInFunctionWrapper, ArgumentList, NodeFuncArg,
                                     CLASS_FLOAT)
    import math
    
    #parse the expression
    ps = simlparser.Parser()
    ex = ps.parseExpressionStr('sqrt(2)')
    print
    print 'AST (parser output): -----------------------------------------------------------'
    print ex
    
    #create module where names live
    mod = IModule()
    #create sqrt function with named arguments
    sqrt = lambda x: math.sqrt(x) 
    #create a function object that wraps the sqrt function
    func = BuiltInFunctionWrapper('sqrt', 
                                  ArgumentList([NodeFuncArg('x', CLASS_FLOAT)]), 
                                  return_type=CLASS_FLOAT, 
                                  py_function=sqrt)
    #put function into module
    mod.create_attribute(DotName('sqrt'), func)
    print
    print 'Module where function is located: --------------------------------------------'
    print mod
    
    #create environment for lookup of variables (stack frame)
    env = ExecutionEnvironment()
    env.global_scope = mod
    #create visitor for evaluating the expression
    exv = ExpressionVisitor(None)
    exv.environment = env
    #evaluate the expression
    res = exv.dispatch(ex)
    print
    print 'Result object: --------------------------------------------------------------'
    print res 
    assert res.value == sqrt(2)
    
    

def test_expression_evaluation_3():
    #py.test.skip('Test disabled')
    print 'Test expression evaluation (returning of partially evaluated expression when accessing variables)'
    from freeode.interpreter import (IModule, CLASS_FLOAT, RoleVariable, 
                                     DotName, ExecutionEnvironment, ExpressionVisitor,
                                     NodeOpInfix2)
    import freeode.simlparser as simlparser
    #parse the expression
    ps = simlparser.Parser()
    ex = ps.parseExpressionStr('a + 2*2')
    print
    print 'AST (parser output): -----------------------------------------------------------'
    print ex
    
    #create module where name lives
    mod = IModule()
    #create attribute 'a' with no value
    val_2 = CLASS_FLOAT()
    val_2.value = None
    val_2.role = RoleVariable
    mod.create_attribute(DotName('a'), val_2)
    print
    print 'Module where variable is located: --------------------------------------------'
    print mod
    
    #create environment for lookup of variables (stack frame)
    env = ExecutionEnvironment()
    env.global_scope = mod
    
    #interpret the expression
    exv = ExpressionVisitor(None)
    exv.environment = env
    res = exv.dispatch(ex)
    print
    print 'Result object - should be an unevaluated expression: --------------------------------------------------------------'
    print res 
    assert isinstance(res, NodeOpInfix2)
    assert res.operator == '+'



# --------- Test basic execution of statements (no interpreter object) ----------------------------------------------------------------
def test_basic_execution_of_statements():
    #py.test.skip('Test basic execution of statements (no interpreter object)')
    print 'Test basic execution of statements (no interpreter object) .................................'
    from freeode.interpreter import (IModule, CLASS_FLOAT, CLASS_STRING,
                                     DotName, ExecutionEnvironment,
                                     ExpressionVisitor, StatementVisitor)
    import freeode.simlparser as simlparser
    
    prog_text = \
'''
data a:Float const 
data b:Float const 
a = 2*2 + 3*4
b = 2 * a

data c:String const
c = 'Hello ' + 'world!'
'''

    #create the built in library
    mod = IModule()
    mod.create_attribute(DotName('Float'), CLASS_FLOAT)
    mod.create_attribute(DotName('String'), CLASS_STRING)
#    print
#    print 'global namespace - before interpreting statements - built in library: ---------------'
#    print mod
           
    #initialize the interpreter
    env = ExecutionEnvironment()
    exv = ExpressionVisitor(None)
    exv.environment = env
    stv = StatementVisitor(None)
    stv.environment = env
    stv.expression_visitor = exv
    #set up parsing the main module
    stv.environment.global_scope = mod
    stv.environment.local_scope = mod

    #parse the program text
    ps = simlparser.Parser()
    module_code = ps.parseModuleStr(prog_text)
    
    #interpreter main loop
    for stmt in module_code.statements:
        stv.dispatch(stmt)
        
#    print
#    print 'global namespace - after interpreting statements: -----------------------------------'
#    print mod
    
    assert mod.get_attribute(DotName('a')).value == 16             #IGNORE:E1103
    assert mod.get_attribute(DotName('b')).value == 2*16           #IGNORE:E1103
    assert mod.get_attribute(DotName('c')).value == 'Hello world!' #IGNORE:E1103
  
  
  
# -------- Test interpreter object - basic --------------------------------------------------------  
def test_interpreter_assignment_1():
    #py.test.skip('Test disabled')
    print 'Test interpreter object: assignment. needs working data statement and number ...............................................................'
    from freeode.interpreter import Interpreter, DotName
    import math
    
    prog_text = \
'''
data a: Float const
a = 2
'''
    #create the interpreter
    intp = Interpreter()
    #run mini program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print 'module after interpreter run: ---------------------------------'
    print intp.modules['test']
    
    assert intp.modules['test'].get_attribute(DotName('a')).value == 2
  
  

def test_interpreter_object_siml_function_1():
    #py.test.skip('Test disabled')
    print 'Test interpreter object: call user defined function ...............................................................'
    print 'User defined functions are created without parser.'
    from freeode.interpreter import (Interpreter, SimlFunction, 
                                     ArgumentList, CLASS_FLOAT, CLASS_STRING,
                                     BUILT_IN_LIB)
    from freeode.ast import (NodeFuncArg, NodeReturnStmt, 
                             NodeIdentifier, UserException)

    #create the interpreter - initializes InterpreterObject.interpreter
    # this way SimlFunction can access the interpreter.
    intp = Interpreter()    #IGNORE:W0612
    #create a Siml value as function argument
    val_1 = CLASS_FLOAT()
    val_1.value = 1.
    #TODO: test function calling mechanism with unevaluated expressions too!
#    #create an unevaluated expression
#    u_ex = NodeOpInfix2()
#    u_ex.type = ref(CLASS_FLOAT)
    
    #create a function without statements (impossible in Siml)
    # func test(a:Float):
    #     ** nothing **
    f1 = SimlFunction('test', ArgumentList([NodeFuncArg('a', CLASS_FLOAT)]), 
                      return_type=None, statements=[], global_scope=BUILT_IN_LIB)
    #call with existing value
    f1(val_1)
    
    #create a function with return statement
    # func test(a:Float) -> Float:
    #     return a
    f2 = SimlFunction('test', ArgumentList([NodeFuncArg('a', CLASS_FLOAT)]), 
                      return_type=CLASS_FLOAT, 
                      statements=[NodeReturnStmt([NodeIdentifier('a')])], 
                      global_scope=BUILT_IN_LIB)
    #call function and see if value is returned
    ret_val = f2(val_1)
    assert ret_val.value == 1.

    #create a function with wrong return type
    # func test(a:Float) -> String:
    #     return a
    f3= SimlFunction('test', ArgumentList([NodeFuncArg('a', CLASS_FLOAT)]), 
                      return_type=CLASS_STRING, 
                      statements=[NodeReturnStmt([NodeIdentifier('a')])], 
                      global_scope=BUILT_IN_LIB)
    try:
        ret_val = f3(val_1)
    except UserException:
        print 'Getting expected exception: type mismatch at function return'
    else:
        py.test.fail('There was wrong return type, but no exception!') #IGNORE:E1101



def test_interpreter_object_builtin_function_call_1():
    #py.test.skip('Test disabled')
    print 'Test interpreter object: call built in function sqrt...............................................................'
    from freeode.interpreter import Interpreter, DotName
    import math
    
    prog_text = \
'''
data a: Float const
a = sqrt(2)
'''
    #create the interpreter
    intp = Interpreter()
    #run mini program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print 'module after interpreter run: ---------------------------------'
    print intp.modules['test']
    
    assert intp.modules['test'].get_attribute(DotName('a')).value == math.sqrt(2)
  
  

def test_interpreter_object_builtin_function_call_2():
    #py.test.skip('Test disabled')
    print 'Test interpreter object: call built in function print...............................................................'
    from freeode.interpreter import Interpreter, DotName
    import math
    
    prog_text = \
'''
print('test')
'''
    #create the interpreter
    intp = Interpreter()
    #run mini program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print 'module after interpreter run: ---------------------------------'
    print intp.modules['test']
  
  

def test_interpreter_function_definition_and_call_1():
    #py.test.skip('Test disabled')
    print 'Test interpreter object: function definition and function call ...............................................................'
    from freeode.interpreter import Interpreter, DotName

    prog_text = \
'''
print('start')

func foo(b):
    print('in foo. b = ', b)
    return b*b
    print('after return')

data a: Float const
a = 2*2 + foo(3*4) + foo(2)
print('a = ', a)

print('end')
'''
    #create the interpreter
    intp = Interpreter()
    #run mini program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print 'module after interpreter run: ---------------------------------'
    print intp.modules['test']
    
    assert intp.modules['test'].get_attribute(DotName('a')).value == 2*2 + (3*4)**2 + 2**2
  
  

def test_interpreter_object_class_definition():
    #py.test.skip('Test disabled')
    print 'Test interpreter object: class definition ...............................................................'
    from freeode.interpreter import Interpreter, DotName

    prog_text = \
'''
print('start')

data pi: Float const
pi = 3.1415

class A:
    print('in A definition')
    data a1: Float const
    data a2: Float const

class B:
    data b1: Float const
    b1 = pi
    data b2: Float const

data a: A const
data b: B const

a.a1 = 1
a.a2 = 2 * b.b1
print('a.a1: ', a.a1, ', a.a2: ', a.a2)

print('end')
'''

    #create the interpreter
    intp = Interpreter()
    #interpret the program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print 'module after interpreter run: ---------------------------------'
    print intp.modules['test']
  
    assert (intp.modules['test'].get_attribute(DotName('pi')).value == 3.1415)
    assert (intp.modules['test'].get_attribute(DotName('a'))
                                .get_attribute(DotName('a1')).value == 1)
    assert (intp.modules['test'].get_attribute(DotName('a'))
                                .get_attribute(DotName('a2')).value == 2 * 3.1415)
    assert (intp.modules['test'].get_attribute(DotName('b'))
                                .get_attribute(DotName('b1')).value == 3.1415)

  
  
def test_interpreter_method_call():
    #py.test.skip('Method calls do not work! Implement method wrappers!')
    print 'Test interpreter: method call ...............................................................'
    from freeode.interpreter import Interpreter, DotName

    prog_text = \
'''
print('start')

class A:
    data a1: Float const
    data a2: Float const
    
    func compute(this, x):
        print('in compute_a2 x=', x)
        return x + 2
        
data a: A const
a.a1 = a.compute(3)

#print('a.a1 = ', a.a1)

print('end')
'''

    #create the interpreter
    intp = Interpreter()
    #interpret the program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    #print intp.modules['test']
  
    assert (intp.modules['test'].get_attribute(DotName('a'))
                                .get_attribute(DotName('a1')).value == 5)
#    assert False, 'Test'



def test_interpreter_method_call_this_namespace():
    #py.test.skip('Method calls do not work! Implement method wrappers!')
    print 'Test interpreter: method call, this namespace ...............................................................'
    from freeode.interpreter import Interpreter, DotName

    prog_text = \
'''
print('start')

class A:
    data a1: Float const
    data a2: Float const
    
    func compute(this, x):
        print('in compute_a2 x=', x)
        a1 = x
        a2 = x + 2
        
data a: A const
a.compute(3)
print('a.a1 = ', a.a1)
print('a.a2 = ', a.a2)

print('end')
'''

    #create the interpreter
    intp = Interpreter()
    #interpret the program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print intp.modules['test']
  
    assert (intp.modules['test'].get_attribute(DotName('a'))
                                .get_attribute(DotName('a1')).value == 3)
    assert (intp.modules['test'].get_attribute(DotName('a'))
                                .get_attribute(DotName('a2')).value == 5)
#    assert False, 'Test'

      
# -------- Test interpreter object - emit code ----------------------------------------
def test_interpreter_object_emit_code_simple():
    #py.test.skip('Test disabled')
    print 'Test interpreter object: emit code simple ...............................................................'
    from freeode.interpreter import Interpreter, Node

    prog_text = \
'''
print('start')

data a: Float const
data b: Float variable
data c: Float variable
a = 2*2 #constant no statement emitted
b = 2*a #compute 2*a at compile time
c = 2*b #emit everything
print('a = ', a)

print('end')
'''

    #create the interpreter
    intp = Interpreter()
    #enable collection of statements for compilation
    intp.compile_stmt_collect = []
    #interpret the program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print '--------------- main module ----------------------------------'
    print intp.modules['test']
    #put collected statements into Node for pretty printing
    n = Node(stmts=intp.compile_stmt_collect)
    print
    print '--------------- collected statements ----------------------------------'
    print n
        
    #TODO: Assertions
      

def test_interpreter_object_compile_statement():
    #py.test.skip('Method calls don\'t work!!!')
    print 'Test interpreter object: compile statement ...............................................................'
    from freeode.interpreter import Interpreter

    prog_text = \
'''
print('start')

class B:
    data b1: Float variable
    
    func foo(this, x):
        b1 = b1 * x
    
class A:
    data a1: Float param
    data b: B variable
    
    func init(this):
        a1 = 1
        b.b1 = 11
        
    func dynamic(this):
        a1 = a1 + 2
        b.foo(a1)

compile A

print('end')
'''

    #create the interpreter
    intp = Interpreter()
    #run program
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print intp.modules['test']
    print intp.compile_module

    #TODO: Assertions
      
      

def test_interpreter_object_dollar_operator():
    #py.test.skip('Method calls don\'t work!!!')
    print 'Test interpreter object: "$" operator ...............................................................'
    from freeode.interpreter import Interpreter

    prog_text = \
'''
print('start')

class B:
    data b1: Float variable
    
    func foo(this, x):
        $b1 = b1 * x
    
class A:
    data a1: Float param
    data b: B variable
    
    func init(this):
        a1 = 1
        b.b1 = 11
        
    func dynamic(this):
        a1 = a1 + 2
        b.foo(a1)

compile A

print('end')
'''

    #create the interpreter
    intp = Interpreter()
    intp.interpret_module_string(prog_text, None, 'test')
  
    print
    print intp.modules['test']
    print intp.compile_module
  
    #TODO: Assertions

  
if __name__ == '__main__':
    # Debugging code may go here.
    #test_expression_evaluation_1()
    test_basic_execution_of_statements()
    pass

