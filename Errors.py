
class TokenError(Exception): pass
class BNFError(Exception): pass
class ZRuntimeError(Exception): pass

class ParseError(Exception):
    def __init__(self, message, token = None):
        super().__init__(message)
        self.token = token

class OverrideError(Exception):
    def __init__(self, className, funcName):
        message = "Failed to override abstract method %s of class %s" \
                  % (funcName, className)
        super().__init__(message)

class ConstructorTypeError(TypeError):
    def __init__(self, className, expected, given):
        message = "%s constructor expected %s; given %s" \
                  % (className, expected, given)
        super().__init__(message)


