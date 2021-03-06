/***************************************************************************
 *   Copyright (C) 2005 by Eike Welk   *
 *   eike.welk@post.rwth-aachen.de   *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
 ***************************************************************************/

#ifndef SIML_CODE_MODEL_HPP
#define SIML_CODE_MODEL_HPP

#include <string>
#include <vector>

namespace siml {

/*!
@short Descripion of an error.

This object contains data about an error. It is used to generate nicely
formated error message.

@todo An error generation functor would be great. e.g.: eps_p[error(code_m, "AS must be followed by a variable type")]
@todo How should I deal with code generator errors?
*/
struct CmErrorDescriptor
{
    //!Error message that was generated by the parser. (If any)
    std::string message_from_parser;
    //!Start of the sequence that contains the error.
    char const * where_first;
    //!End of the sequence that contains the error.
    char const * where_last;

    CmErrorDescriptor() : where_first(0), where_last(0) {};
};
//!container for Errors. See: @see CmErrorDescriptor
typedef std::vector<CmErrorDescriptor> CmErrorTable;


/*!
@short All data of a single parameter

This is the parsing result for one line of the PARAMETER section. The code
generator will later use this information.
@todo A pair of pointers: char const * where_first, where_last; instead of std::string definition_text would be a good idea, to aid the generation of code generator errors.
@todo maybe CmParameterDescriptor and CmVariableDescriptor should be merged.
*/
struct CmParameterDescriptor
{
    //!parameter name
    std::string name;
    //!identifier name in generated program
    std::string name_program;
    //!REAL or INT
    std::string type;
    //!the default value, relevant if no value is set.
    std::string default_expr;
//    //!mathematical expression from the set section.
//     std::string set_expr;
    //!text that was parsed to gather the information in this object.
    std::string definition_text;

    CmParameterDescriptor() : type("REAL"), default_expr("1") {};
};
//!container for the parameter descriptors of a model. See: @see CmParameterDescriptor
typedef std::vector<CmParameterDescriptor> CmParameterTable;


/*!
@short All data of a single variable

This is the parsing result for one line of the VARIABLE section. The code
generator will later use this information.
*/
struct CmVariableDescriptor
{
    //!identifier name
    std::string name;
    //!identifier name in generated program
    std::string name_program;
    //!User defined type
    std::string type;
    //!expression for assignment of an initial value.
    std::string initial_expr;
    //!true if variable is an integrated variable
    bool is_state_variable;
    //!Index into the state vector e.g.: 1; 1:10
    std::string state_vec_index;
    //!text that was parsed to gather the information in this object.
    std::string definition_text;

    CmVariableDescriptor() : type("ANY"), is_state_variable(false) {};
};
//!container for the variable descriptors of a model. See: @see CmVariableDescriptor
typedef std::vector<CmVariableDescriptor> CmVariableTable;


/*!
@short Descripion of one equation or assignment.
*/
struct CmEquationDescriptor
{
    //!the equation's left hand side
    std::string lhs;
    //!the equation's right hand side
    std::string rhs;
    //!if true the equation is really an assignment ":=" otherwise it's a true equation "="
    bool is_assignment;
    //!if true the lhs is the time differential of a variable: $v1 := a*b*v1 + v2;
    bool is_ode_assignment;
    //!text that was parsed to gather the information in this object.
    std::string definition_text;

    CmEquationDescriptor() : is_assignment(false), is_ode_assignment(false) {};
};
//!container for the equation descriptors of a model. See: @see CmEquationDescriptor
typedef std::vector<CmEquationDescriptor> CmEquationTable;


/*!
@short Descripion of a model
This is the parsing result of a model: "MODEL ... END"
*/
struct CmModelDescriptor
{
    //!The model's name
    std::string name;
    //!Container for parameters. See: @see CmParameterDescriptor
    CmParameterTable parameter;
    //!Container for variables. See: @see CmVariableDescriptor
    CmVariableTable variable;
    //!Container for the eqations. See: @see CmEquationDescriptor
    CmEquationTable equation;
};
//!container for the models of a file.
typedef std::vector<CmModelDescriptor> CmModelTable;


/*!
@short Toplevel parsing result.

The code generator gets this object and it generates a computer program from it.
Additonally errors and warnings from the parser and the code generator are
collected here too.
*/
struct CmCodeRepository
{
    //!list of models
    CmModelTable model;
    //!list of recognized errors
    CmErrorTable error;

    ///@todo procedure list and procedure object in code model
    ///@todo store the input file(s) (mmaped) or char const * begin, end; too?
};

} //namespace siml

#endif // SIML_CODE_MODEL_HPP
