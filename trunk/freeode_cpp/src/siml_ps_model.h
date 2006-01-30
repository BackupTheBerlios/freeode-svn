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
#include "siml_ps_path.h"
#include "siml_ps_formula.h"
#include "siml_ps_memory_definition.h"
#include "siml_ps_equation.h"
#include "siml_error_generator.h"

#include <boost/spirit/core.hpp>
#include <boost/spirit/symbols/symbols.hpp>
// #include <boost/spirit/actor/actors.hpp>
#include <boost/shared_ptr.hpp>

#include <string>
// #include <vector>
#include <iostream>


//!Intermediate storage for data aquired while parsing a model.
/*!Created a new namespace to avoid name clashes since these are all global symbols.
The namespace is named for easier access in KDevelop. */
namespace temp_store_model {
using namespace siml;
using namespace std;
using boost::shared_ptr;

//!pointer to the central storage of parse results
CmCodeRepository* parse_result_storage;

//!The data gathered while parsing the model is stored here
// CmModelDescriptor model;

//!error that is maybe detected.
// CmErrorDescriptor err_temp;

//!Clear the temporary storage
// void start_model(char const * /*first*/, char const * /*last*/)
// {
//     model = CmModelDescriptor();
//     err_temp = CmErrorDescriptor();
// }

//model name--------------------------------------------------------------------
//!See if the model or process name is unique
// void test_model_name_unique(char const *, char const *)
// {
///@todo implement test_model_name_unique
///@todo make this a member function of the CmCodeRepository
// }

//set to process----------------------------------------------------------------
//!Store that the model is really a process
// void set_process(char const *, char const *)
// {
//     model.isProcess = true;
// }

//parameter---------------------------------------------------------------------
//!temporary storage while a parameter definition is parsed
// CmMemoryDescriptor p_temp;
//!Clear the temporary storage for parsing parameters
// void start_parameter(char const *, char const *) { p_temp = CmMemoryDescriptor(); }
//!Add a parameter definition to the model.
/*!
The function takes "p_temp" and puts it into "model.parameter"; the container for
parsed parameters. The chunk of text that led to the new parameter desciptor
is stored too*/
// void add_parameter(char const * first, char const * const last)
// {
//     p_temp.definition_text = string(first, last);
//
//     shared_ptr<CmErrorDescriptor> err = model.addParameter(p_temp);
//
//     if( err )
//     {
//         model.errorsDetected = true;  //remember: there were errors in this model.
//         add_error_context(*err, first, last);  //make error look better
//         parse_result_storage->error.push_back(*err); //add error to parsing store
//     }
// }

//unit (sub-model)--------------------------------------------------------------
//!temporary storage while a unit definition is parsed
// CmSubModelLink submod_temp;
//!Clear the temporary storage for parsing parameters
// void start_sub_model(char const *, char const *) { submod_temp = CmSubModelLink(); }
//!Add a parameter definition to the model.
// void add_sub_model(char const * first, char const * const last)
// {
// //     string definition_text(first, last);
//
//     shared_ptr<CmErrorDescriptor> err = model.addSubModel(submod_temp);
//
//     if( err )
//     {
//         model.errorsDetected = true;  //remember: there were errors in this model.
//         add_error_context(*err, first, last);  //make error look better
//         parse_result_storage->error.push_back(*err); //add error to parsing store
//     }
// }

//variable----------------------------------------------------------------------
//!temporary storage while a variable definition is parsed
// CmMemoryDescriptor v_temp;
//!Clear the temporary storage for the CmVariableDescriptor objects
// void start_variable(char const *, char const *) { v_temp = CmMemoryDescriptor(); }
//!Add a variable definition to the model.
/*!@see add_parameter*/
// void add_variable(char const * first, char const * const last)
// {
//     v_temp.definition_text = string(first, last);
//
//     shared_ptr<CmErrorDescriptor> err = model.addVariable(v_temp);
//
//     if( err )
//     {
//         model.errorsDetected = true;
//         add_error_context(*err, first, last);
//         parse_result_storage->error.push_back(*err);
//     }
// }
//!Mark one variable inside model as a state variable.
/*!
If the variable does not exist nothing will happen.*/
// void set_variable_integrated(char const * first, char const * const last)
// {
//     string stateVarName(first, last);
//
//     shared_ptr<CmErrorDescriptor> err = model.setVariableIntegrated(stateVarName);
//
//     if( err )
//     {
//         model.errorsDetected = true;
//         add_error_context(*err, first, last);
//         parse_result_storage->error.push_back(*err);
//     }
// }

//parameter assignment (SET)----------------------------------------------------
//!temporary storage while a variable definition is parsed
// CmEquationDescriptor param_assign_temp;
//!Clear the temporary storage for the CmEquationDescriptor objects
// void start_param_assign(char const *, char const *) { param_assign_temp = CmEquationDescriptor(); }
//!Add an assignment to a algebraic variable to the model. (a:=p2*c)
// void add_param_assign(char const * first, char const * const last)
// {
//     param_assign_temp.definition_text = string(first, last);
//     model.addParameterAssignment( param_assign_temp);
// }

//equation----------------------------------------------------------------------
//!temporary storage while a variable definition is parsed
// CmEquationDescriptor e_temp;
//!Clear the temporary storage for the CmEquationDescriptor objects
// void start_equation(char const *, char const *) { e_temp = CmEquationDescriptor(); }
//!Add an equation (realy an asignment) to the model. (a:=p2*c)
// void add_equation(char const * first, char const * const last)
// {
//     e_temp.definition_text = string( first, last);
//
//     ///@todo the decision if a variable is integrated should be done at code generation time
//     ///@todo the lhs can always contain a path. when the model is flattened it is more easy to look up variables that reside in different sub-models.
//     /*test if ode assignment and [&set_variable_integrated]*/
// //     shared_ptr<CmErrorDescriptor> err = model.setVariableIntegrated(stateVarName);
// //
// //     if( err )
// //     {
// //         model.errorsDetected = true;
// //         add_error_context(*err, first, last);
// //         parse_result_storage->error.push_back(*err);
// //     }
//
//     model.addEquation( e_temp);
// }

//initial value assignment (INITIAL)----------------------------------------------------------------
//!temporary storage while a variable definition is parsed
// CmEquationDescriptor init_expr_temp;
//!Clear the temporary storage for the CmEquationDescriptor objects
// void start_init_expr(char const *, char const *) { init_expr_temp = CmEquationDescriptor(); }
//!Add an assignment to a algebraic variable to the model. (a:=p2*c)
// void add_init_expr(char const * first, char const * const last)
// {
//     init_expr_temp.definition_text = string(first, last);
// //     init_expr_temp.is_assignment = true;
// //     init_expr_temp.is_ode_assignment = false;
//     model.initialEquation.push_back(init_expr_temp);
// }

//SOLUTIONPARAMETERS----------------------------------------------------------------
//!temporary storage while a variable definition is parsed
// CmSolutionParameterDescriptor sol_parms_temp;
//!Clear the temporary storage for the CmEquationDescriptor objects
// void start_sol_parms(char const *, char const *) { sol_parms_temp = CmSolutionParameterDescriptor(); }
//!Add an assignment to a algebraic variable to the model. (a:=p2*c)
// void add_sol_parms(char const * /*first*/, char const * const /*last*/)
// {
//     model.solutionParameters = sol_parms_temp;
// }

//return model------------------------------------------------------------------
// int isProcessTemp;
//!add the correctly parsed model to the global code repository.
// void return_model(char const * /*first*/, char const * const /*last*/)
// {
//     cout << "Parsing model or process " << model.name << " finished correctly." << endl;
//     cout << "model.isProcess: " << model.isProcess << endl;
// //     cout << "isProcessTemp: " << isProcessTemp << endl;
//
//     if( model.isProcess ) { parse_result_storage->process.push_back(model); }
//     else                  { parse_result_storage->model.push_back(model); }
// }

//!add error and the partial model to the global code repository.
// void return_error(char const * /*first*/, char const * const /*last*/)
// {
//     cout << "Parsing model or process " << model.name << " failled!" << endl;
//
//     model.errorsDetected = true;
//
//     parse_result_storage->error.push_back(err_temp);
//     if( model.isProcess ) { parse_result_storage->process.push_back(model); }
//     else                  { parse_result_storage->model.push_back(model); }
// }

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
@author Eike Welk <eike.welk@post.rwth-aachen.de>
 */
struct ps_model : public spirit::grammar<ps_model>
{
    //!The data gathered while parsing the model is stored here
    CmModelDescriptor model;
private:
    //!temporary storage for a sub-model "UNIT"
    CmSubModelLink submod_temp;
    //!error that is maybe detected.
    CmErrorDescriptor err_temp;
public:
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

