
from BuiltInClasses import *

class ProgramState:
    """Class containing the internal state of a program."""
    def __init__(self):
        self.symbols = {}
        self.variables = []
        self.memory = []
        self.reservedMemory = {}
        self.reservedSize = 514

    def output(self):
        print("-" * 70)
        print()
        print("SYMBOL TABLE:")
        for varName, varId in self.symbols.items():
            print("%8s  %s" % (varName, "v%d" % varId))
        print()
        print("VARIABLES:")
        for varId, (address, type) in enumerate(self.variables):
            if address == -1:
                print("%8s  %s" % ("v%d" % varId, "-"))
            else:
                print("%8s  %-10s  %s" % ("v%d" % varId,
                                          type.z_name, "a%d" % address))
        print()
        print("RESERVED MEMORY:")
        for address, value in self.reservedMemory.items():
            print("%8s  %s" % ("a%d" % address, repr(value)))
        print()
        print("MEMORY:")
        for realAddress, value in enumerate(self.memory):
            address = realAddress + self.reservedSize
            print("%8s  %s" % ("a%d" % address, repr(value)))

    def getVarId(self, varname):
        """Gets the ID for the given variable name.
        If no variable by that name exists, create a new one."""
        if varname not in self.symbols:
            self.symbols[varname] = self.createVariable()
        return self.symbols[varname]

    def createVariable(self, type = ZObject):
        """Creates a new (uninitialized) variable and returns its ID."""
        varId = len(self.variables)
        self.variables.append((-1, type))
        return varId

    def createVariables(self, number, type = ZObject):
        """Creates a block of new variables and returns the first one's ID."""
        startId = len(self.variables)
        for i in range(number):
            self.variables.append((-1, type))
        return startId
    
    def getVarAddress(self, varId):
        """Gets the memory address assocated with the given variable ID.
        If no variable by that ID exists, raises KeyError."""
        try:
            return self.variables[varId][0]
        except IndexError:
            raise KeyError

    def getVarType(self, varId):
        """Gets the type associated with the given variable ID.
        If no variable by that ID exists, raises KeyError."""
        try:
            return self.variables[varId][1]
        except IndexError:
            raise KeyError

    def setVarAddress(self, varId, address):
        """Sets the memory address associated with the given variable ID.
        Finds the varId's associated type; if it matches the type of the
        item at the given address, sets the varId's address to the given
        address. If the types do not match, raises TypeError; if the
        variable does not exist, raises KeyError."""
        varType = self.getVarType(varId)
        value = self.recall(address)
        if isinstance(value, varType):
            self.variables[varId] = (address, varType)
        else:
            raise TypeError

    def memorize(self, item):
        """Places the given item in memory and returns the virtual address."""
        # Determine whether the item is or should be in reserved memory
        reserved = False
        if item.__class__ == ZBoolean:
            reserved = True
            if item.value is False:
                address = 0
            else:
                address = 1
        elif item.__class__ == ZInteger and item.value >= -256 \
                                      and item.value < 256:
            reserved = True
            if item.sgn() >= 0:
                # Nonnegative ZInteger
                address = item.value * 2 + 2
            else:
                # Negative ZInteger
                address = -item.value * 2 + 1
        if reserved and address not in self.reservedMemory:
            # The item isn't stored yet; store it
            self.reservedMemory[address] = item
        elif not reserved:
            # Shove the item in regular memory and get the virtual address
            realAddress = len(self.memory)
            self.memory.append(item)
            address = realAddress + self.reservedSize
        return address

    def recall(self, address):
        """Returns the item at the given virtual address.
        If the address is -1, raises ValueError; if there is no item at
        the given (positive) address, raises KeyError."""
        if address == -1:
            # Must be trying to recall a value for an uninitialized variable
            raise ValueError
        elif address < self.reservedSize:
            # Address in reserved memory
            try:
                return self.reservedMemory[address]
            except KeyError:
                # What to do in the case of a miss in reserved memory?
                # We could just raise the error, or we could generate the
                # correct object, store it, and then return it.
                # For now, we'll go with the one-liner:
                raise KeyError
        else:
            # Address in regular memory
            realAddress = address - self.reservedSize
            try:
                return self.memory[realAddress]
            except IndexError:
                raise KeyError

    def getValue(self, entity):
        """Returns the value associated with the given entity:
            - If the entity is a name, finds the associated varId and returns
              its value recursively.
            - If the entity is a varId, finds the associated address and then
              returns the value at that address in (virtual) memory.
            - If the entity is a value already, returns it unchanged.
        If the variable does not exist, raises KeyError; if the variable is
        not associated with a value, raises ValueError."""
        if isinstance(entity, str):
            varId = self.getVarId(entity)
            return self.getValue(varId)
        elif isLValue(entity):
            address = self.getVarAddress(entity)
            return self.recall(address)
        else:
            return entity


def isLValue(entity):
    # Currently, an lvalue is an int
    return isinstance(entity, int)


