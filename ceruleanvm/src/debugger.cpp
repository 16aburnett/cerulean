#include "debugger.hpp"
#include <iostream>
#include <sstream>
#include <set>

std::string toHex (uint64_t value) {
    std::ostringstream oss;
    // Need to handle 0 separately since showbase does not work with 0
    if (value == 0) {
        oss << "0x0";
    } else {
        oss << std::showbase << std::hex << value;
    }
    return oss.str();
}


Debugger::Debugger (CeruleanVM& vm) : vm (vm) {}

void Debugger::repl () {
    std::string line;
    while (true) {
        std::cout << "(dbg) ";
        if (!std::getline (std::cin, line)) break;
        handleCommand (line);
    }
}

void Debugger::handleCommand (const std::string& line) {
    std::istringstream iss (line);
    std::string cmd, arg;
    iss >> cmd >> arg;

    if      (cmd == "s" || cmd == "step"    ) cmdStep ();
    else if (cmd == "c" || cmd == "continue") cmdContinue ();
    else if (cmd == "b" || cmd == "break"   ) cmdBreak (arg);
    else if (cmd == "d" || cmd == "delete"  ) cmdDelete (arg);
    else if (cmd == "l" || cmd == "list"    ) cmdList ();
    else if (cmd == "p" || cmd == "print"   ) cmdPrint (arg);
    else if (cmd == "h" || cmd == "help"    ) cmdHelp ();
    else if (cmd == "q" || cmd == "quit"    ) cmdQuit ();
    else if (cmd == "") ; // ignore empty commands
    else std::cout << "Unknown command. Type 'help'.\n";
}

void Debugger::cmdStep () {
    // Ensure program has more code to run
    if (vm.isHalted ()) {
        std::cout << "Program finished - cannot step" << std::endl;
        return;
    }
    vm.step ();
    // Check if program completed
    if (vm.isHalted ()) {
        std::cout << "Program finished" << std::endl;
        return;
    }
}

void Debugger::cmdContinue () {
    // Ensure program has more code to run
    if (vm.isHalted ()) {
        std::cout << "Program finished - cannot continue" << std::endl;
        return;
    }
    while (!vm.isHalted ()) {
        vm.step ();
        if (hasBreakpoint (vm.getPC ()))
        {
            std::cout << "Breakpoint reached at " << toHex (vm.getPC ()) << std::endl;
            break;
        }
    }
    // Check if program completed
    if (vm.isHalted ()) {
        std::cout << "Program finished" << std::endl;
        return;
    }
}

void Debugger::cmdBreak (const std::string& arg) {
    try {
        uint64_t addr = std::stoul (arg, nullptr, 0);
        // Ensure breakpoint doesnt already exist
        if (breakpoints.find (addr) != breakpoints.end ()) {
            std::cout << "Breakpoint was already set at address: " << toHex (addr) << std::endl;
            return;
        }
        std::cout << "Setting breakpoint at address: " << toHex (addr) << std::endl;
        breakpoints.insert (addr);
    } catch (const std::exception& e) {
        std::cerr << "Invalid argument to break: " << arg << std::endl;
    }
}

void Debugger::cmdDelete (const std::string& arg) {
    try {
        uint64_t addr = std::stoul (arg, nullptr, 0);
        // Ensure breakpoint exists
        if (breakpoints.find (addr) == breakpoints.end ()) {
            std::cout << "No breakpoint at address: " << toHex (addr) << std::endl;
            return;
        }
        std::cout << "Removing breakpoint from address: " << toHex (addr) << std::endl;
        breakpoints.erase (addr);
    } catch (const std::exception& e) {
        std::cerr << "Invalid argument to delete: " << arg << std::endl;
    }
}

void Debugger::cmdList () {
    std::cout << "Breakpoints:" << std::endl;
    std::set<uint64_t> sortedBreakpoints (breakpoints.begin (), breakpoints.end ());
    for (const auto& breakpoint : sortedBreakpoints) {
        std::cout << toHex (breakpoint) << std::endl;
    }
}

void Debugger::cmdPrint (const std::string& arg) {
    uint64_t value = 0;
    if      (arg == "r0") value = vm.getRegister (0);
    else if (arg == "r1") value = vm.getRegister (1);
    else if (arg == "r2") value = vm.getRegister (2);
    else if (arg == "r3") value = vm.getRegister (3);
    else if (arg == "r4") value = vm.getRegister (4);
    else if (arg == "r5") value = vm.getRegister (5);
    else if (arg == "r6") value = vm.getRegister (6);
    else if (arg == "r7") value = vm.getRegister (7);
    else if (arg == "r8") value = vm.getRegister (8);
    else if (arg == "r9") value = vm.getRegister (9);
    else if (arg == "r10") value = vm.getRegister (10);
    else if (arg == "r11") value = vm.getRegister (11);
    else if (arg == "r12") value = vm.getRegister (12);
    else if (arg == "r13" || arg == "ra") value = vm.getRegister (13);
    else if (arg == "r14" || arg == "bp") value = vm.getRegister (14);
    else if (arg == "r15" || arg == "sp") value = vm.getRegister (15);
    else {
        std::cout << "Unknown register. Type 'help'.\n";
        return;
    }
    std::cout << value << std::endl;
}

void Debugger::cmdHelp () {
    std::cout << "s, step           execute current instruction" << std::endl;
    std::cout << "c, continue       resume running program (stopping at any breakpoints)" << std::endl;
    std::cout << "b, break <addr>   sets a breakpoint at the given address to pause execution" << std::endl;
    std::cout << "d, delete <addr>  deletes the breakpoint at the given address" << std::endl;
    std::cout << "l, list           lists all of the current breakpoints" << std::endl;
    std::cout << "p, print <reg>    prints the value stored in the give register" << std::endl;
    std::cout << "h, help           prints this message" << std::endl;
    std::cout << "q, quit           exit debugger" << std::endl;
}

void Debugger::cmdQuit () {
    std::cout << "Quit" << std::endl;
    exit (0);
}

bool Debugger::hasBreakpoint (uint64_t addr) {
    return breakpoints.find (addr) != breakpoints.end ();
}
