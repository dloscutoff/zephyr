
import BNF
from AST import TreeNode, TempNode
from Errors import ParseError

def parse(scanner, grammar):
    try:
        return parseNonterm(grammar.startSymbol, scanner, grammar)
    except ParseError as e:
        if e.token is not None:
            print("Encountered syntax error: was not expecting %s" \
                  % repr(e.token.value))
        else:
            print("Encountered syntax error")
        raise

def parseNonterm(nonterm, scanner, grammar):
    if grammar.nontermPermanent(nonterm):
        node = TreeNode(str(nonterm))
    else:
        node = TempNode()
    la = scanner.lookAhead()
    prod = grammar.findProduction(nonterm, la)
    for symbol in prod.rhsList:
        if symbol.__class__ == BNF.Nonterminal:
            childNode = parseNonterm(symbol, scanner, grammar)
            node.addChild(childNode)
        elif symbol.__class__ == BNF.Terminal:
            token = scanner.match(type = symbol.value)
            if symbol.permanent:
                node.addChild(token)
        elif symbol.__class__ == BNF.Literal:
            token = scanner.match(value = symbol.value)
            if symbol.permanent:
                node.addChild(token)
    return node


