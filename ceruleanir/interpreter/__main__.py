# CeruleanIR Interpreter - Command Line Entry Point
# Author: Amy Burnett
# =================================================================================================

import sys
import argparse
from pathlib import Path

from .interpreter import CeruleanIRInterpreter

# =================================================================================================

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="CeruleanIR Interpreter - Execute CeruleanIR programs directly from the command line"
    )
    
    argparser.add_argument(
        "sourceFiles",
        nargs='+',
        help="CeruleanIR source file(s) to interpret"
    )
    argparser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = argparser.parse_args()
    
    # Create interpreter
    interpreter = CeruleanIRInterpreter(debug=args.debug)
    
    # Load all source files
    for source_file in args.sourceFiles:
        source_path = Path(source_file)
        if not source_path.exists():
            print(f"ERROR: File not found: {source_file}")
            sys.exit(1)
        
        interpreter.load_file(source_file)
    
    # Execute linked program
    exit_code = interpreter.run()
    
    # Propagate exit code to the shell
    sys.exit(exit_code)
