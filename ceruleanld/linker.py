import os
import sys
import argparse
import json

# =================================================================================================

class Linker:
    def __init__(self, debug=False):
        self.shouldPrintDebug = debug
        pass

    def printDebug (self, *args, **kwargs):
        """Custom debug print function."""
        if (self.shouldPrintDebug):
            print(*args, **kwargs)

    def link (self, objectCodes:list):
        # Assign base addresses to each section
        self.assignSectionBaseAddresses (objectCodes)
        # Update the addresses of the symbol definitions
        self.resolveSymbolAddresses (objectCodes)
        # Fill in the final address for the symbol references
        self.applyRelocations (objectCodes)
        # Put all the code together
        finalBytecode = self.flattenCodeSections (objectCodes)
        return finalBytecode

    def assignSectionBaseAddresses (self, objectCodes, baseStart=0x0000):
        self.printDebug ("Assigning section base addresses...")
        currentBaseAddress = baseStart
        for objectCode in objectCodes:
            objectCode["baseAddress"] = currentBaseAddress
            self.printDebug (f"code for {objectCode['filename']} stored at address {objectCode['baseAddress']:x}")
            # Determine next base address
            size = len (objectCode["bytecode"])
            currentBaseAddress += size
            # Round up for alignment
            alignmentBytes = 8
            while currentBaseAddress % alignmentBytes != 0:
                currentBaseAddress += 1
    
    def resolveSymbolAddresses (self, objectCodes):
        self.printDebug ("Resolving symbol addresses...")
        for objectCode in objectCodes:
            for symbol in objectCode["symbols"]:
                objectCode["symbols"][symbol]["relAddress"] += objectCode["baseAddress"]

    # Processes the address based on relocType and returns the (little endian) bytes to patch
    def convertAddressToBytes (self, address, relocType):
        # Assuming little endian
        if relocType == 'imm16_abs_lo':
            return ((address      ) & 0xFFFF).to_bytes (2, 'little')
        elif relocType == 'imm16_abs_ml':
            return ((address >> 16) & 0xFFFF).to_bytes (2, 'little')
        elif relocType == 'imm16_abs_mh':
            return ((address >> 32) & 0xFFFF).to_bytes (2, 'little')
        elif relocType == 'imm16_abs_hi':
            return ((address >> 48) & 0xFFFF).to_bytes (2, 'little')
        elif relocType == 'addr64':
            return (address).to_bytes (8, 'little')
        # Reaches here if there is a relocType, and we dont have a rule for it
        print (f"ERROR: Unknown relocation type '{relocType}'")
        exit (1)

    def applyRelocations (self, objectCodes):
        self.printDebug ("Applying relocations...")
        for objectCode in objectCodes:
            for relocation in objectCode["relocations"]:
                # Ensure symbol exists
                if relocation["symbol"] not in objectCode["symbols"]:
                    print (f"ERROR: Unknown symbol '{relocation['symbol']}'")
                    exit (1)
                address = objectCode["symbols"][relocation["symbol"]]["relAddress"]
                relocType = relocation["type"]
                # Handle relocType
                addressBytes = self.convertAddressToBytes (address, relocType)
                patchSize = len (addressBytes)
                # Patch address in code
                offset = relocation['location']
                objectCode["bytecode"][offset:offset+patchSize] = addressBytes
                self.printDebug (f"Patched {relocation['symbol']} ({relocType}) at {offset:x} with {address:x}")

    def flattenCodeSections (self, objectCodes):
        self.printDebug ("Flattening code sections...")
        finalBytecode = bytearray ()
        for objectCode in objectCodes:
            # Ensure code is aligned to the correct address
            # This is needed bc we align base address while assigning
            while len (finalBytecode) < objectCode["baseAddress"]:
                finalBytecode.extend (bytearray ([0x00]))
            # Add this code section
            finalBytecode.extend (bytearray (objectCode["bytecode"]))
        return finalBytecode

# =================================================================================================

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="CeruleanLD Linker")
    argparser.add_argument(dest="inputFilenames", nargs="+", help="CeruleanObj files to link")
    argparser.add_argument("-o", "--outputFilename", dest="outputFilename", default="a.ceruleanbc", help="name for the outputted linked file")
    argparser.add_argument("--debug", dest="debug", action="store_true", help="enable debug output")
    args = argparser.parse_args()

    # Read in object files
    objectDataStructs = []
    for objectFilename in args.inputFilenames:
        # Ensure source file exists
        if not os.path.isfile (objectFilename):
            print (f"Error: '{objectFilename}' does not exist or is not a file")
            exit (1)
        with open (objectFilename, "r") as f:
            objectData = json.load (f)
            objectDataStructs += [objectData]

    if args.debug:
        print (objectDataStructs)

    # Link object files together
    linker = Linker (debug=args.debug)
    bytecode = linker.link (objectDataStructs)

    # Write out linked bytecode
    print (f"Writing bytecode to \"{args.outputFilename}\"")
    with open (args.outputFilename, "wb") as f:
        f.write (bytecode)
