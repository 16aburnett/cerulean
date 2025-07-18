import os
import sys
import argparse
import json

# =================================================================================================

class Linker:
    def __init__(self):
        pass

    def link (self, objectCodes:list):
        # TODO: Implement the linker!!
        return bytearray(objectCodes[0]["bytecode"])

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

    print (objectDataStructs)

    # Link object files together
    linker = Linker ()
    bytecode = linker.link (objectDataStructs)

    # Write out linked bytecode
    print (f"Writing bytecode to \"{args.outputFilename}\"")
    with open (args.outputFilename, "wb") as f:
        f.write (bytecode)
