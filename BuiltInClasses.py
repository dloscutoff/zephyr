
# Built-in Zephyr classes

# A note about constructors--the standard order for checking types
# should go as follows:
#   - str
#   - Other Python types
#   - The Zephyr type being constructed
#   - Other Zephyr types

# Try to import the built-in gcd function; if it is not available, use the
# local reimplementation
try:
    from fractions import gcd
except ImportError:
    from Utilities import gcd

from Errors import OverrideError, ConstructorTypeError

def getClassName(obj):
    try:
        return obj.py_name
    except AttributeError:
        return str(obj.__class__)

class ZObject(object):
    py_name = "ZObject"
    z_name = "Object"
    tokenStart = tokenEnd = ""

    def __repr__(self):
        """By default, repr() returns the same thing as str() on a ZObject."""
        return str(self)
    
    def z_equal(self, rhs):
        """Objects are equal iff they are identical. Override in subclasses."""
        return self is rhs

    def z_notEqual(self, rhs):
        """x \= y <==> not(x = y)"""
        return self.z_equal(rhs).z_not()

    def z_concat(self, rhs):
        """Concatenate two values to a string (w/ space in between)"""
        return ZString('%s %s' % (self, rhs))

# Deprecated--use z_concat
    def z_spaceConcat(self, rhs):
        return ZString('%s %s' % (self, rhs))

class ZFunction(ZObject):
    py_name = "ZFunction"
    z_name = "Function"

    pass

class ZNumber(ZObject):
    py_name = "ZNumber"
    z_name = "Number"
    
    def z_plus(lhs, rhs):
        raise OverrideError("ZNumber", "z_plus")

    def z_times(lhs, rhs):
        raise OverrideError("ZNumber", "z_times")
    
    def z_lessThan(lhs, rhs):
        raise OverrideError("ZNumber", "z_lessThan")

    def z_negation(value):
        raise OverrideError("ZNumber", "z_negation")

    def z_inverse(value):
        raise OverrideError("ZNumber", "z_inverse")

    def z_rplus(rhs, lhs):
        """y + x <==> x + y"""
        return rhs.z_plus(lhs)
    
    def z_minus(lhs, rhs):
        """x - y <==> x + (-y)"""
        return lhs.z_plus(rhs.z_negation())

    def z_rminus(rhs, lhs):
        """y - x <==> (-x) + y"""
        return rhs.z_negation().z_plus(lhs)

    def z_rtimes(rhs, lhs):
        """y * x <==> x * y"""
        return rhs.z_times(lhs)
    
    def z_divide(lhs, rhs):
        """x / y <==> x * (/y)"""
        return lhs.z_times(rhs.z_inverse())

    def z_rdivide(rhs, lhs):
        """y / x <==> (/x) * y"""
        return rhs.z_inverse().z_times(lhs)
    
    def z_mod(lhs, modulo):
        if not isinstance(modulo, ZNumber):
            raise TypeError
        # Make a copy of <lhs> in <result>
        result = lhs.__class__(lhs)
        if modulo.sgn() == 1:
            # The modulo is positive
            # Decrease the result until it is < modulo
            while result.z_greaterThanEqual(modulo):
                result = result.z_minus(modulo)
            # Increase the result until is is >= 0
            while result.sgn() == -1:
                result = result.z_plus(modulo)
        elif modulo.sgn() == -1:
            # The modulo is negative
            # Increase the result until it is > modulo
            while result.z_lessThanEqual(modulo):
                result = result.z_minus(modulo)
            # Decrease the result until it is <= 0
            while result.sgn() == 1:
                result = result.z_plus(modulo)
        else:
            # The modulo is zero
            raise ZeroDivisionError
        return result

    def z_greaterThan(self, rhs):
        """x > y <==> not(x < y or x = y)"""
        less = self.z_lessThan(rhs)
        equal = self.z_equal(rhs)
        return less.z_or(equal).z_not()

    def z_lessThanEqual(self, rhs):
        """x <= y <==> x < y or x = y"""
        less = self.z_lessThan(rhs)
        equal = self.z_equal(rhs)
        return less.z_or(equal)

    def z_greaterThanEqual(self, rhs):
        """x >= y <==> not(x < y)"""
        return self.z_lessThan(rhs).z_not()

    def z_inc(self):
        """Incrementing x gives x + 1"""
        return self.z_plus(ZInteger(1))
    
    def sgn(self):
        """Utility function to return the sign of a ZNumber.
        Override in subclasses for more efficient implementation."""
        zero = ZInteger(0)
        if self.z_lessThan(zero):
            return -1
        elif self.z_equal(zero):
            return 0
        else:
            return 1

