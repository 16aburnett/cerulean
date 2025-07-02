#include "debugger.hpp"
#include "loader.hpp"
#include <iostream>
#include <cstring>
#include <vector>

int main (int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <bytecode_file>" << std::endl;
        return 1;
    }

    const std::string filename = argv[1];

    auto bytecode = loadBytecode (filename);
    CeruleanVM vm (bytecode, true);
    Debugger dbg (vm);
    dbg.repl ();
}