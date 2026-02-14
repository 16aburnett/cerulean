#include "test_framework.hpp"
#include "memory_manager.hpp"
#include "tee_buf.hpp"
#include "ceruleanvm.hpp"
#include <sstream>
#include <iostream>

// Tests
#include "test_helloworld1.cpp"
#include "test_helloworld2.cpp"
#include "test_helloworld3.cpp"
#include "test_helloworld4.cpp"
#include "test_loadstore.cpp"
#include "test_arithmetic.cpp"
#include "test_arithmetic_float.cpp"
#include "test_control_flow.cpp"
#include "test_conversions.cpp"

bool g_debug = false;

int main (int argc, char* argv[]) {
    std::string filter;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--debug") {
            g_debug = true;
        } else if (arg == "--list") {
            for (const auto& test : getTestRegistry ()) {
                std::cout << test.name << "\n";
            }
            return 0;
        } else {
            // Assume anything else is a test name filter
            filter = arg;
        }
    }

    runAllTests (filter);
    return 0;
}