class ZInteger(ZNumber):
    py_name = "ZInteger"
    z_name = "Integer"
    
    def __new__(cls, *args):
        self = super(ZInteger, cls).__new__(cls)
        if len(args) == 1:
            if type(args[0]) == str:
                # Convert a Python string
                self.value = int(args[0])
            elif type(args[0]) == int:
                # Convert a Python integer
                self.value = args[0]
            elif args[0].__class__ == ZInteger:
                # Convert another Zephyr integer
                self.value = args[0].value
            elif args[0].__class__ == ZFraction:
                # Convert a Zephyr fraction (by truncating toward 0)
                if args[0].sgn() == 1:
                    self.value = args[0].num // args[0].den
                else:
                    self.value = -(abs(args[0].num) // args[0].den)
            else:
                expectedTypes = "str, int, ZInteger, or ZFraction"
                raise ConstructorTypeError(cls.py_name,
                                            expectedTypes,
                                            getClassName(args[0]))
        else:
            expectedNumber = "1 argument"
            raise ConstructorTypeError(cls.py_name,
                                        expectedNumber,
                                        len(args))
        return self

    def __str__(self):
        return str(self.value)

    def z_plus(self, rhs):
        if rhs.__class__ == ZInteger:
            return ZInteger(self.value + rhs.value)
        else:
            raise TypeError
    
    def z_times(self, rhs):
        if rhs.__class__ == ZInteger:
            return ZInteger(self.value * rhs.value)
        else:
            raise TypeError

    def z_lessThan(self, rhs):
        if rhs.__class__ == ZInteger:
            return ZBoolean(self.value < rhs.value)
        else:
            raise TypeError

    def z_equal(self, rhs):
        if rhs.__class__ == ZInteger:
            return ZBoolean(self.value == rhs.value)
        else:
            return False

    def z_negation(self):
        return ZInteger(-self.value)

    def z_inverse(self):
        return ZFraction(1, self.value)
    
    def sgn(self):
        if self.value > 0:
            return 1
        elif self.value == 0:
            return 0
        else:
            return -1

class ZFraction(ZNumber):
    py_name = "ZFraction"
    z_name = "Fraction"
    
    def __new__(cls, *args):
        self = super(ZFraction, cls).__new__(cls)
        if len(args) == 1:
            if args[0].__class__ == str:
                # Convert a Python string
                if '/' not in args[0]:
                    # If only one number was given, treat it as an Integer
                    return ZInteger(args[0])
                else:
                    num, den = args[0].split('/')
                    self.num = int(num)
                    self.den = int(den)
            elif args[0].__class__ == ZFraction:
                # Convert another Zephyr fraction
                self.num = args[0].num
                self.den = args[0].den
            elif args[0].__class__ == ZInteger:
                # "Convert" a Zephyr integer
                return ZInteger(args[0])
            else:
                expectedTypes = "ZFraction or ZInteger"
                raise ConstructorTypeError(cls.py_name,
                                            expectedTypes,
                                            getClassName(args[0]))
        elif len(args) == 2:
            if type(args[0]) == type(args[1]) == int:
                # Convert a pair of Python ints
                self.num = args[0]
                self.den = args[1]
            else:
                expectedTypes = "int"
                raise ConstructorTypeError(cls.py_name,
                                            expectedTypes,
                                            (getClassName(args[0]),
                                              getClassName(args[1])))
        else:
            expectedNumber = "1 or 2 arguments"
            raise ConstructorTypeError(cls.py_name,
                                        expectedNumber,
                                        len(args))
        # Normalize before storing
        if self.den < 0:
            self.num *= -1
            self.den *= -1
        elif self.den == 0:
            raise ZeroDivisionError
        this_gcd = abs(gcd(self.num, self.den))
        self.num //= this_gcd
        self.den //= this_gcd
        if self.den == 1:
            # If the denominator is 1, return an Integer instead
            return ZInteger(self.num)
        else:
            return self

    def __str__(self):
        return "%s/%s" % (self.num, self.den)

    def z_plus(self, rhs):
        if rhs.__class__ == ZFraction:
            # a/b + c/d <==> (a*d + b*c)/(b*d)
            return ZFraction(self.num * rhs.den + self.den * rhs.num,
                              self.den * rhs.den)
        elif rhs.__class__ == ZInteger:
            # a/b + n <==> (a + n*b)/b
            return ZFraction(self.num + self.den * rhs.value, self.den)
        else:
            raise TypeError
    
    def z_times(self, rhs):
        if rhs.__class__ == ZFraction:
            # a/b * c/d <==> (a*c)/(b*d)
            return ZFraction(self.num * rhs.num, self.den * rhs.den)
        elif rhs.__class__ == ZInteger:
            # a/b * n <==> (a*n)/b
            return ZFraction(self.num * rhs.value, self.den)
        else:
            raise TypeError

    def z_lessThan(self, rhs):
        diff = self.z_minus(rhs)
        if diff.sgn() == -1:
            # self - rhs < 0, so self < rhs
            return ZBoolean(True)
        else:
            # self - rhs >= 0, so not(self < rhs)
            return ZBoolean(False)

    def z_equal(self, rhs):
        if rhs.__class__ == ZFraction:
            return (self.num == rhs.num and self.den == rhs.den)
        else:
            # No need to test for ZInteger, since no ZFraction has a
            # denominator of 1
            return False

    def z_negation(self):
        return ZFraction(-self.num, self.den)

    def z_inverse(self):
        return ZFraction(self.den, self.num)
    
    def sgn(self):
        if self.num > 0:
            return 1
        elif self.num == 0:
            return 0
        else:
            return -1

class ZBoolean(ZObject):
    py_name = "ZBoolean"
    z_name = "Boolean"
    
    def __new__(cls, *args):
        self = super(ZBoolean, cls).__new__(cls)
        if len(args) == 1:
            if type(args[0]) == str:
                # Convert a Python string
                string = args[0].lower()
                if string.startswith("t") or string.startswith("y"):
                    self.value = True
                else:
                    self.value = False
            elif type(args[0]) == bool:
                # Convert a Python boolean
                self.value = args[0]
            elif args[0].__class__ == ZBoolean:
                # Convert another Zephyr boolean
                self.value = args[0].value
            else:
                expectedTypes = "str, bool, or ZBoolean"
                raise ConstructorTypeError(cls.py_name,
                                            expectedTypes,
                                            getClassName(args[0]))
        else:
            expectedNumber = "1 argument"
            raise ConstructorTypeError(cls.py_name,
                                        expectedNumber,
                                        len(args))
        return self

    def __str__(self):
        if self.value == True:
            return "true"
        else:
            return "false"

    def __bool__(self):
        return self.value
    
    def z_and(self, rhs):
        if rhs.__class__ == ZBoolean:
            return ZBoolean(self.value and rhs.value)
        else:
            raise TypeError
    
    def z_or(self, rhs):
        if rhs.__class__ == ZBoolean:
            return ZBoolean(self.value or rhs.value)
        else:
            raise TypeError

    def z_not(self):
        return ZBoolean(not self.value)

    def z_equal(self, rhs):
        if rhs.__class__ == ZBoolean:
            return ZBoolean(self.value == rhs.value)
        else:
            return False

class ZCharacter(ZObject):
    py_name = "ZCharacter"
    z_name = "Character"
    tokenStart = tokenEnd = "'"

    def __new__(cls, *args):
        self = super(ZCharacter, cls).__new__(cls)
        if len(args) == 1:
            if args[0].__class__ == str:
                # Convert a Python string
                self.value = args[0][0]
            elif args[0].__class__ == ZCharacter:
                self.value = args[0].value
            elif args[0].__class__ == ZInteger:
                try:
                    self.value = chr(args[0].value)
                except ValueError:
                    raise
            else:
                expectedTypes = "str, ZCharacter, or ZInteger"
                raise ConstructorTypeError(cls.py_name,
                                            expectedTypes,
                                            getClassName(args[0]))
        else:
            expectedNumber = "1 argument"
            raise ConstructorTypeError(cls.py_name,
                                        expectedNumber,
                                        len(args))
        return self

    def __str__(self):
        # str returns the character sans single-quotes
        return self.value
    
    def __repr__(self):
        # repr puts single-quotes around the character
        return "'%s'" % self.value

    def z_lessThan(self, rhs):
        if rhs.__class__ == ZCharacter:
            return ZBoolean(self.value < rhs.value)
        else:
            raise TypeError

    def z_equal(self, rhs):
        if rhs.__class__ == ZCharacter:
            return ZBoolean(self.value == rhs.value)
        else:
            return False

class ZString(ZObject):
    py_name = "ZString"
    z_name = "String"
    tokenStart = tokenEnd = '"'

    def __new__(cls, *args):
        self = super(ZString, cls).__new__(cls)
        if len(args) == 1:
            if args[0].__class__ == str:
                # Convert a Python string
                self.value = args[0]
            elif isinstance(args[0], ZObject):
                # Cast a Zephyr object to a string
                self.value = str(args[0])
            else:
                expectedTypes = "str or ZObject subclass"
                raise ConstructorTypeError(cls.py_name,
                                            expectedTypes,
                                            getClassName(args[0]))
        else:
            expectedNumber = "1 argument"
            raise ConstructorTypeError(cls.py_name,
                                        expectedNumber,
                                        len(args))
        return self

    def __str__(self):
        return self.value

    def __repr__(self):
        return '"%s"' % self.value

    def z_lessThan(self, rhs):
        if rhs.__class__ == ZString:
            return ZBoolean(self.value < rhs.value)
        else:
            raise TypeError

    def z_equal(self, rhs):
        if rhs.__class__ == ZString:
            return ZBoolean(self.value == rhs.value)
        else:
            return False

    def z_plus(self, rhs):
        """string + x ==> concatenation"""
        return ZString('%s%s' % (self, rhs))

    def z_rplus(rhs, lhs):
        """x + string ==> concatenation"""
        return ZString('%s%s' % (lhs, rhs))

    def z_subscript(self, index):
        if index.__class__ == ZInteger:
            if index.value >= 1 and index.value <= len(self.value):
                char = self.value[index.value-1]
                return ZCharacter(char)
            else:
                raise IndexError
        else:
            raise TypeError

    def z_section(self, start, stop):
        if start.__class__ == ZInteger and stop.__class__ == ZInteger:
            if start.value < 1:
                start = ZInteger(1)
            if stop.value > len(self.value):
                stop = ZInteger(len(self.value))
            if start.value > stop.value:
                return ZString("")
            else:
                string = self.value[start.value-1:stop.value]
                return ZString(string)
        else:
            raise TypeError
    
class ZArray(ZObject):
    py_name = "ZArray"
    z_name = "Array"
    
    def __new__(cls, *args):
        self = super(ZArray, cls).__new__(cls)
        if len(args) == 1:
            if args[0].__class__ == int:
                # Create an array with the given size
                self.size = args[0]
            elif args[0].__class__ == ZInteger:
                # Create an array with the given size
                self.size = args[0].value
            else:
                expectedTypes = "int or ZInteger"
                raise ConstructorTypeError(cls.py_name,
                                            expectedTypes,
                                            getClassName(args[0]))
        else:
            expectedNumber = "1 argument"
            raise ConstructorTypeError(cls.py_name,
                                        expectedNumber,
                                        len(args))
        # Return a memory operation consisting of the number of variables
        # needed
        return (self, self.size)

    def assignAddress(self, address):
        self.address = address

    def __str__(self):
        # Could change
        return "Array(%d)" % self.size
    
    def __repr__(self):
        return "Array(%d,v%d)" % (self.size, self.address)

    def z_subscript(self, index):
        if index.__class__ == ZInteger:
            if index.value >= 1 and index.value <= self.size:
                return self.address + index.value - 1
            else:
                raise IndexError
        else:
            raise TypeError


