# CeruleanIR Interpreter - Command Line Entry Point
# Author: Amy Burnett
# =================================================================================================

import sys
import argparse
from pathlib import Path

from .interpreter import CeruleanIRInterpreter

# =================================================================================================

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="CeruleanIR Interpreter")
    
    argparser.add_argument("sourceFile", help="CeruleanIR source file to interpret")
    argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    
    args = argparser.parse_args()
    
    # Read source file
    source_path = Path(args.sourceFile)
    if not source_path.exists():
        print(f"ERROR: File not found: {args.sourceFile}")
        sys.exit(1)
    
    with open(source_path, "r") as f:
        source_code = f.read()
    
    # Run interpreter
    interpreter = CeruleanIRInterpreter(debug=args.debug)
    exit_code = interpreter.interpret(source_code, args.sourceFile)
    
    sys.exit(exit_code)