    /*!Functor that clears the temporary storage for model parsing.*/
    struct start_model
    {
        CmModelDescriptor & m_model;
        CmErrorDescriptor & m_error;

        start_model( CmModelDescriptor & model, CmErrorDescriptor & error):
            m_model(model), m_error( error) {}

        template <typename IteratorT>
        void operator()( IteratorT, IteratorT) const
        {
            m_model = CmModelDescriptor();
            m_error = CmErrorDescriptor();
        }
    };
//     finish_model_error( model, false_val)
    /*!Functor that finishes the model. If necessary it puts the temporary
    error into the list of errors.*/
    struct finish_model_error
    {
        CmModelDescriptor & m_model;
        CmErrorDescriptor & m_error;
        bool m_error_detected;

        finish_model_error( CmModelDescriptor & model, CmErrorDescriptor & error, bool error_yes):
            m_model( model), m_error( error), m_error_detected( error_yes) {}

        template <typename IteratorT>
        void operator()( IteratorT, IteratorT) const
        {
            std::string mp_type, ps_result;

            //set the model's error flag
            m_model.errorsDetected = m_error_detected;
            //put the model (or process) into the code repository
            if( m_model.isProcess ) {
                temp_store_model::parse_result_storage->process.push_back(m_model);
                mp_type = "process ";
            }
            else {
                temp_store_model::parse_result_storage->model.push_back(m_model);
                mp_type = "model ";
            }

            //put error in list if necessary
            if( m_error_detected ) {
                temp_store_model::parse_result_storage->error.push_back(m_error);
                ps_result = " failled!\n";
            }
            else {
                ps_result = " finished correctly.\n";
            }

            cout << "Parsing " << mp_type << m_model.name << ps_result;
        }
    };

