#pragma once
#include "ceruleanvm.hpp"
#include <unordered_set>
#include <string>

class Debugger {
public:
    Debugger (CeruleanVM& vm);
    void repl ();

private:
    CeruleanVM& vm;
    std::unordered_set<uint64_t> breakpoints;

    void handleCommand (const std::string& line);
    void cmdStep ();
    void cmdContinue ();
    void cmdBreak (const std::string& arg);
    void cmdDelete (const std::string& arg);
    void cmdList ();
    void cmdPrint (const std::string& arg);
    void cmdHelp ();
    void cmdQuit ();

    bool hasBreakpoint (uint64_t addr);
};