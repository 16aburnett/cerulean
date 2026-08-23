# CeruleanIR Debugger - Main Entry Point
# Usage: python -m ceruleanir.debugger <files...>
# Author: Amy Burnett
# =================================================================================================

import sys
import argparse
from .debugger import CeruleanIRDebugger

def main():
    parser = argparse.ArgumentParser(
        description='CeruleanIR Interactive Debugger',
        epilog='Example: python -m ceruleanir.debugger program.ceruleanir'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='CeruleanIR source files to debug'
    )
    parser.add_argument(
        '-x', '--command-file',
        dest='command_file',
        help='Execute commands from file before starting interactive mode'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug output for the debugger itself'
    )
    
    args = parser.parse_args()
    
    # Create debugger
    debugger = CeruleanIRDebugger(debug=args.debug)
    
    # Load program
    try:
        for file in args.files:
            debugger.load_file(file)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR loading files: {e}")
        sys.exit(1)
    
    # Execute command file if provided
    if args.command_file:
        try:
            debugger.execute_command_file(args.command_file)
        except Exception as e:
            print(f"ERROR executing command file: {e}")
            sys.exit(1)
    
    # Start interactive debugger
    debugger.repl()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
