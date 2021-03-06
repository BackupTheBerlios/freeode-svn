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


#include "siml_globaldef.h"
#include "siml_cmpath.h"
#include "siml_cmmemaccess.h"
#include "siml_cmformula.h"

#include <string>
#include <vector>
#include <list>

#include <boost/shared_ptr.hpp>


namespace siml {

/*!
@short Data of parameter or variable

This is the parsing result for one line of the PARAMETER section. The code
generator will later use this information.
a good idea, to aid the generation of code generator errors.
@todo A split between syntax tree and code generation structure may be a good idea.
*/
struct CmMemoryDescriptor
{
    //!parameter name
    /*! This is a path (and not a string) because CmMemoryDescriptor represents
    parsed definitions (variable or parameter) and memory that needs to be allocated. */
    CmPath name;
    //!REAL, INT, ANY (currently unused)
    std::string type;
    //!true if variable is an integrated variable
    bool isStateVariable;
    //!Iterator to the place where the definition started (into the file buffer)
    BufferIterator defBegin;

    CmMemoryDescriptor() : type("ANY"), isStateVariable(false) {};
};
/*!container for the parameter descriptors of a model. See: @see CmParameterDescriptor*/
typedef std::list<CmMemoryDescriptor> CmMemoryTable;


/*!
@short Descripion of one equation or assignment.
*/
struct CmEquationDescriptor
{
    //!the equation's left hand side
    CmMemAccess lhs;
    //!the equation's right hand side
    CmFormula rhs;
    //!if true the equation is really an assignment ":=" otherwise it's a true equation "=" (unused)
//     bool is_assignment;
    //!Is lhs a time differential?
    bool isOdeAssignment() const;
    //!Iterator to the place where the definition started (into the file buffer)
    BufferIterator defBegin;

    CmEquationDescriptor() /*: is_assignment(false), is_ode_assignment(false)*/ {};
};
/*!container for the equation descriptors of a model. See: @see CmEquationDescriptor*/
typedef std::vector<CmEquationDescriptor> CmEquationTable;


/*!
@short Descripion of sub-models

Represents one line of the "UNIT" section
*/
struct CmSubModelLink
{
    //!The sub-model's name in the parent model.
    std::string name;
    //!The sub-model's type.
    std::string type;
    //!Iterator to the place where the definition started (into the file buffer)
    BufferIterator defBegin;
};
//!container for model references.
typedef std::vector<CmSubModelLink> CmSubModelTable;


/*!
@short Storage for "SOLUTIONPARAMETERS"
*/
struct CmSolutionParameterDescriptor
{
    //!The interval between reported time points
    std::string reportingInterval;
    //!The total simulation time
    std::string simulationTime;
    //!Iterator to the place where the definition started (into the file buffer)
    BufferIterator defBegin;

    CmSolutionParameterDescriptor(): reportingInterval("1"), simulationTime("10") {}
};


/*!
@short Descripion of a "MODEL"
This is the parsing result of a model: "MODEL ... END"

@todo write a class CmModelCodeGen that contians the operatins of siml_code_transformations.
*/
struct CmModelDescriptor
{
    //!The model's name
    std::string name;

    /*!Container for parameters. ("PARAMETER") See: @see CmParameterDescriptor*/
    CmMemoryTable parameter;
    /*!Container for the sub models ("UNIT") @see CmSubModelLink*/
    CmSubModelTable subModel;
    /*!Container for variables. See: @see CmVariableDescriptor*/
    CmMemoryTable variable;
    /*!Container for parameter initializations. ("SET section") See: @see CmEquationDescriptor*/
    CmEquationTable parameterAssignment;
    /*!Container for the eqations. See: @see CmEquationDescriptor*/
    CmEquationTable equation;
    /*!Container for initializations of integrated variables. ("INITIAL" section) See: @see CmEquationDescriptor*/
    CmEquationTable initialEquation;
    //!Some simulation options
    CmSolutionParameterDescriptor solutionParameters;
    //!Iterator to the place where the definition started (into the file buffer)
    BufferIterator defBegin;

    //!If true: the model is really a "PROCESS"; else: it is a "MODEL"
    bool isProcess;
    //!There are errors
    bool errorsDetected;

    //!Constructor
    CmModelDescriptor(): /*defBegin(0),*/ isProcess(false), errorsDetected(false) {};
    //!Display the model's contents (for debuging)
    void display() const;

    //!Add a parameter descriptor to the model
    void addParameter(CmMemoryDescriptor inPar);
    //!Add a sub-model descriptor to the model
    void addSubModel(CmSubModelLink inSub);
    //!Add a variable descriptor to the model
    void addVariable(CmMemoryDescriptor inVar);
    //!Set a value to a parameter
    void addParameterAssignment( CmEquationDescriptor inEqu);
    //!Add an equation to the model
    void addEquation( CmEquationDescriptor inEqu);
    //!Set an initial value to a state variable
    void addInitialEquation( CmEquationDescriptor inEqu);

//     //!Mark variable as state variable
//     void setVariableIntegrated(CmPath const & stateVarName);

    //!Find parmeter by name, return the definition.
    CmMemoryTable::const_iterator   findParameter(CmPath const & name) const;
    //!Find parmeter by name, return the definition.
    CmMemoryTable::iterator         findParameter(CmPath const & name);
    //!Find submodel by name, return the definition.
    CmSubModelTable::const_iterator findSubModel(CmPath const & name) const;
    //!Find submodel by name, return the definition.
    CmSubModelTable::iterator       findSubModel(CmPath const & name);
    //!Find variable by name, return the definition.
    CmMemoryTable::const_iterator   findVariable(CmPath const & name) const;
    //!Find variable by name, return the definition.
    CmMemoryTable::iterator         findVariable(CmPath const & name);

    //!Check if name already exists
    bool isIdentifierExisting(CmPath const & name) const;
};
struct CmModelDescriptor;
//!safe pointer type
typedef boost::shared_ptr<CmModelDescriptor> ModelPtr;
//!container for models.
typedef std::vector<CmModelDescriptor> CmModelTable;


/*!
@short Binary representation of the input files.

The parser stores all results here, and intermediate results (what symbols do
currently exist) are taken from here.

The code generator gets this object and it generates a computer program from it.
Additonally errors and warnings from the parser and the code generator are
collected here too.
*/
struct CmCodeRepository
{
    //!List of models
    CmModelTable model;
    //!List of processes
    CmModelTable process;

    //!Static pointer to the one and only code model
    static CmCodeRepository * repository;
    //!The names of the input files - for inclusion into messages.
    static std::vector<std::string> inputFileNames;

    //!Display the repositorie's contents (for debuging)
    void display() const;
    //!Find a model declaration by name
    CmModelDescriptor * findModel(std::string const & name);
    ///@todo we need a const version of the function
//     CmModelDescriptor const * findModel(std::string const & name) const;
};

//!Accessor function for the one and only code model
inline CmCodeRepository * repository() { return CmCodeRepository::repository; };
} //namespace siml

#endif // SIML_CODE_MODEL_HPP
