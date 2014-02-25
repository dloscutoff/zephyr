
from Errors import ParseError, BNFError
import os

class BNFObject:
    symbols = None
    def __init__(self, value, permanent = False):
        self.value = value
        self.permanent = permanent

    def __str__(self):
        return self.left + str(self.value) + self.right

    # The __hash__ and __eq__ methods are implemented to allow manipulation
    # of BNFObject instances using sets.
    
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        result = False
        if self.__class__ == other.__class__:
            if self.value == other.value:
                result = True
        return result

    @property
    def left(self):
        if self.symbols is not None:
            return self.symbols[0]
        else:
            return ""

    @property
    def right(self):
        if self.symbols is not None:
            return self.symbols[1]
        else:
            return ""

class Nonterminal(BNFObject): pass
class Terminal(BNFObject): symbols = "<>"
class Literal(BNFObject): symbols = '""'

def makeBNFObject(string):
    if string[0] == "@":
        string = string[1:]
        permanent = True
    else:
        permanent = False
    if string == '""':
        # This is an "epsilon"
        return None
    elif string[0] == '"':
        # Strip the quotes and return a Literal object
        return Literal(string[1:-1], permanent)
    elif string[0] == "<":
        # Strip the angle brackets and return a Terminal object
        return Terminal(string[1:-1], permanent)
    else:
        # Not a literal or terminal; must be a nonterminal
        return Nonterminal(string, permanent)

class Production:
    def __init__(self, nonterm, rhsList):
        self.nonterm = nonterm
        self.rhsList = rhsList

    def __str__(self):
        result = "%s ::=" % self.nonterm
        for item in self.rhsList:
            result += " %s" % item
        return result

