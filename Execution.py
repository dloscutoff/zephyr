
from BuiltInClasses import *
from Errors import ZRuntimeError, ConstructorTypeError
from ProgramState import ProgramState, isLValue
from AST import TreeNode
from Tokens import Operator
from Utilities import removeFromFront, removeFromEnd
from sys import stdout
from random import randrange

binaryOpNames = {
    '+': "z_plus",
    '-': "z_minus",
    '*': "z_times",
    '/': "z_divide",
    'mod': "z_mod",
    '=': "z_equal",
    r'\=': "z_notEqual",
    '<': "z_lessThan",
    '>': "z_greaterThan",
    '<=': "z_lessThanEqual",
    '>=': "z_greaterThanEqual",
    '|': "z_concat",
    '||': "z_spaceConcat",
    'and': "z_and",
    'or': "z_or"
    }

unaryOpNames = {
    '-': "z_negation",
    '/': "z_inverse",
    'not': "z_not"
    }

reverseOpNames = {
    "z_equal": "z_equal",
    "z_notEqual": "z_notEqual",
    "z_lessThan": "z_greaterThan",
    "z_greaterThan": "z_lessThan",
    "z_lessThanEqual": "z_greaterThanEqual",
    "z_greaterThanEqual": "z_lessThanEqual"
    }

builtInClasses = {
    "Integer": ZInteger,
    "Fraction": ZFraction,
    "Boolean": ZBoolean,
    "Character": ZCharacter,
    "String": ZString,
    "Array": ZArray
    }

def runProgram(syntaxTree, debug = False):
    # Create a new (empty) program state
    state = ProgramState()
    # Execute the code
    try:
        execute(syntaxTree, state)
    except (ZRuntimeError, KeyboardInterrupt):
        print("Execution terminated.")
    if debug:
        # For debugging purposes, print the final state of the program
        state.output()
    
def execute(node, state):
    """Generates output and/or state changes based on the given AST node."""
    if node.name == "Program":
        # Execute the program's main block
        execute(node.children[0], state)
    elif node.name == "Block":
        # Execute each statement in the block
        for child in node.children:
            execute(child, state)
    elif node.name == "PrintStatement":
        # Evaluate the statement's expressions and output them
        printNewline = True
        for child in node.children:
            if child.name == "Symbol" and child.value == "...":
                printNewline = False
                break
            value = getValue(child, state)
            if hasattr(value, "z_output"):
                # Call the value's z_output function
                value.z_output()
            else:
                # Use the value's __str__ function instead
                stdout.write(str(value))
            # Either way, print a space afterward
            stdout.write(" ")
        if printNewline:
            stdout.write("\n")
    elif node.name == "SetStatement":
        # Make the appropriate changes to the given variable
        lhsEntity = evaluate(node.children[0], state)
        if not isLValue(lhsEntity):
            print("Trying to assign to value or reserved name")
            raise ZRuntimeError
        rhsEntity = evaluate(node.children[1], state)
        if isLValue(rhsEntity):
            # Assign by reference
            address = state.getVarAddress(rhsEntity)
        else:
            # Assign by value
            address = state.memorize(rhsEntity)
        state.setVarAddress(lhsEntity, address)
    elif node.name == "IncStatement":
        # Increment the given variable
        lhsEntity = evaluate(node.children[0], state)
        if not isLValue(lhsEntity):
            print("Trying to increment value or reserved name")
            raise ZRuntimeError
        try:
            oldValue = state.getValue(lhsEntity)
        except ValueError:
            print("Trying to increment uninitialized variable")
            raise ZRuntimeError
        try:
            newValue = oldValue.z_inc()
        except AttributeError:
            # oldValue's class does not have a z_inc() function
            print("Cannot increment %s" % oldValue.z_name)
            raise ZRuntimeError
        address = state.memorize(newValue)
        state.setVarAddress(lhsEntity, address)
    elif node.name == "InputStatement":
        # Wait for user input and store it in the given variable
        lhsEntity = evaluate(node.children[0], state)
        if not isLValue(lhsEntity):
            print("Trying to assign to value or reserved name")
            raise ZRuntimeError
        if len(node.children) > 1:
            inputType = getValue(node.children[1], state)
            if not isinstance(inputType, type):
                print("Cannot input as %s because it is not a type" % inputType)
                raise ZRuntimeError
        else:
            inputType = ZString
        value = inputType(input())
        address = state.memorize(value)
        state.setVarAddress(lhsEntity, address)
    elif node.name == "WhileStatement":
        # Execute the statement's block as long as its expression is true
        condition = node.children[0]
        block = node.children[1]
        condVal = getValue(condition, state)
        if condVal.__class__ != ZBoolean:
            print("Given non-boolean as condition expression:", \
                  repr(condVal))
            raise ZRuntimeError
        while condVal.value == True:
            execute(block, state)
            condVal = getValue(condition, state)
            if condVal.__class__ != ZBoolean:
                print("Given non-boolean as condition expression:", \
                      repr(condVal))
                raise ZRuntimeError
    elif node.name == "ForStatement":
        # Execute the statement's block for values of its variable between
        # the given bounds
        loopVar = node.children[0]
        start = node.children[1]
        finish = node.children[2]
        block = node.children[-1]
        # Construct a couple of statements to update the value of the
        # loop variable and an expression to test it
        initializer = TreeNode("SetStatement", loopVar, start)
        updater = TreeNode("IncStatement", loopVar)
        condOperator = Operator("<=")
        condition = TreeNode("Expression", loopVar, condOperator, finish)
        # Enter the loop
        execute(initializer, state)
        condVal = getValue(condition, state)
        if condVal.__class__ != ZBoolean:
            print("Given non-boolean as condition expression:", \
                  repr(condVal))
            raise ZRuntimeError
        while condVal.value == True:
            execute(block, state)
            execute(updater, state)
            condVal = getValue(condition, state)
            if condVal.__class__ != ZBoolean:
                print("Given non-boolean as condition expression:", \
                      repr(condVal))
                raise ZRuntimeError
    elif node.name == "IfStatement":
        # Execute the appropriate block based on the conditions
        index = 0
        while index < len(node.children):
            if index == len(node.children) - 1:
                # We're looking at the last child, which must be the block
                # of an else branch
                block = node.children[index]
                execute(block, state)
                break
            else:
                # Otherwise, we're looking at the original if branch or
                # an else if branch
                condition = node.children[index]
                block = node.children[index+1]
                condVal = getValue(condition, state)
                if condVal.__class__ != ZBoolean:
                    print("Given non-boolean as condition expression:", \
                          repr(condVal))
                    raise ZRuntimeError
                elif condVal.value == True:
                    # Execute this branch and skip the others
                    execute(block, state)
                    break
                else:
                    # Skip this branch and try the next one
                    index += 2
    else:
        print("Trying to execute unrecognized entity:", node.name)
        raise ZRuntimeError
    return

