############################################################################
#    Copyright (C) 2006 by Eike Welk                                       #
#    eike.welk@post.rwth-aachen.de                                         #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################


# Setup script for the freeode simulation software
#
# Install the software by issuing on the command line:
#    python setup.py install
#
# Commandline for creating distributions:
#    python setup.py sdist --formats=gztar,zip bdist_rpm bdist_wininst
#
# Small overview of frequently used commands. The command line
# generally is:
#    python setup.py <command>  [--dry-run]
#
# Some commands are:
#    sdist         : create source distribution. (*.tar.gz or *.zip)
#    bdist_wininst : create Windows executable installer (binary distribution). (*.exe)
#    bdist_rpm     : create binary RPM disribution (*.rpm)
#    install       : install the software
#    --dry-run     : test the operation without doing anything
#
# also usefull:
#    python setup.py --help
#    python setup.py --help-commands


# IMPORTANT:
# Files for the source distribution are also specified in the file:
#    MANIFEST.in


from distutils.core import setup
from freeode.ast import progVersion

setup(name = 'freeode',
      version = progVersion,
      author = 'Eike Welk',
      author_email = 'Eike.Welk@gmx.net',
      url = 'http://freeode.berlios.de/',
      description = 'Simulation Language for Differential Equations',
      long_description = \
'''This packge contains a compiler for a specialized language (SIML) for the
simulation of differential equations (ODE). The generated simulation program
is in the Python programing language, using the Numpy and Scipy libraries.''',
      license = 'GPL',
      packages = ['freeode'],
      scripts = ['simlc'],
      #data_files = [('freeode', ['hl_siml.xml'])], # (<folder>, [<file>])
      )
