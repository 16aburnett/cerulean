#pragma once
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <stdexcept>
#include <cstring>

class MemoryManager {
public:
    // Virtual address layout
    static constexpr uint64_t CODE_BASE  = 0x00000000;
    static constexpr uint64_t HEAP_BASE  = 0x10000000;
    static constexpr uint64_t STACK_BASE = 0xFFFFFFFF;

    MemoryManager(size_t codeSize, size_t stackSize, size_t heapSize)
        : code(codeSize), stackSize(stackSize), heapSize(heapSize) {
        // Allocate stack (grows down)
        stackBase = static_cast<uint8_t*>(std::malloc(stackSize));
        if (!stackBase) throw std::bad_alloc();

        // Allocate heap (flat buffer)
        heapBase = static_cast<uint8_t*>(std::malloc(heapSize));
        if (!heapBase) throw std::bad_alloc();
    }

    ~MemoryManager() {
        std::free(stackBase);
        std::free(heapBase);
    }

    // Load code into the code segment
    void loadCode(const std::vector<uint8_t>& program) {
        if (program.size() > code.size()) {
            throw std::runtime_error("Program too large for code segment");
        }
        std::copy(program.begin(), program.end(), code.begin());
    }

    // Allocate from the heap (bump allocator)
    uint64_t alloc(size_t size) {
        if (heapOffset + size > heapSize) throw std::bad_alloc();
        uint64_t vaddr = HEAP_BASE + heapOffset;
        heapOffset += size;
        return vaddr;
    }

    // Unified memory access
    uint8_t read8(uint64_t addr) const {
        if (inCode(addr)) {
            return code.at(addr - CODE_BASE);
        } else if (inHeap(addr)) {
            return heapBase[addr - HEAP_BASE];
        } else if (inStack(addr)) {
            return stackBase[STACK_BASE - addr];
        } else {
            throw std::runtime_error("Invalid memory read");
        }
    }

    uint16_t read16(uint64_t addr) const {
        return static_cast<uint16_t>(read8(addr)) |
            (static_cast<uint16_t>(read8(addr + 1)) << 8);
    }

    uint32_t read32(uint64_t addr) const {
        return static_cast<uint32_t>(read8(addr)) |
            (static_cast<uint32_t>(read8(addr + 1)) << 8) |
            (static_cast<uint32_t>(read8(addr + 2)) << 16) |
            (static_cast<uint32_t>(read8(addr + 3)) << 24);
    }

    uint64_t read64(uint64_t addr) const {
        uint64_t result = 0;
        for (int i = 0; i < 8; ++i) {
            result |= static_cast<uint64_t>(read8(addr + i)) << (i * 8);
        }
        return result;
    }

    void write8(uint64_t addr, uint8_t value) {
        if (inHeap(addr)) {
            heapBase[addr - HEAP_BASE] = value;
        } else if (inStack(addr)) {
            stackBase[STACK_BASE - addr] = value;
        } else {
            throw std::runtime_error("Invalid memory write (read-only or unmapped)");
        }
    }

    void write16(uint64_t addr, uint16_t value) {
        write8(addr,     static_cast<uint8_t>(value & 0xFF));
        write8(addr + 1, static_cast<uint8_t>((value >> 8) & 0xFF));
    }

    void write32(uint64_t addr, uint32_t value) {
        for (int i = 0; i < 4; ++i) {
            write8(addr + i, static_cast<uint8_t>((value >> (i * 8)) & 0xFF));
        }
    }

    void write64(uint64_t addr, uint64_t value) {
        for (int i = 0; i < 8; ++i) {
            write8(addr + i, static_cast<uint8_t>((value >> (i * 8)) & 0xFF));
        }
    }

    // Stack access helpers (used by VM with its own SP)
    uint64_t readStack64(uint64_t sp) const {
        checkStackBounds(sp, sizeof(uint64_t));
        return *reinterpret_cast<uint64_t*>(stackBase + stackOffset(sp));
    }

    void writeStack64(uint64_t sp, uint64_t value) {
        checkStackBounds(sp, sizeof(uint64_t));
        *reinterpret_cast<uint64_t*>(stackBase + stackOffset(sp)) = value;
    }

private:
    std::vector<uint8_t> code;
    uint8_t* stackBase = nullptr;
    uint8_t* heapBase = nullptr;
    size_t stackSize = 0;
    size_t heapSize = 0;
    size_t heapOffset = 0;

    // Region checks
    bool inCode(uint64_t addr) const {
        return addr >= CODE_BASE && addr < CODE_BASE + code.size();
    }

    bool inHeap(uint64_t addr) const {
        return addr >= HEAP_BASE && addr < HEAP_BASE + heapSize;
    }

    bool inStack(uint64_t addr) const {
        return addr >= STACK_BASE - stackSize && addr <= STACK_BASE;
    }

    // Stack helpers
    size_t stackOffset(uint64_t sp) const {
        return STACK_BASE - sp;
    }

    void checkStackBounds(uint64_t sp, size_t size) const {
        if (sp < STACK_BASE - stackSize + size || sp > STACK_BASE) {
            throw std::runtime_error("Stack access out of bounds");
        }
    }
};