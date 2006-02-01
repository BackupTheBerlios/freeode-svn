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
#include "config.h"
#include "siml_pyprocessgenerator.h"
#include "siml_code_transformations.h"

#include <iostream>
#include <boost/format.hpp>
#include <boost/tuple/tuple.hpp>


using std::string;
using std::endl;
using std::map;
using std::vector;
using std::cout;
using boost::format;
using boost::tie;
using boost::shared_ptr;


/*!Construct and initialize the object, but do not generate codee.*/
siml::PyProcessGenerator::PyProcessGenerator( std::ostream& inPyFile ) :
        m_PyFile(inPyFile),
        m_StateVectorSize(0),
        m_ResultArrayColls(0)
{

}


siml::PyProcessGenerator::~PyProcessGenerator()
{
}


/*!
 Create python objects for all processs in parse_result.
 */
void siml::PyProcessGenerator::generateAll()
{
    cout << "Start generating Python code --------------------------\n";
    genFileStart();
    //loop over all processs and generate a python object for each.
    //genProcessObject(0); ///@TODO generate all processes
    cout << "Number of processes: " << repository()->process.size() << "\n";
    for( uint i=0; i< repository()->process.size(); ++i)
    {
        genProcessObject(i);
    }
}


/*!
Generate the first few lines of the python file

@TODO find out how to insert time and date.
For time and date see:
http://www.boost.org/doc/html/date_time/examples/general_usage_examples.html
 */
void siml::PyProcessGenerator::genFileStart()
{
    m_PyFile <<
            "#!/usr/bin/python\n"
            "\n"
            "#------------------------------------------------------------------------------#\n"
            "#                            Warning: Do not edit!                             #\n"
            "#                                                                              #\n"
            "# This file is generated, it will be overwritten every time the source file is #\n"
            "# changed.                                                                     #\n"
            "# Write a main routine in an other file. Use import or execfile to load        #\n"
            "# the objects defined in this file into the Python interpreter.                #\n"
            "#------------------------------------------------------------------------------#\n" <<
     format("# Generated by Siml Version %1% on ????.??.?? ??:??                      %|79t|#\n") % VERSION  <<
            "#------------------------------------------------------------------------------#\n"
            "\n"
            "\n"
            "from scipy import * # Also includes Numeric.\n"
            "import Gnuplot, Gnuplot.funcutils\n" ///@TODO change from Gnuplot to a more standard plotting library
            "\n"
            "\n"
            ;
}


/*!
Create a single process
 */
void siml::PyProcessGenerator::genProcessObject(int iProcess)
{
    shared_ptr<CmModelDescriptor> procFinal;
    procFinal = createFlatModel( &repository()->process[iProcess], repository());
    procFinal->display();

    return;

    //collect parameters, variables and equations from all models and put them in big global tables
    ///@todo multi model capabilities and recursion into sub-models
    m_Parameter = repository()->model[0].parameter;
    m_Variable = repository()->model[0].variable;
    m_Equation = repository()->model[0].equation;

    ///@todo create identifier names that are compatible with python

    //allocate space for each state m_Variable in the state vector. Changes: state_vector_layout, m_StateVectorSize
    layoutArrays();

    string process_name("TestProcess");

    m_PyFile << format("class %1%:\n") % process_name;
    m_PyFile << format("%|4t|\"\"\" object to simulate process %1% \"\"\"\n") % process_name;
    m_PyFile << endl;

    //Generate some infrastructure functions
    ///@todo these functions should later go into a common base class of all processs
    genAccessFunction();
    genGraphFunction();

    //Generate Constuctor which creates the parameters as member variables.
    genConstructor();

    //Generate the function that contains the equations.
    genOdeFunction();

    //Function to compute the algebraic variables after the simulation.
    genOutputEquations();

    //Generate the function that performs the simulation.
    genSimulateFunction();
}


/*!
Generate the __init__ function.
Generate Constuctor which creates the parameters as member variables
 */
