# CeruleanIR REPL - CLI Entry Point
# Usage: python -m ceruleanir.repl [files...]
# =================================================================================================

import sys
from .repl import main

if __name__ == '__main__':
    # Get optional files from command line
    files = sys.argv[1:] if len(sys.argv) > 1 else None
    main(files)
