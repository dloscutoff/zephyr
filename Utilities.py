
# Utility functions

def processCmdLineArgs():
    import sys
    options = { "filename": None,
                "debug": False }
    for item in sys.argv[1:]:
        if item == "-d":
            options["debug"] = True
        elif item[0] != "-":
            options["filename"] = item
    return options

def gcd(num1, num2):
    """Function to mimic the functionality of fractions.gcd()
    when the fractions package is unavailable."""
    if num2 == 0:
        return num1
    elif num1 == 0:
        return num2
    else:
        if num2 > 0:
            sign = 1
        else:
            sign = -1
        return sign * r_gcd(abs(num1), abs(num2))

def r_gcd(num1, num2):
    """Recursive helper function for gcd.
    Assumes that num1 and num2 are both > 0."""
    if num1 == num2:
        # gcd(x, x) == x
        return num1
    elif num1 > num2:
        bigger = num1
        smaller = num2
    else:
        # num2 > num1
        bigger = num2
        smaller = num1
    new = bigger % smaller
    if new == 0:
        return smaller
    else:
        return r_gcd(smaller, new)

def removeFromFront(string, substring):
    if substring and string.startswith(substring):
        return string[ len(substring) : ]
    else:
        return string

def removeFromEnd(string, substring):
    if substring and string.endswith(substring):
        return string[ : -len(substring) ]
    else:
        return string

