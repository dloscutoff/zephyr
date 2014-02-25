
from Tokens import tokenize
import Tokens
from Errors import ParseError

class Scanner:
    def __init__(self, codeString):
        self.tokenList = [ token for token in tokenize(codeString) ]
        # Insert explicit EOF token
        self.tokenList.append(Tokens.EOF())
        self.index = 0
        self.fastForward()

    def fastForward(self):
        """Skips past whitespace and comments."""
        done = False
        while not done:
            token = self.tokenList[self.index]
            if token.name != "Space" and token.name != "SingleComment" \
                                    and token.name != "MultiComment":
                done = True
            else:
                self.index += 1
    
    def lookAhead(self):
        return self.tokenList[self.index]

    def match(self, type = None, value = None):
        token = self.tokenList[self.index]
        if token.compatible(type, value):
            # Advance to the next meaningful token
            self.index += 1
            self.fastForward()
            # Return the stored token
            return token
        else:
            errMessage = "Token %s did not match against" % token
            if type is not None:
                errMessage += " type %s" % type
            if value is not None:
                errMessage += " value %s" % value
            raise ParseError(errMessage, token)
    
def testScanner(filename = None):
    if filename != None:
        # Read code from file
        f = open(filename, 'r')
        code = f.read()
        f.close()
    else:
        # Use pre-canned code
        code = """
set x to 14 + 3 # Single-line comment
print (x - 4) * 2   #
#-- Multiline comment
    containing #- various stuff #--#
#-## Another multiline -#
"""
    scanner = Scanner(code)
    for token in scanner.tokenList:
        if token.name != "Space":
            print(token)

if __name__ == "__main__":
    #testScanner("test1.zeph")
    testScanner()
