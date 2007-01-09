#!/usr/bin/env python
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


#import pdb
import optparse
import sys
import os
import stat
from subprocess import Popen, PIPE, STDOUT
import pyparsing
import simlparser
import pygenerator
import ast #for ast.progVersion
from ast import UserException


class SimlCompiler(object):
    def __init__(self):
        super(SimlCompiler, self).__init__()
        self.inputFileName = ''
        self.outputFileName = ''
        #which process should be run after compiling
        self.runSimulation = None #can be: None, 'all', '0', '1', ...
        
        
    def parseCmdLine(self):
        '''Parse the command line, and find out what the user wants from us.'''
        #set up parser for the command line aruments
        optPars = optparse.OptionParser(
                    usage='%prog <input_file> [-o <output_file>] [<options>]',
                    description='Compiler for the Siml simulation language.', 
                    version='%prog ' + ast.progVersion)
        
        optPars.add_option('-o', '--outfile', dest='outfile', 
                           help='explicitly specify name of output file', 
                           metavar='<output_file>')
        optPars.add_option('-r', '--run', dest='runone',
                           help='run the given simulation process after ' 
                              + 'compiling (number counts fron top; ' 
                              + 'or special value "all")',
                           metavar='<number>')
        optPars.add_option('-a', '--runall', dest='runall',
                           action="store_true", default=False,
                           help='run all simulation processes after compiling')
    #    optPars.add_option('-n', '--nomain', dest='genmain',
    #                       action="store_false", default=True,
    #                       help='do not generate a main routine [default]')
        #do the parsing
        (options, args) = optPars.parse_args()
        
        #get name of input file
        #self.inputFileName = None
        if len(args) > 0:
            self.inputFileName = args[0]
        if not self.inputFileName:
            optPars.error('no input file given')
        #test extension
        inputFileExtension = self.inputFileName.rsplit('.',1)[1]
        if inputFileExtension.lower() != 'siml':
            print 'warning: programs in the Siml language ' + \
                  'should have the extension ".siml"'
        
        #get name of output file
        if options.outfile:
            #output file name is explicitly given
            self.outputFileName = options.outfile
        else:
            #take away extension from inputFileName and replace with '.py'
            baseName = self.inputFileName.rsplit('.',1)[0]
            self.outputFileName = baseName + '.py'
        
        #see if user whishes to run the simulation after compiling
        if options.runone == 'all':
            self.runSimulation = 'all'
        elif options.runone: #anythin else is considered a number
            #convert into string containing a number
            self.runSimulation = str(int(options.runone)) 
        #special option runall
        if options.runall:
            self.runSimulation = 'all'
              
    
    def doCompile(self):
        '''Do the work'''
        #create the top level objects that do the compilation
        parser = simlparser.ParseStage()
        iltGen = simlparser.ILTGenerator()
        progGen = pygenerator.ProgramGenerator()
        
        #the compilation proper
        try:
            astTree = parser.parseProgramFile(self.inputFileName)
            #print astTree
            iltTree = iltGen.createIntermediateTree(astTree)
            #print iltTree
            progGen.createProgram(iltTree)
            progStr = progGen.buffer()
        #errors from freeode
        except UserException, theError:
            print theError
            sys.exit(1)
        #errors from pyparsing. Don't remove: parser may re-raise pyparsing errors.
        except pyparsing.ParseException, theError:
            print 'syntax error: ', theError
            sys.exit(1)
            
        #write generated program to file
        try:    
            outputFile = open(self.outputFileName,'w')
            outputFile.write(progStr)
            outputFile.close()
            #make genrated program executable
            modeBits = os.stat(self.outputFileName).st_mode
            os.chmod(self.outputFileName, modeBits | stat.S_IEXEC)
        except IOError, theError:
            print 'error: could nor write output file\n', theError 
            sys.exit(1)
        
        print 'Compilation finished successfully.\n',\
              'input file: %s, output file: %s' % (self.inputFileName, self.outputFileName)
     
    
    def runProgram(self):   
        '''Run the generated program if the user wants it.'''
        if self.runSimulation == None:
            return
        print 'running generated program ...'
        #optStr = ' -r %s' % self.runSimulation
        cmdStr = 'python %s -r %s' % (self.outputFileName, self.runSimulation)
        proc = Popen([cmdStr], shell=True, #bufsize=1000,
                     stdin=None, stdout=None, stderr=None, close_fds=True)

    
    def mainFunc(self):
        '''the main function'''
        try:
            self.parseCmdLine()
            self.doCompile()
            self.runProgram()
        except SystemExit:
            raise #for sys.exit() - the error message was already printed
        except Exception:
            print 'Compiler internal error! Please file a bug report at:\n',\
                  'https://developer.berlios.de/projects/freeode/\n'
            raise 
        
        # 'return with success'
        sys.exit(0)


if __name__ == '__main__':
    #run the compiler
    m = SimlCompiler()
    m.mainFunc()