    /*!Functor that changes the model's name and tests if it is unique.*/
    struct set_model_name
    {
        CmModelDescriptor & m_model;

        set_model_name( CmModelDescriptor & model):
            m_model(model) {}

        template <typename IteratorT>
        void operator()( IteratorT begin, IteratorT end) const
        {
            m_model.name = std::string( begin, end);
            ///@todo test if model name is unique
            ///@todo make "isModelNameUnique" a member function of the CmCodeRepository and/or
            ///@todo write CmModelDescriptor::setModelName that does the test.
        }
    };

    /*!Functor that adds a parameter definition (PARAMETER) to a model*/
    struct add_parameter
    {
        CmModelDescriptor & m_model;
        CmMemoryDescriptor & m_memory;

        add_parameter( CmModelDescriptor & model, CmMemoryDescriptor & mem):
            m_model(model), m_memory( mem) {}

        template <typename IteratorT>
        void operator()( IteratorT, IteratorT) const
        {
            m_model.addParameter( m_memory);
            ///@todo errors:  m_model.errorsDetected |= m_model.addParameter( m_memory);
        }
    };

    /*!Functor that adds a variable definition (VARIABLE) to a model*/
    struct add_variable
    {
        CmModelDescriptor & m_model;
        CmMemoryDescriptor & m_memory;

        add_variable( CmModelDescriptor & model, CmMemoryDescriptor & mem):
            m_model(model), m_memory( mem) {}

        template <typename IteratorT>
        void operator()( IteratorT, IteratorT) const
        {
            m_model.addVariable( m_memory);
            ///@todo errors:  m_model.errorsDetected |= m_model.addVariable( m_memory);
        }
    };

