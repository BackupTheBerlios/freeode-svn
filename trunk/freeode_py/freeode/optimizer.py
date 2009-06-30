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
import math
import os

from freeode.ast import *

