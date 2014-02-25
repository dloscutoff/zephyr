
from BNF import Grammar
from Scanner import Scanner
from TableParser import parse
from Execution import runProgram
from Utilities import processCmdLineArgs
import sys

defaultFile = "Programs/10print.zeph"
defaultDebug = False

if __name__ == "__main__":
    options = processCmdLineArgs()
    filename = options["filename"]
    debug = options["debug"]
    grammarFile = "BNF.txt"
    grammar = Grammar(grammarFile)
    if filename is None:
        # If no code filename was given on the command line, see if a default
        # is specified
        try:
            filename = defaultFile
        except NameError:
            # If no default was given, keep the filename at None
            pass
    if debug is False:
        # If the debug flag was not set on the command line, see if a default
        # is specified
        try:
            debug = defaultDebug
        except NameError:
            # If no default was given, keep the debug setting at False
            pass
    
    if filename is not None:
        # If we have a filename, open it and read the contents
        # (first check to make sure it's got the extension .zeph)
        if not filename.endswith(".zeph"):
            filename += ".zeph"
        try:
            f = open(filename, 'r')
        except IOError:
            # TODO: explain requirement for source file to end in .zeph if the
            # user supplied one that didn't
            print("Could not open \"%s\"" % filename)
            sys.exit(1)
        code = f.read()
        f.close()
    else:
        # No filename; use a snippet of test code instead
        code = 'print "Welcome to Zephyr!"'
    # The code must be terminated with a newline to parse correctly
    code += "\n"
    scanner = Scanner(code)
    try:
        syntaxTree = parse(scanner, grammar)
    except:
        # A better error message should be printed where the error is raised,
        # right?  TODO investigate
        print("Execution terminated.")
    else:
        runProgram(syntaxTree, debug = debug)
