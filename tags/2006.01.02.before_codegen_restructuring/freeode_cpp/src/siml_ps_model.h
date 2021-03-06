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
#ifndef SIML_MODEL_GRAMMAR_HPP
#define SIML_MODEL_GRAMMAR_HPP

#include "siml_code_model.h"
#include "siml_ps_name.h"
#include "siml_error_generator.h"

#include <boost/spirit/core.hpp>
#include <boost/spirit/symbols/symbols.hpp>
// #include <boost/spirit/actor/actors.hpp>
// #include <boost/shared_ptr.hpp>

#include <string>
// #include <vector>
#include <iostream>

//!Intermediate storage for data aquired while parsing a model.
/*!Created a new namespace to avoid name clashes since these are all global symbols.
The namespace is named for easier access in KDevelop. */
namespace temp_store_model {
using namespace siml;
using namespace std;
// using boost::shared_ptr;

//!pointer to the central storage of parse results
CmCodeRepository* parse_result_storage;

//!The data gathered while parsing the model is stored here
CmModelDescriptor model;

//!error that is maybe detected.
CmErrorDescriptor err_temp;

//!Clear the temporary storage
void start_model(char const * /*first*/, char const * /*last*/)
{
    model = CmModelDescriptor();
    err_temp = CmErrorDescriptor();
}

//model name--------------------------------------------------------------------
///See if the model or process name is unique
void test_model_name_unique(char const *, char const *)
{
///@todo implement test_model_name_unique
///@todo make this a member function of the model
}

//parameter---------------------------------------------------------------------
//!temporary storage while a parameter definition is parsed
CmMemoryDescriptor p_temp;
//!Clear the temporary storage for parsing parameters
void start_parameter(char const *, char const *) { p_temp = CmMemoryDescriptor(); }
//!Add a parameter definition to the model.
/*!@todo make this a member function of the model
The function takes "p_temp" and puts it into "model.parameter"; the container for
parsed parameters. The chunk of text that led to the new parameter desciptor
is stored too*/
void add_parameter(char const * first, char const * const last)
{
    p_temp.definition_text = string(first, last);
    ///@todo check if name is unique
    model.parameter.push_back(p_temp);
}

//unit (sub-model)--------------------------------------------------------------
//!temporary storage while a unit definition is parsed
CmSubModelDescriptor submod_temp;
//!Clear the temporary storage for parsing parameters
void start_sub_model(char const *, char const *) { submod_temp = CmSubModelDescriptor(); }
//!Add a parameter definition to the model.
void add_sub_model(char const * first, char const * const last)
{
    string definition_text(first, last);
    ///@todo check if name is unique, check if model type exists
    model.subModel.push_back(submod_temp);
}

//variable----------------------------------------------------------------------
//!temporary storage while a variable definition is parsed
CmMemoryDescriptor v_temp;
//!Clear the temporary storage for the CmVariableDescriptor objects
void start_variable(char const *, char const *) { v_temp = CmMemoryDescriptor(); }
//!Add a variable definition to the model.
/*!@todo make this a member function of the model
See add_parameter*/
void add_variable(char const * first, char const * const last)
{
    v_temp.definition_text = string(first, last);
    ///@todo check if name is unique
    model.variable.push_back(v_temp);
}
//!Mark one variable inside model as a state variable.
/*!@todo make this a member function of the model
If the variable does not exist nothing will happen.*/
void set_variable_integrated(char const * first, char const * const last)
{
    string stateVarName(first, last);

    //loop over all variables to find the variable that will be marked
    CmMemoryTable::iterator it;
    for( it = model.variable.begin(); it != model.variable.end(); ++it )
    {
        CmMemoryDescriptor& varD = *it;
        if( varD.name == stateVarName )
        {
            varD.is_state_variable = true;
            break;
        }
    }
}

//parameter assignment (SET)----------------------------------------------------
//!temporary storage while a variable definition is parsed
CmEquationDescriptor param_assign_temp;
//!Clear the temporary storage for the CmEquationDescriptor objects
void start_param_assign(char const *, char const *) { param_assign_temp = CmEquationDescriptor(); }
//!Add an assignment to a algebraic variable to the model. (a:=p2*c)
void add_param_assign(char const * first, char const * const last)
{
    param_assign_temp.definition_text = string(first, last);
    param_assign_temp.is_assignment = true;
    param_assign_temp.is_ode_assignment = false;
    model.parameterAssignment.push_back(param_assign_temp);
}

//equation----------------------------------------------------------------------
//!temporary storage while a variable definition is parsed
CmEquationDescriptor e_temp;
//!Clear the temporary storage for the CmEquationDescriptor objects
void start_equation(char const *, char const *) { e_temp = CmEquationDescriptor(); }
//!Add an equation (realy an asignment) to the model. (a:=p2*c)
/*!@todo make this a member function of the model*/
void add_equation(char const * first, char const * const last)
{
    e_temp.definition_text = string(first, last);
    model.equation.push_back(e_temp);
}

//initial value assignment (INITIAL)----------------------------------------------------------------
//!temporary storage while a variable definition is parsed
CmEquationDescriptor init_expr_temp;
//!Clear the temporary storage for the CmEquationDescriptor objects
void start_init_expr(char const *, char const *) { init_expr_temp = CmEquationDescriptor(); }
//!Add an assignment to a algebraic variable to the model. (a:=p2*c)
void add_init_expr(char const * first, char const * const last)
{
    init_expr_temp.definition_text = string(first, last);
    init_expr_temp.is_assignment = true;
    init_expr_temp.is_ode_assignment = false;
    model.initialExpression.push_back(init_expr_temp);
}

//SOLUTIONPARAMETERS----------------------------------------------------------------
//!temporary storage while a variable definition is parsed
CmSolutionParameterDescriptor sol_parms_temp;
//!Clear the temporary storage for the CmEquationDescriptor objects
void start_sol_parms(char const *, char const *) { sol_parms_temp = CmSolutionParameterDescriptor(); }
//!Add an assignment to a algebraic variable to the model. (a:=p2*c)
void add_sol_parms(char const * /*first*/, char const * const /*last*/)
{
    model.solutionParameters = sol_parms_temp;
}

//return model------------------------------------------------------------------
//!add the correctly parsed model to the global code repository.
void return_model(char const * /*first*/, char const * const /*last*/)
{
    cout << "Parsing model or process " << model.name << " finished correctly." << endl;
    cout << "model.isProcess: " << model.isProcess << endl;

    if( model.isProcess ) { parse_result_storage->process.push_back(model); }
    else                  { parse_result_storage->model.push_back(model); }
}

//!add error and the partial model to the global code repository.
void return_error(char const * /*first*/, char const * const /*last*/)
{
    cout << "Parsing model or process " << model.name << " failled!" << endl;

    model.errorsDetected = true;

    parse_result_storage->error.push_back(err_temp);
    if( model.isProcess ) { parse_result_storage->process.push_back(model); }
    else                  { parse_result_storage->model.push_back(model); }
}

} //namespace temp_store_model