class Grammar:
    def __init__(self, BNF_filename = None):
        self.productions = []
        self.nonterms = []
        self.nontermProdNums = {}
        self.startSymbol = None
        self.firstSets = {}
        self.followSets = {}
        self.selectSets = []
        self.parseTable = {}
        if BNF_filename is not None:
            self.loadFromFile(BNF_filename)
    
    def loadFromFile(self, BNF_filename):
        currNonterm = None
        prodNum = 0
        currProdNumStart = None
        # We assume that the BNF file is in the same directory as this code
        path = os.path.dirname(os.path.abspath(__file__))
        f = open(os.path.join(path, BNF_filename), 'r')
        for line in f:
            if "::=" in line:
                lhs, rhs = [ half.strip() for half in line.split("::=") ]
                if lhs == "":
                    # No explicit nonterminal given
                    if self.startSymbol is None:
                        # This is the first line of the file--we have a problem
                        raise BNFError("Start symbol not specified")
                    else:
                        # Use the previous nonterminal
                        nonterm = currNonterm
                else:
                    # New nonterminal
                    nonterm = makeBNFObject(lhs)
                    self.nonterms.append(nonterm)
                    if self.startSymbol is None:
                        # This is the first production of the file; treat it as
                        # the start symbol
                        self.startSymbol = nonterm
                        currProdNumStart = 0
                    else:
                        # We're switching nonterminals
                        self.nontermProdNums[currNonterm] \
                                        = (currProdNumStart, prodNum)
                        currProdNumStart = prodNum
                    currNonterm = nonterm
                rhsList = [ makeBNFObject(rhsItem) \
                                        for rhsItem in rhs.split() ]
                self.productions.append(Production(nonterm, rhsList))
                prodNum += 1
        self.nontermProdNums[currNonterm] = (currProdNumStart, prodNum)
        f.close()
        self.makeParseTable()

    def output(self):
        print("Start symbol is %s" % self.startSymbol)
        for prod in self.productions:
            print(prod)

    def findProduction(self, nonterm, token):
        """Find the correct production for the given nonterm and token."""
        for prodNum in range(*self.nontermProdNums[nonterm]):
            for symbol in self.selectSets[prodNum]:
                if symbol.__class__ == Terminal \
                           and token.compatible(type = symbol.value) \
                       or symbol.__class__ == Literal \
                           and token.compatible(value = symbol.value):
                    return self.productions[prodNum]
        raise ParseError("failed while parsing %s at %s" \
                          % (nonterm, token), token)
    
    def makeParseTable(self):
        self.generateSelectSets()
        for prodNum, prod in enumerate(self.productions):
            for symbol in self.selectSets[prodNum]:
                key = (prod.nonterm, symbol)
                if key in self.parseTable:
                    raise BNFError("Duplicate parse table entry: " \
                                    + "productions %d and %d both match " \
                                    + "(%s, %s)" \
                                    % (prodNum, self.parseTable[key],
                                        prod.nonterm, symbol))
                self.parseTable[key] = prodNum
    
    def generateSelectSets(self):
        self.generateFirstSets()
        self.generateFollowSets()
        for prod in self.productions:
            selectSet = self.first(prod.rhsList)
            if None in selectSet:
                selectSet.discard(None)
                selectSet.update(self.follow(prod.nonterm))
            self.selectSets.append(selectSet)
            
    def outputSelectSets(self):
        # Calculate how much of an indent we need for everything to line up
        indent = 0
        for nonterm in self.nonterms:
            if indent < len(nonterm.value) + 1:
                indent = len(nonterm.value) + 1
        # Output the select sets
        currNonterm = None
        for prodNum, prod in enumerate(self.productions):
            if prod.nonterm is not currNonterm:
                nontermHeader = "%s:" % prod.nonterm
                print(nontermHeader \
                      + " " * (indent - len(nontermHeader)), end=' ')
                currNonterm = prod.nonterm
            else:
                print(" " * indent, end=' ')
            print("%d {" % (prodNum + 1), end=' ')
            print(", ".join(str(item) for item in self.selectSets[prodNum]), end=' ')
            print("}")

    def generateFollowSets(self):
        for nonterm in self.nonterms:
            # Mark where the process started to avoid infinite recursion
            self.cycleStart = nonterm
            # Call follow on each nonterminal, which automatically adds entries
            # to self.followSets as necessary
            self.follow(nonterm)

    def follow(self, nonterm):
        """Returns the follow set of <nonterm>.
        If <nonterm> doesn't have an entry in self.followSets, the function
        calls partialFollowSet to generate the set and then stores it."""
        if nonterm in self.followSets:
            followSet = self.followSets[nonterm]
        else:
            # The follow set of nonterm is not stored yet; find it
            followSet = self.preliminaryFollowSet(nonterm, [ nonterm ])
            self.followSets[nonterm] = followSet
        return followSet

    def preliminaryFollowSet(self, nonterm, prevNonterms):
        result = set()
        if nonterm is self.startSymbol:
            # If it's the start symbol, add EOF
            result.add(Terminal("eof"))
        for prod in self.productions:
            # Scan production right-hand sides for nonterm
            try:
                ntIndex = prod.rhsList.index(nonterm)
            except ValueError:
                # nonterm isn't in this production; go to the next one
                continue
            # Otherwise, nonterm was found at index ntIndex
            # Loop through the remaining symbols in that production
            # If they look like A B, include first(A); if that contains
            # epsilon, delete it and include first(B); if that contains
            # epsilon, delete it and include the (preliminary) follow set of
            # the left-hand side of the production
            result.add(None)
            for i in range(ntIndex + 1, len(prod.rhsList)):
                symbol = prod.rhsList[i]
                symbolFirst = self.first(symbol)
                result.update(symbolFirst)
                if None not in symbolFirst:
                    # Reached a non-nullable symbol; discard any epsilon
                    # that may have been there from previous symbols, and
                    # then stop adding stuff
                    result.discard(None)
                    break
            if None in result:
                # If result still contains epsilon, all the rhs symbols must
                # have been nullable
                result.discard(None)
                # Find the follow set of the left-hand side of the production
                # (but ignore any lhs that's in the list of nonterminals
                # whose follow sets we were trying to find earlier in this
                # call stack) and add it to this nonterminal's follow set
                if prod.nonterm not in prevNonterms:
                    prevNonterms.append(prod.nonterm)
                    result.update(self.preliminaryFollowSet(prod.nonterm,
                                                              prevNonterms))
                    prevNonterms.pop()

        return result
            
    def outputFollowSets(self):
        for nonterm in self.orderedNonterms():
            print("%s: {" % nonterm, end=' ')
            print(", ".join(str(item) for item in self.followSets[nonterm]), end=' ')
            print("}")

    def generateFirstSets(self):
        for nonterm in self.nonterms:
            # Call first on each nonterminal, which automatically adds entries
            # to self.firstSets as necessary
            self.first(nonterm)

    def first(self, item):
        """Returns the first set of <item>.
        If <item> is a nonterminal that doesn't have an entry in
        self.firstSets, the function calls makeFirstSet to rectify that
        problem."""
        if item.__class__ == Nonterminal:
            # Item is a nonterminal
            if item not in self.firstSets:
                self.makeFirstSet(item)
            return self.firstSets[item]
        elif item.__class__ == list:
            # Item is the right-hand side of a production
            # first(A B C) contains first(A); if A is nullable then
            # add first(B); if B is nullable then add first(C); if
            # all are nullable then add epsilon.
            result = set()
            for rhsItem in item:
                itemFirst = self.first(rhsItem)
                result.update(itemFirst)
                if None not in itemFirst:
                    # Reached a non-nullable symbol; discard any epsilon that
                    # may have been there from previous nullable symbols,
                    # and then stop adding stuff
                    result.discard(None)
                    break
            # If all rhsItems were nullable, None is already in result
            return result
        else:
            # Item must be a terminal
            return set([ item ])

    def makeFirstSet(self, nonterm):
        result = set()
        for prodNum in range(*self.nontermProdNums[nonterm]):
            prod = self.productions[prodNum]
            result.update(self.first(prod.rhsList))
        self.firstSets[nonterm] = result

    def outputFirstSets(self):
        for nonterm in self.orderedNonterms():
            print("%s: {" % nonterm, end=' ')
            print(", ".join(str(item) for item in self.firstSets[nonterm]), end=' ')
            print("}")

    def orderedNonterms(self):
        """Returns an ordered list of the nonterminals in the grammar.
        The list is sorted based on the order of nonterminals in the
        original BNF file."""
        pairs = []
        for nonterm, prodNums in self.nontermProdNums.items():
            pairs.append((prodNums, nonterm))
        pairs.sort()
        return [ nonterm for prodNums, nonterm in pairs ]

    def nontermPermanent(self, nonterm):
        for nt in self.nonterms:
            if nt == nonterm:
                return nt.permanent

def loadGrammar(BNF_filename):
    grammar = Grammar()
    grammar.loadFromFile(BNF_filename)
    return grammar


if __name__ == "__main__":
    # Test code
    grammar = loadGrammar("BNF.txt")
    grammar.output()
    print()
    print("FIRST SETS:")
    grammar.outputFirstSets()
    print()
    print("FOLLOW SETS:")
    grammar.outputFollowSets()
    print()
    print("SELECT SETS:")
    grammar.outputSelectSets()