def getValue(node, state):
    """Convenience function that combines evaluate() and state.getValue()."""
    try:
        return state.getValue(evaluate(node, state))
    except ValueError:
        print("Trying to get the value of uninitialized variable")
        raise ZRuntimeError

def evaluate(node, state):
    """Returns the value of the given AST node."""
    if node.name == "Expression":
        # Evaluate an expression
        if len(node.children) == 1:
            # Single entity
            return evaluate(node.children[0], state)
        elif len(node.children) == 2:
            # Unary operator and a single entity
            operator = node.children[0].value
            value = getValue(node.children[1], state)
            return applyUnaryOperator(operator, value)
        else:
            # Two entities and a binary operator
            lhsValue = getValue(node.children[0], state)
            operator = node.children[1].value
            # TODO: Short-circuit code goes here?
            rhsValue = getValue(node.children[2], state)
            return applyBinaryOperator(operator, lhsValue, rhsValue)
    elif node.name == "Keyword" and node.value == "random":
        # Generate a random Fraction in [0,1) and return it
        denom = 12252240
        numer = randrange(denom)
        return ZFraction(numer, denom)
    elif node.name == "NameThing":
        # Get the value of a variable or constant name, an object
        # instantiation, a subscript, or a slice
        # Start by getting the (l)value associated with the base name
        name = node.children[0].value
        if name in builtInClasses:
            currEntity = builtInClasses[name]
        else:
            currEntity = state.getVarId(name)
        # Modify the entity based on the remaining child nodes
        for child in node.children[1:]:
            # Get the value of the current entity
            currValue = state.getValue(currEntity)
            # Under certain error conditions, we had the following:
            #print "Trying to get the value of uninitialized variable", \
            #      "'%s'" % name
            #raise ZRuntimeError
            if child.name == "Parentheses":
                if isinstance(currValue, type):
                    # currValue is a built-in class; instantiate it
                    arguments = [ getValue(grandchild, state)
                                  for grandchild in child.children ]
                    try:
                        currEntity = currValue(*arguments)
                    except ConstructorTypeError:
                        print("Wrong argument number or type(s) for %s():" \
                                  % getClassName(currValue), end=' ')
                        argtypes = [ getClassName(arg) for arg in arguments ]
                        print(", ".join(argtypes))
                        raise ZRuntimeError
                    if type(currEntity) == tuple:
                        # Constructor returned a value and a memory operation
                        currEntity, memOp = currEntity
                        # At this point, the only "memory operation" is an
                        # integer number of variables to allocate for an array
                        address = state.createVariables(memOp)
                        currEntity.assignAddress(address)
                else:
                    print("Trying to instantiate object of type", \
                          getClassName(currValue))
                    raise ZRuntimeError
            elif child.name == "SquareBraces":
                if isinstance(currValue, type):
                    print("Trying to subscript built-in class", \
                          currValue.z_name)
                    raise ZRuntimeError
                else:
                    # Determine whether we're dealing with a subscript or a
                    # section
                    if len(child.children) == 1:
                        # This is a subscript
                        isSection = False
                        # Evaluate the given index
                        index = getValue(child.children[0], state)
                    elif len(child.children) == 2:
                        # This is a section
                        isSection = True
                        # Evaluate the given indices
                        start = getValue(child.children[0], state)
                        stop = getValue(child.children[1], state)
                    if isSection:
                        # Get the value of the given section
                        try:
                            currEntity = currValue.z_section(start, stop)
                        except AttributeError:
                            print("%s object does not allow sections" \
                                  % currValue.z_name)
                            raise ZRuntimeError
                        except TypeError:
                            print("Illegal section bounds for %s: %s and %s" \
                                  % (currValue.z_name, start, stop))
                            raise ZRuntimeError
                    else:
                        # Get the lvalue of the item at the given subscript
                        try:
                            currEntity = currValue.z_subscript(index)
                        except AttributeError:
                            print("%s object is not subscriptable" \
                                  % currValue.z_name)
                            raise ZRuntimeError
                        except TypeError:
                            print("Illegal subscript for %s: %s" \
                                  % (currValue.z_name, index))
                            raise ZRuntimeError
                        except IndexError:
                            print("Subscript out of bounds:", index)
                            raise ZRuntimeError
            else:
                print("Unsupported NameThing child:", child.name)
                raise ZRuntimeError
        return currEntity
    elif node.name in builtInClasses:
        # Token is a literal of a built-in type
        itemClass = builtInClasses[node.name]
        tokenString = node.value
        tokenString = removeFromFront(tokenString, itemClass.tokenStart)
        tokenString = removeFromEnd(tokenString, itemClass.tokenEnd)
        return itemClass(tokenString)
    else:
        print("Trying to evaluate unrecognized entity:", node.name)
        raise ZRuntimeError