void siml::PyProcessGenerator::genConstructor()
{
//     m_PyFile << format("%|4t|def __init__(self):") << endl;
//
//     //Assign values to the parameters (and create them)
//     m_PyFile << format("%|8t|#Assign values to the parameters (and create them)") << endl;
//     CmMemoryTable::const_iterator it;
//     for( it = m_Parameter.begin(); it != m_Parameter.end(); ++it )
//     {
//         CmMemoryDescriptor paramD = *it;
//         string pName = paramD.name.toString();
//         string pVal  = paramD.default_expr;
//         string pType = paramD.type;
//         m_PyFile << format("%|8t|self.%1% %|25t|= %2% #%3%") % pName % pVal % pType << endl;
//     }
//     m_PyFile << endl;
//
//     //Set initial values of the state variables.
//     m_PyFile << format("%|8t|#Set the initial values (of the state variables).") << endl;
//     m_PyFile << format("%|8t|self.y0 = zeros(%1%, Float)") % m_StateVectorSize << endl;
//     CmMemoryTable::const_iterator itV;
//     for( itV = m_Variable.begin(); itV != m_Variable.end(); ++itV )
//     {
//         CmMemoryDescriptor varD = *itV;
//         if( varD.is_state_variable == false ) { continue; }
//
//         string varName = varD.name.toString();
//         string index = m_StateVectorMap[varName]; //look up m_Variable's index in the state vector.
//         string initExpression = varD.initial_expr;
//         m_PyFile << format("%|8t|self.y0[%1%] = %2% # %3%") % index % initExpression % varName << endl;
//     }
//     m_PyFile << endl;
//
//     //Map for converting m_Variable names to indices or slices
//     //necessary for later m_Parameter access
//     m_PyFile << format("%|8t|#Map for converting variable names to indices or slices.") << endl;
//     m_PyFile << format("%|8t|self.resultArrayMap = { ");
//     map<string, string>::const_iterator itMa;
//     for( itMa = m_ResultArrayMap.begin(); itMa != m_ResultArrayMap.end(); ++itMa )
//     {
//         string varName, index;
//         tie(varName, index) = *itMa;
//         m_PyFile << format(" '%1%':%2%, ") % varName % index;
//     }
//     m_PyFile << " }" << endl << endl;
//
// /*    m_PyFile << format("%|8t|#List of diagrams.") << endl;
//     m_PyFile << format("%|8t|self.graphList = []") << endl;
//     m_PyFile << endl;*/
}


/*!
Generate the function that computes the time derivatives.
This function contains all equations. The function will be called repeatedly by
the simulation library routine.
 */
void siml::PyProcessGenerator::genOdeFunction()
{
//     //y: state vector, time current time
//     m_PyFile <<
//             "    def _diffStateT(self, y, time):\n"
//             "        \"\"\"\n"
//             "        Compute the time derivatives of the state variables.\n"
//             "        This function will be called repeatedly by the integration algorithm.\n"
//             "        y: state vector,  time: current time\n"
//             "        \"\"\"\n"
//             "        \n";
//
//     //Create local variables for the parameters.
//     m_PyFile << format("%|8t|#Create local variables for the parameters.") << endl;
//     CmMemoryTable::const_iterator itP;
//     for( itP = m_Parameter.begin(); itP != m_Parameter.end(); ++itP )
//     {
//         CmMemoryDescriptor paramD = *itP;
//         m_PyFile << format("%|8t|%1% = self.%1%") % paramD.name << endl;
//     }
//     m_PyFile << endl;
//
//     //Dissect the state vector into individual, local state variables.
//     m_PyFile << format("%|8t|#Dissect the state vector into individual, local state variables.") << endl;
//     CmMemoryTable::const_iterator itV;
//     for( itV = m_Variable.begin(); itV != m_Variable.end(); ++itV )
//     {
//         CmMemoryDescriptor varD = *itV;
//         if( varD.is_state_variable == false ) { continue; }
//
//         string varName = varD.name.toString();
//         string index = m_StateVectorMap[varName]; //look up variable's index in the state vector.
//         m_PyFile << format("%|8t|%1% = y[%2%]") % varName % index << endl;
//     }
//     m_PyFile << endl;
//
//     //Create the return vector
//     m_PyFile << format("%|8t|#Create the return vector (the time derivatives dy/dt).") << endl;
//     m_PyFile << format("%|8t|y_t = zeros(%1%, Float)") % m_StateVectorSize << endl;
//     m_PyFile << endl;
//
//     //write a line to compute each algebraic variable
//     m_PyFile << format("%|8t|#Compute the algebraic variables.") << endl;
//     CmEquationTable::const_iterator itE;
//     for( itE = m_Equation.begin(); itE != m_Equation.end(); ++itE )
//     {
//         CmEquationDescriptor equnD = *itE;
//         if( equnD.is_ode_assignment ) { continue; }
//         string algebVar = equnD.lhs;
//         string mathExpr = equnD.rhs;
//         m_PyFile << format("%|8t|%1% = %2%") % algebVar % mathExpr << endl;
//     }
//
//     //write a line to compute the time derivative of each integrated variable
//     m_PyFile << format("%|8t|#Compute the state variables. (Really the time derivatives.)") << endl;
//     for( itE = m_Equation.begin(); itE != m_Equation.end(); ++itE )
//     {
//         CmEquationDescriptor equnD = *itE;
//         if( !equnD.is_ode_assignment ) { continue; }
//         string stateVar = equnD.lhs;
//         string mathExpr = equnD.rhs;
//         string index = m_StateVectorMap[stateVar]; //look up variable's index in state vector
//         m_PyFile << format("%|8t|y_t[%1%] = %2% # = d %3% /dt ") % index % mathExpr % stateVar << endl;
//     }
//     m_PyFile << endl;
//
//     //return the result
//     m_PyFile << format("%|8t|return y_t") << endl;
//     m_PyFile << endl;
}