    /*!Functor that adds a parameter assignment (SET) to a model*/
    struct add_param_assignment
    {
        CmModelDescriptor & m_model;
        CmEquationDescriptor & m_equation;

        add_param_assignment( CmModelDescriptor & model, CmEquationDescriptor & equation):
            m_model(model), m_equation( equation) {}

        template <typename IteratorT>
        void operator()( IteratorT, IteratorT) const
        {
            m_model.addParameterAssignment( m_equation);
            ///@todo errors
        }
    };

    /*!Functor that adds an equation (EQUATION) to a model*/
    struct add_equation
    {
        CmModelDescriptor & m_model;
        CmEquationDescriptor & m_equation;

        add_equation( CmModelDescriptor & model, CmEquationDescriptor & equation):
            m_model(model), m_equation( equation) {}

        template <typename IteratorT>
        void operator()( IteratorT, IteratorT) const
        {
            m_model.addEquation( m_equation);
            ///@todo the decision if a variable is integrated should be done at code generation time
            ///@todo the lhs can always contain a path. when the model is flattened it is more easy to look up variables that reside in different sub-models.
            ///@todo errors
        }
    };

    /*!Functor that adds a parameter assignment to a model*/
    struct add_init_equation
    {
        CmModelDescriptor & m_model;
        CmEquationDescriptor & m_equation;

        add_init_equation( CmModelDescriptor & model, CmEquationDescriptor & equation):
        m_model(model), m_equation( equation) {}

        template <typename IteratorT>
        void operator()( IteratorT, IteratorT) const
        {
            m_model.addInitialEquation( m_equation);
            ///@todo errors
        }
    };

    /*!Functor that adds a sub-model to a model*/
    struct add_sub_model
    {
        CmModelDescriptor & m_model;
        CmSubModelLink & m_submod;

        add_sub_model( CmModelDescriptor & model, CmSubModelLink & submod):
            m_model( model), m_submod( submod) {}

        template <typename IteratorT>
        void operator()( IteratorT, IteratorT) const
        {
            m_model.addSubModel( m_submod);
            ///@todo errors
        }
    };

