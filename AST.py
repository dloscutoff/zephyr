
import subprocess
import os

dotFilename = "syntaxTree.dot"
pdfFilename = "syntaxTree.pdf"
dotProgram = r"C:\Program Files\Graphviz2.26\bin\dot.exe"

class TreeNode:
    def __init__(self, name, *children):
        self.name = name
        self.children = []
        for child in children:
            self.addChild(child)

    def __str__(self):
        return str(self.name)

    def addChild(self, otherNode):
        if otherNode is None:
            # Given a null child node, do nothing
            pass
        elif otherNode.__class__ == TempNode:
            # If it's a temporary node, don't add it but its children
            self.children.extend(otherNode.children)
        else:
            # For any other kind of node, just add it
            self.children.append(otherNode)

class TempNode(TreeNode):
    def __init__(self):
        super().__init__("(temporary node)")

def treeDump(rootNode):
    #treePrint(rootNode)
    dotDump(rootNode)

def treePrint(rootNode):
    recursivePrint(rootNode, 0)

def recursivePrint(node, numSpaces):
    print("%s%s" % (" " * numSpaces, node))
    if node.__class__ == TreeNode:
        for child in node.children:
            recursivePrint(child, numSpaces + 2)

def dotDump(rootNode):
    global dotFilename, pdfFilename, dotProgram
    dotString = "digraph ParseTree {\n"
    dotString += recursiveDotFormat(rootNode, "node1")
    dotString += "}\n"
    if dotFilename is not None:
        # Write the data to the dot file
        dotFile = open(dotFilename, "w")
        dotFile.write(dotString)
        dotFile.close()
        # Remove the pdf if it exists
        try:
            os.remove(pdfFilename)
        except:
            pass
        # Generate the pdf file from the dot file
        subprocess.call([ dotProgram, "-Tpdf", dotFilename, "-o",
                           pdfFilename ])
        # Delete the dot file
        os.remove(dotFilename)
    else:
        print(dotString, end=' ')

def recursiveDotFormat(node, nodeId):
    subtreeString = ""
    if node.__class__ == TreeNode:
        subtreeString += "    %s [label=\"%s\"];\n" \
                                 % (nodeId, str(node))
        for index, child in enumerate(node.children):
            childId = nodeId + str(index + 1)
            subtreeString += "    %s -> %s;\n" % (nodeId, childId)
        for index, child in enumerate(node.children):
            childId = nodeId + str(index + 1)
            subtreeString += recursiveDotFormat(child, childId)
    else:
        if node.value == '\n':
            valueDisplay = r"'\\n'"
        else:
            valueDisplay = repr(node.value)
        subtreeString += '    %s [shape=box,style=filled,label="%s\\n%s"];\n' \
                         % (nodeId, node.name, valueDisplay)
    return subtreeString