/*!
Allocate space for each state variable in the state vector and result array.
The state variable have the same indices in both arrays.

The function changes:
m_StateVectorMap, state_vector_ordering??, m_StateVectorSize,
m_ResultArrayMap, result_array_ordering??, m_ResultArrayColls.

The ...map m_Variable are contain pairs (var_name, index) e.g: ("S", "1")
???The ...ordering variables contain the variable names in order of ascending index.???
m_StateVectorSize is the state vector's number of rows.
m_ResultArrayColls is number of collumns in result array.
 */
void siml::PyProcessGenerator::layoutArrays()
{
//     m_StateVectorMap.clear(); /*state_vector_ordering.clear();*/ m_StateVectorSize=0;
//     m_ResultArrayMap.clear(); /*result_array_ordering.clear();*/ m_ResultArrayColls=0;
//
//     //loop over all variables and assign indices for the state variables
//     //each state variable gets a unique index in both arrays: state vector, result array.
//     CmMemoryTable::const_iterator itV;
//     uint currIndex=0;
//     for( itV = m_Variable.begin(); itV != m_Variable.end(); ++itV )
//     {
//         CmMemoryDescriptor varD = *itV;
//         if( varD.is_state_variable == false ) { continue; }
//
//         string currIndexStr = (format("%1%") % currIndex).str(); //convert currIndex to currIndexStr
//         string varNameStr = varD.name.toString();
//         m_StateVectorMap[varNameStr] = currIndexStr;
//         m_ResultArrayMap[varNameStr] = currIndexStr;
// /*        state_vector_ordering.push_back(varD.name);
//         result_array_ordering.push_back(varD.name);*/
//         ++currIndex;
//     }
//     m_StateVectorSize = currIndex;
//
//     //Loop over all variables again and assign indices for the algebraic variables.
//     //Each algebraic variable gets a unique index in the result array.
//     for( itV = m_Variable.begin(); itV != m_Variable.end(); ++itV )
//     {
//         CmMemoryDescriptor varD = *itV;
//         if( varD.is_state_variable == true ) { continue; }
//
//         string currIndexStr = (format("%1%") % currIndex).str(); //convert currIndex to currIndexStr
//         string varNameStr = varD.name.toString();
//         m_ResultArrayMap[varNameStr] = currIndexStr;
// /*        result_array_ordering.push_back(varD.name);*/
//         ++currIndex;
//     }
//     m_ResultArrayColls = currIndex;
}


