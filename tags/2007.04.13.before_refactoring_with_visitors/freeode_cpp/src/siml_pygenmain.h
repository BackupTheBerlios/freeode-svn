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
#ifndef SIML_PYGENMAIN_H
#define SIML_PYGENMAIN_H


// #include <boost/shared_ptr.hpp>

#include <iostream>
// #include <vector>
// #include <string>
// #include <fstream>
// #include <map>


namespace siml {

/**
@short Main generator object

This object writes a program in the python language that performs the simulation(s)

@author Eike Welk <eike.welk@post.rwth-aachen.de>
*/
class PyGenMain{
public:
    //!Constructor
    PyGenMain( std::ostream & inPyFile );
    //!Destuctor
    ~PyGenMain();

    //!generate python code for all processes
    void generateAll();

protected:
    //!Generate the code at the file's start
    void genFileStart();

private:
    //!The generated python program is stored here
    std::ostream& m_PyFile;

};

}

#endif
