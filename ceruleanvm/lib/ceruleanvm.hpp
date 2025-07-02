// CeruleanVM
//=================================================================================================

#pragma once
#include <vector>
#include <string>
#include <cstdint>
#include "memory_manager.hpp"
#include "opcode.hpp"
#include "syscall.hpp"

//=================================================================================================

class CeruleanVM {
public:
    CeruleanVM (const std::vector<uint8_t>& bytecode, bool debug_ = false);
    ~CeruleanVM ();
    void run ();
    void step ();
    bool isHalted ();
    uint64_t get_register (uint8_t index) const;
    uint64_t getPC () const;

private:
    void execute_instruction ();
    void handle_syscall (uint8_t sym_id);

    // The bytecode for the program
    std::vector<uint8_t> code;

    // Memory manager
    MemoryManager memory;
    static constexpr size_t STACK_SIZE = 64 * 1024;
    static constexpr size_t HEAP_SIZE = 1024 * 1024;

    // Registers
    // Program counter - the address of the current instruction being processed
    uint64_t pc = 0;
    // Registers are specified via 4-bits which allows for 16 unique registers
    // Registers are 64-bit and can be used to store ints, chars, floats, bools, addresses, etc
    uint64_t registers[16] = {0};
    // r0-r12  - general purpose registers (Callee Saved - saved on stack)
    // r13    0xd - return value  (ra)
    const uint8_t ra = 13;
    // r14    0xe - base pointer  (bp)
    const uint8_t bp = 14;
    // r15    0xf - stack pointer (sp)
    const uint8_t sp = 15;
    bool debug = false;
};