/*!
Generate a function that computes the algebraic variables again after the simulation,
so they can be examined too. Only state variables are stored doring ODE simulation.
*/
void siml::PyProcessGenerator::genOutputEquations()
{
/*    m_PyFile <<
            "    def _outputEquations(self, y):\n"
            "        \"\"\"\n"
            "        Compute (again) the algebraic variables as functions of the state \n"
            "        variables. All variables are then stored together in a 2D array.\n"
            "        \"\"\"\n"
            "        \n";

    //create the result array
    m_PyFile << format("%|8t|#create the result array") << endl;
    m_PyFile << format("%|8t|assert shape(y)[0] == size(self.time)") << endl;
    m_PyFile << format("%|8t|sizeTime = shape(y)[0]") << endl;
    m_PyFile << format("%|8t|self.resultArray = zeros((sizeTime, %1%), Float)") % m_ResultArrayColls << endl;
    m_PyFile << endl;

    //copy the state variables into the result array
    m_PyFile << format("%|8t|#copy the state variables into the result array") << endl;
    m_PyFile << format("%|8t|numStates = shape(y)[1]") << endl;
    m_PyFile << format("%|8t|self.resultArray[:,0:numStates] = y;") << endl;
    m_PyFile << endl;

    //Create local variables for the parameters.
    m_PyFile << format("%|8t|#Create local variables for the parameters.") << endl;
    CmMemoryTable::const_iterator itP;
    for( itP = m_Parameter.begin(); itP != m_Parameter.end(); ++itP )
    {
        CmMemoryDescriptor paramD = *itP;
        m_PyFile << format("%|8t|%1% = self.%1%") % paramD.name << endl;
    }
    m_PyFile << endl;

    //Create local state variables - take them from the result array.
    m_PyFile << format("%|8t|#Create local state variables - take them from the result array.") << endl;
    CmMemoryTable::const_iterator itV;
    for( itV = m_Variable.begin(); itV != m_Variable.end(); ++itV )
    {
        CmMemoryDescriptor varD = *itV;
        if( varD.is_state_variable == false ) { continue; }

        string varName = varD.name.toString();
        string index = m_ResultArrayMap[varName]; //look up variable's index
        m_PyFile << format("%|8t|%1% = self.resultArray[:,%2%]") % varName % index << endl;
    }
    m_PyFile << endl;

    //compute the algebraic variables
    m_PyFile << format("%|8t|#Compute the algebraic variables.") << endl;
    CmEquationTable::const_iterator itE;
    for( itE = m_Equation.begin(); itE != m_Equation.end(); ++itE )
    {
        CmEquationDescriptor equnD = *itE;
        if( equnD.is_ode_assignment ) { continue; }

        string algebVar = equnD.lhs;
        string index = m_ResultArrayMap[algebVar];
        string mathExpr = equnD.rhs;
        m_PyFile << format("%|8t|self.resultArray[:,%1%] = %2% # %3%") % index % mathExpr % algebVar << endl;
    }

    m_PyFile << endl;*/
}


/*!
Generate the function that will perform the simulation.
*/
void siml::PyProcessGenerator::genSimulateFunction()
{
    m_PyFile <<
            "    def simulate(self):\n"
            "        \"\"\"\n"
            "        This function performs the simulation.\n"
            "        \"\"\"\n"
            "        \n"
            "        self.time = linspace(0, 20, 100)\n" ///@todo respect SOLUTIONPARAMETERS
            "        y = integrate.odeint(self._diffStateT, self.y0, self.time)\n"
            "        self._outputEquations(y)\n"
            "        \n";
}



/*!
Access variables by name.
@todo add returning multiple variables at once
*/
void siml::PyProcessGenerator::genAccessFunction()
{
    m_PyFile <<
            "    def get(self, varName):\n"
            "        \"\"\"\n"
            "        Get a variable by name.\n"
            "        \n"
            "        There are special variable names:\n"
            "           'time': vector of times\n"
            "           'all': array of all variables\n"
            "        \"\"\"\n"
            "        if varName == 'time':\n"
            "            return self.time\n"
            "        elif varName == 'all':\n"
            "            return self.resultArray\n"
            "        index = self.resultArrayMap[varName]\n"
            "        return self.resultArray[:,index]\n"
            "        \n";
}


/*!
Display graphs
*/
void siml::PyProcessGenerator::genGraphFunction()
{
    m_PyFile <<
            "    def graph(self, varNames):\n"
            "        \"\"\"\n"
            "        Show one or several variables in a graph.\n"
            "        \n"
            "        Parameters:\n"
            "           varNames: String with a list of variables to be plotted. (Space or comma seperated.)\n"
            "                     e.g.: 'X mu' \n"
            "        \"\"\"\n"
            "        \n"
            "        diagram=Gnuplot.Gnuplot(debug=0, persist=1)\n"
            "        diagram('set data style lines')\n"
            "        diagram.title(varNames)\n"
            "        diagram.xlabel('Time')\n"
            "        \n"
            "        varList = varNames.replace(',', ' ').split(' ')\n"
            "        for varName1 in varList:\n"
            "            if not (varName1 in self.resultArrayMap): continue\n"
            "            curve=Gnuplot.Data(self.get('time'), self.get(varName1))\n"
            "            diagram.replot(curve)\n"
            "        \n";
}
