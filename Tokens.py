
import re
from Errors import TokenError
import sys
import os

REGEX_FILENAME = "Regexes.txt"

def loadRegexes():
    dictionary = {}
    # We assume that the regex file is in the same directory as this code
    path = os.path.dirname(os.path.abspath(__file__))
    regFile = open(os.path.join(path, REGEX_FILENAME), 'r')
    for line in regFile:
        if line[0] == "#":
            continue
        name, regStr = [ part.strip() for part in line.split("::=") ]
        regex = re.compile(regStr, re.MULTILINE)
        dictionary[name] = regex
    regFile.close()
    return dictionary

tokenRegexes = loadRegexes()

class Token:
    """Token base class."""
    priority = 1
    regex = None
    def __init__(self, value = None):
        self._name = self.__class__.__name__
        self._value = value

    def __str__(self):
        return "<%s:%s>" % (self._name, repr(self._value))
    
    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def hasType(self, type):
        if type == self._name.lower():
            return True
        else:
            return False

    def hasValue(self, value):
        if value == self._value:
            return True
        else:
            return False

    def compatible(self, type = None, value = None):
        if type and not self.hasType(type):
            return False
        if value and not self.hasValue(value):
            return False
        return True



class Symbol(Token): pass
class Operator(Token): pass
class EOL(Token): pass
class Keyword(Token): pass
class Name(Token):
    # Names must have lower priority than Keywords, Operators, and Booleans
    priority = 0
class Integer(Token): pass
class Boolean(Token): pass
class Character(Token): pass
class String(Token): pass
class Space(Token): pass
class SingleComment(Token): pass
class MultiComment(Token): pass
class EOF(Token): pass
class Unknown(Token):
    # Unknown is a catch-all, and, as such, must have the lowest priority
    priority = -1


# Fill tokenClasses with all token types that are associated with regexes
tokenClasses = []
for tokenName, tokenRegex in tokenRegexes.items():
    try:
        TokenClass = vars()[tokenName]
    except KeyError:
        raise NameError("no class for token type %s" % tokenName)
    else:
        TokenClass.regex = tokenRegex
        tokenClasses.append(TokenClass)


def tokenize(codeString):
    """Generator function that yields tokens from <codeString>."""
    global tokenClasses
    pos = 0
    while pos < len(codeString):
        # Find the longest regex token match in codeString starting at pos
        longestMatch = None
        lmTokenClass = None
        for TokenClass in tokenClasses:
            # Match on codeString starting at pos
            matchObj = TokenClass.regex.match(codeString, pos)
            if matchObj is not None and \
                    (longestMatch is None 
                      or matchObj.end() > longestMatch.end()
                      or matchObj.end() == longestMatch.end()
                          and TokenClass.priority > lmTokenClass.priority
                    ):
                # This nonempty match is the new longest (or highest-priority)
                # match
                longestMatch = matchObj
                lmTokenClass = TokenClass
        if longestMatch is not None:
            # The longest regex match is now in longestMatch
            # Update pos to the character after this match
            pos = longestMatch.end()
            # Yield an instance of the longest-match token class containing
            # the matched data
            yield lmTokenClass(longestMatch.group())
        else:
            # No token matched the given code string
            nlIndex = codeString.find('\n', pos)
            restOfLine = codeString[pos:nlIndex]
            raise TokenError("could not match '%s'" % restOfLine)