def applyBinaryOperator(operator, lhs, rhs):
    if operator not in binaryOpNames:
        print("Trying to apply unrecognized binary operator:", operator)
        raise ZRuntimeError
    opName = binaryOpNames[operator]
    try:
        try:
            opFunction = getattr(lhs, opName)
            result = opFunction(rhs)
            if not isinstance(result, ZObject):
                raise TypeError
        except (AttributeError, TypeError):
            # That operator function does not exist for that lhs's class
            # or does not accept that rhs's class
            try:
                # Try the reverse operator
                ropName = reverseOpName(opName)
                ropFunction = getattr(rhs, ropName)
                result = ropFunction(lhs)
                if result.__class__ == bool:
                    result = ZBoolean(result)
            except (AttributeError, TypeError):
                print("Wrong operand types for %s: %s and %s" \
                      % (operator, lhs.z_name, rhs.z_name))
                raise ZRuntimeError
    except ZeroDivisionError:
        # Division or modulo by zero
        print("Attempting to take %s %s 0" % (lhs, operator))
        raise ZRuntimeError
    return result

def applyUnaryOperator(operator, value):
    if operator not in unaryOpNames:
        print("Trying to apply unrecognized unary operator:", operator)
        raise ZRuntimeError
    opName = unaryOpNames[operator]
    try:
        opFunction = getattr(value, opName)
        return opFunction()
    except AttributeError:
        # That operator function does not exist for that value's class
        print("Wrong operand type for unary %s:" % operator, value.z_name)
        raise ZRuntimeError
    except ZeroDivisionError:
        # Inverting zero
        print("Attempting to apply unary %s to 0" % operator)
        raise ZRuntimeError

def reverseOpName(opName):
    if opName in reverseOpNames:
        return reverseOpNames[opName]
    else:
        opNameBase = opName.strip("z_")
        return "z_r" + opNameBase



