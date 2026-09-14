// CeruleanRISC Virtual Machine
//=================================================================================================

#pragma once
#include <vector>
#include <string>
#include <cstdint>
#include "register_file.hpp"
#include "memory_manager.hpp"
#include "opcode.hpp"
#include "syscall.hpp"

//=================================================================================================

class CeruleanRISCVM {
public:
    CeruleanRISCVM (const std::vector<uint8_t>& bytecode, bool debug_ = false);
    ~CeruleanRISCVM ();
    void run ();
    void step ();
    bool isHalted ();
    uint64_t getRegister (uint8_t index) const;
    uint64_t getPC () const;

private:
    void execute_instruction ();
    void handle_syscall (uint16_t sym_id);

    // The bytecode for the program
    std::vector<uint8_t> code;

    // Memory manager
    MemoryManager memory;
    static constexpr size_t STACK_SIZE = 64 * 1024;
    static constexpr size_t HEAP_SIZE = 1024 * 1024;

    // Registers
    // Program counter - the address of the current instruction being processed
    uint64_t pc = 0;
    RegisterFile registers;
    // r0      0x0  - hardwired constant 0
    // r1-r28       - general purpose registers
    // r29     0x1d - return address (ra)
    const uint8_t ra = 29;
    // r30     0x1e - base pointer   (bp)
    const uint8_t bp = 30;
    // r31     0x1f - stack pointer  (sp)
    const uint8_t sp = 31;
    bool debug = false;
};