    //!When the grammar is used the framework creates this struct. All rules are defined here.
    template <typename ScannerT>
    struct definition
    {
        //!The grammar's rules.
        definition(ps_model const & self) :
                true_val(true), false_val(false)
        {
            using namespace temp_store_model;
            using spirit::str_p; using spirit::ch_p;
            using spirit::eps_p; using spirit::nothing_p; using spirit::anychar_p;
            using spirit::assign_a;

            //we need a mutable self for the semantic actions
            ps_model & selfm = const_cast<ps_model &>(self);

            ///@todo evaluate "distinct_parser" as an alternative to "str_p" - http://www.boost.org/libs/spirit/doc/distinct.html
            ///@todo very nice were a parser generator keyw_p("MODEL") that inserted the keyword into the table of keywords.

            //The start rule. Parses the complete model: MODEL ... END
            model_definition
                = ( str_p("MODEL")          [start_model( selfm.model, selfm.err_temp)]  //clear all temporary storage
                  | str_p("PROCESS")        [start_model( selfm.model, selfm.err_temp)]
                                            [assign_a(selfm.model.isProcess, true_val)] //the model is really a process
                  )
                  //model or process body
                >> ( (  name                [set_model_name( selfm.model)]
                        >> !parameter_section >> !unit_section >> !variable_section
                        >> !set_section >> !equation_section >> !initial_section
                        >> !solutionparameters_section
                        >> str_p("END")     [finish_model_error( selfm.model, selfm.err_temp, false)]
                     )
                   | (  eps_p               [finish_model_error( selfm.model, selfm.err_temp, true)]
                        >> nothing_p
                     )
                   )
                ;

            //parse block of parameter definitions: PARAMETER p1 AS REAL DEFAULT 1; p2 AS REAL DEFAULT 10; ...
            parameter_section
                =   str_p("PARAMETER") >>
                    *(  memory_definition   [add_parameter( selfm.model, memory_definition.memory)]
                     | ( eps_p              [make_error( "Error in parameter definition!", selfm.err_temp)] >> nothing_p )
                     )
                ;

            //parse block of sub-model definitions: UNIT u1 AS Model1; ...
            unit_section
                =   str_p("UNIT") >>
                    *( unit_definition
                     | (eps_p           [make_error("Error in UNIT (sub-model) definition!", selfm.err_temp)] >> nothing_p)
                     )
                ;
            unit_definition
                =  name                 [assign_a( selfm.submod_temp.name)]   //store name in temporary storage
                >> !("AS" >> name       [assign_a( selfm.submod_temp.type)])  //store sub model type
                >> (+ch_p(';'))         [add_sub_model( selfm.model, selfm.submod_temp)] //add sub-model definition to model
                ;

            //parse block of variable definitions: VARIABLE v1 AS ANY; v2 AS ANY; ...
            variable_section
                = str_p("VARIABLE") >>
                *( memory_definition    [add_variable( selfm.model, memory_definition.memory)]
                 | ( eps_p              [make_error("Error in variable definition!", selfm.err_temp)] >> nothing_p )
                 );

            //parse the SET section where values are assigned to the parameters: SET p1=2.5; p2:=3.1;
            set_section
                = str_p("SET")
                >> *( equation_pars     [add_param_assignment( selfm.model, equation_pars.equation)]
                    | ( eps_p           [make_error( "Error in SET section!", selfm.err_temp)] >> nothing_p )
                    )
                ;

            //Parse the EQUATION section: EQUATION v1 := 2*v2 + v3; $v2 := v2/v1;
            equation_section
                =  str_p("EQUATION")
                >> *(   equation_pars   [add_equation( selfm.model, equation_pars.equation)]
                    | ( eps_p           [make_error( "Error in EQUATION section!", selfm.err_temp)] >> nothing_p)
                    )
                ;

            //parse the INITIAL section where start values are assigned to the integrated variables: INITAIL v1=2.5; v2:=3.1;
            initial_section
                =  str_p("INITIAL")
                >> *(   equation_pars   [add_init_equation( selfm.model, equation_pars.equation)]
                    |   (eps_p          [make_error( "Error in INITIAL section!", selfm.err_temp)] >> nothing_p)
                    )
                ;

            //parse the SOLUTIONPARAMETERS section
            solutionparameters_section
                = str_p("SOLUTIONPARAMETERS")           /*[&start_sol_parms]*/ >>
                  *(    solutionparameters_assignment   /*[&add_sol_parms]*/
                   |   (eps_p[make_error("Error in SOLUTIONPARAMETERS section!", selfm.err_temp)] >> nothing_p)
                   );
            solutionparameters_assignment
                = ( str_p("ReportingInterval") >> ":=" >>
                    (real_p >> eps_p)                   [assign_a(selfm.model.solutionParameters.reportingInterval)] >>
                    +ch_p(';')
                  )
                | ( str_p("SimulationTime") >> ":=" >>
                    (real_p  >> eps_p)                  [assign_a(selfm.model.solutionParameters.simulationTime)] >>
                    +ch_p(';')
                  );
        }

        //!The start rule of the model grammar.
        spirit::rule<ScannerT> const &
        start() const { return model_definition; }

        private:

        //!Rules that are defined here
        spirit::rule<ScannerT>
            model_definition,
            parameter_section,/* parameter_definition,*/
            unit_section, unit_definition,
            variable_section, /*variable_definition,*/
            set_section, equation_section, initial_section,
            solutionparameters_section, solutionparameters_assignment;
        //!Grammar that describes all names (model, parameter, variable) e.g.: "reactor"
        ps_name name;
        //!parser for formulas
        ps_formula formula;
        //!parser for equations
        ps_equation equation_pars;
        //!parser for definition of variable or parameter
        ps_memory_definition memory_definition;
        //!Constants because assign_a needs references
        bool const true_val, false_val;
    };
};

} // namespace siml

#endif // SIML_MODEL_GRAMMAR_HPP
