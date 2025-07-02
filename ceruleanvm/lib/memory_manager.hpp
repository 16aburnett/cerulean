#pragma once
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <stdexcept>
#include <cstring>

class MemoryManager {
public:
    MemoryManager (size_t codeSize, size_t stackSize, size_t heapSize);
    ~MemoryManager ();
    // Load code into the code segment
    void loadCode (const std::vector<uint8_t>& program);
    // Allocate from the heap (bump allocator)
    uint64_t alloc (size_t size);
    // Unified memory access
    uint8_t read8(uint64_t addr) const;
    uint16_t read16(uint64_t addr) const;
    uint32_t read32(uint64_t addr) const;
    uint64_t read64(uint64_t addr) const;
    void write8(uint64_t addr, uint8_t value);
    void write16(uint64_t addr, uint16_t value);
    void write32(uint64_t addr, uint32_t value);
    void write64(uint64_t addr, uint64_t value);
    // Stack access helpers (used by VM with its own SP)
    uint64_t readStack64(uint64_t sp) const;
    void writeStack64(uint64_t sp, uint64_t value);
    // Virtual address layout
    static constexpr uint64_t CODE_BASE  = 0x00000000;
    static constexpr uint64_t HEAP_BASE  = 0x10000000;
    static constexpr uint64_t STACK_BASE = 0xFFFFFFFF;

private:
    std::vector<uint8_t> code;
    uint8_t* stackBase = nullptr;
    uint8_t* heapBase = nullptr;
    size_t stackSize = 0;
    size_t heapSize = 0;
    size_t heapOffset = 0;
    // Region checks
    bool inCode(uint64_t addr) const;
    bool inHeap(uint64_t addr) const;
    bool inStack(uint64_t addr) const;
    // Stack helpers
    size_t stackOffset(uint64_t sp) const;
    void checkStackBounds(uint64_t sp, size_t size) const;
};