namespace siml {

namespace spirit = boost::spirit;


/*!
@short Grammar of a "MODEL" and a "PROCESS".

This grammar parses model and process definitions and adds CmModelDescriptor objects
to the global code repository (CmCodeRepository* parse_result_storage) when
parsing was successfull.

Processes are handled as special cases of models.

The model uses global variables to store temporary
information, during a parsing run.
The temporary varibles and the semantic actions reside in the namespace
"temp_store_model".

@todo With functors no global variables nor global functions were necessary.
*/
struct ps_model : public spirit::grammar<ps_model>
{
    //!Construct the grammar
    /*!Before using the grammar it must have a pointer to the global result storage.
    Therefore the function set_result_storage (...) must be called. (once for all
    ps_model instances)*/
    ps_model() {}

    //!Give the grammar a pointer to the global storage for parse results.
    static void set_result_storage(CmCodeRepository* result_storage)
    {
        temp_store_model::parse_result_storage = result_storage;
    }

    //!When the grammar is used the framework creates this struct. All rules are defined here.
    template <typename ScannerT>
    struct definition
    {
        //!The grammar's rules.
        definition(ps_model const& self)
        {
            using namespace temp_store_model;
            using spirit::str_p; using spirit::ch_p;
            using spirit::eps_p; using spirit::nothing_p; using spirit::anychar_p;
            using spirit::assign_a;

            //The start rule. Parses the complete model: MODEL ... END
            model_definition
                = ( str_p("MODEL")          [&start_model]  //clear all temporary storage
                                            /*[assign_a(model.isProcess, false)]*/ ///@todo investigate why this does not work.
                  | str_p("PROCESS")        [&start_model]
                                            [assign_a(model.isProcess, true)] //the model is really a process
                  ) >>
                  //model or process body
                  ( ( name                  [assign_a(model.name)]
                                            [&test_model_name_unique] >>
                      !parameter_section >> !unit_section >> !variable_section >>
                      !set_section >> !equation_section >> !initial_section >>
                      !solutionparameters_section >>
                      str_p("END")          [&return_model]
                    )
                  | ( eps_p                 [&return_error] >>
                      nothing_p
                    )
                  );

            //parse block of parameter definitions: PARAMETER p1 AS REAL DEFAULT 1; p2 AS REAL DEFAULT 10; ...
            parameter_section
                =   str_p("PARAMETER") >>
                    *(    parameter_definition
//                     | (eps_p[assign_a(possible_error, "Error in parameter definition!")] >> nothing_p)
                    | (eps_p[make_error("Error in parameter definition!", err_temp)] >> nothing_p)
                     );
            parameter_definition ///@TODO units
                = ( eps_p                                [&start_parameter] >> //clear temporary storage
                    (name /*- param_name*/)                  /*[param_name.add]*/ //store in symbol table + check if name is already taken
                                                         [assign_a(p_temp.name)] >>  //store name in temporary storage
                    !("AS" >> str_p("REAL")              [assign_a(p_temp.type)]) >> //store parameter type
                    !("DEFAULT" >> rough_math_expression [assign_a(p_temp.default_expr)]) >> //store default value
                    +ch_p(';')
                  )                                      [&add_parameter]; //add parameter definition to model

            //parse block of sub-model definitions: UNIT u1 AS Model1; ...
            unit_section
                =   str_p("UNIT") >>
                    *(    unit_definition
                        | (eps_p[make_error("Error in UNIT (sub-model) definition!", err_temp)] >> nothing_p)
                     );
            unit_definition
                = ( eps_p                                [&start_sub_model] >> //clear temporary storage
                    name                                 [assign_a(submod_temp.name)] >>  //store name in temporary storage
                    !("AS" >> name                       [assign_a(submod_temp.type)]) >> //store sub model type
                    +ch_p(';')
                  )                                      [&add_sub_model]; //add sub-model definition to model

            //parse block of variable definitions: VARIABLE v1 AS ANY; v2 AS ANY; ...
            variable_section
                = str_p("VARIABLE") >>
                *(    variable_definition
                    | (eps_p[make_error("Error in variable definition!", err_temp)] >> nothing_p)
                 );
            variable_definition ///@TODO add upper and lower bounds; units;
                = ( eps_p                                [&start_variable] >> //clear temporary storage
                    (name /*- param_name - var_name*/)       /*[var_name.add]*/       //store in symbol table + check if name is already taken
                                                         [assign_a(v_temp.name)] >>
                    !("AS" >> str_p("ANY")               [assign_a(v_temp.type)]) >>
                    !("INITIAL" >> rough_math_expression [assign_a(v_temp.initial_expr)]) >> //store initial value
                    +ch_p(';')
                  )                                      [&add_variable]; //add variable definition to model

            //parse the SET section where values are assigned to the parameters: SET p1=2.5; p2:=3.1;
            set_section
                = str_p("SET") >>
                *(    parameter_assignment
                    | (eps_p[make_error("Error in SET section!", err_temp)] >> nothing_p)
                 );
            parameter_assignment
                = ( path                                [&start_param_assign]
                                                        [assign_a(param_assign_temp.lhs)] >>
                    ":=" >> rough_math_expression       [assign_a(param_assign_temp.rhs)] >>
                    +ch_p(';')
                  )                                     [&add_param_assign];

            //Parse the EQUATION section: EQUATION v1 := 2*v2 + v3; $v2 := v2/v1;
            equation_section
                = str_p("EQUATION") >>
                *(    assignment_variable
                    | assignment_time_derivative
                    | (eps_p[make_error("Error in EQUATION section!", err_temp)] >> nothing_p)
                 );
            assignment_variable
                = ( eps_p                           [&start_equation]
                                                    [assign_a(e_temp.is_assignment, true)] >>
                    path                            [assign_a(e_temp.lhs)] >>
                    ":=" >> rough_math_expression   [assign_a(e_temp.rhs)] >>
                    +ch_p(';')
                  )                                 [&add_equation];
            assignment_time_derivative
                = ( eps_p                           [&start_equation]
                                                    [assign_a(e_temp.is_assignment, true)] >>
                    '$' >> path                     [assign_a(e_temp.lhs)]
                                                    [assign_a(e_temp.is_ode_assignment, true)]
                                                    [&set_variable_integrated] >>
                    ":=" >> rough_math_expression   [assign_a(e_temp.rhs)] >>
                    +ch_p(';')
                  )                                 [&add_equation];

            //parse the INITIAL section where start values are assigned to the integrated variables: INITAIL v1=2.5; v2:=3.1;
            initial_section
                = str_p("INITIAL") >>
                  *(    initial_assignment
                    |   (eps_p[make_error("Error in INITIAL section!", err_temp)] >> nothing_p)
                   );
            initial_assignment
                = ( path                                [&start_init_expr]
                                                        [assign_a(init_expr_temp.lhs)] >>
                    ":=" >> rough_math_expression       [assign_a(init_expr_temp.rhs)] >>
                    +(ch_p('\n') | ';')
                  )                                     [&add_init_expr];

            //parse the SOLUTIONPARAMETERS section
            solutionparameters_section
                = str_p("SOLUTIONPARAMETERS")           [&start_sol_parms] >>
                  *(    solutionparameters_assignment   [&add_sol_parms]
                    |   (eps_p[make_error("Error in SOLUTIONPARAMETERS section!", err_temp)] >> nothing_p)
                   );
            solutionparameters_assignment
                = ( str_p("ReportingInterval") >> ":=" >>
                    (real_p >> eps_p)                   [assign_a(sol_parms_temp.reportingInterval)] >>
                    +ch_p(';')
                  )
                | ( str_p("SimulationTime") >> ":=" >>
                    (real_p  >> eps_p)                  [assign_a(sol_parms_temp.simulationTime)] >>
                    +ch_p(';')
                  );

            //very bad parser for mathematical expressions
            rough_math_expression
                    = +(path | real_p | '+' | '-' | '*' | '/' | '(' | ')');

            //parser for a variable or a parameter path "mo1.X"
            path = name >> *("." >> name);
        }

        //!The start rule of the model grammar.
        spirit::rule<ScannerT> const &
        start() const { return model_definition; }

        private:

        //!Rules that are defined here
        spirit::rule<ScannerT>
            model_definition,
            parameter_section, parameter_definition,
            unit_section, unit_definition,
            variable_section, variable_definition,
            set_section, parameter_assignment,
            equation_section, assignment_variable, assignment_time_derivative,
            initial_section, initial_assignment,
            solutionparameters_section, solutionparameters_assignment,
            rough_math_expression, path;
        //!Grammar that describes all names (model, parameter, variable)
        ps_name name;
        //!symbol table for the known parmeter names.
//         spirit::symbols<> param_name;
        //!symbol table for the known variable names.
//         spirit::symbols<> var_name;
    };
};

} // namespace siml

#endif // SIML_MODEL_GRAMMAR_HPP
