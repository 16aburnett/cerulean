#include "memory_manager.hpp"
#include <cstdint>
#include <cstdlib>
#include <vector>
#include <stdexcept>
#include <cstring>

MemoryManager::MemoryManager(size_t codeSize, size_t stackSize, size_t heapSize)
    : code(codeSize), stackSize(stackSize), heapSize(heapSize) {
    // Allocate stack (grows down)
    stackBase = static_cast<uint8_t*>(std::malloc(stackSize));
    if (!stackBase) throw std::bad_alloc();

    // Allocate heap (flat buffer)
    heapBase = static_cast<uint8_t*>(std::malloc(heapSize));
    if (!heapBase) throw std::bad_alloc();
}

MemoryManager::~MemoryManager() {
    std::free(stackBase);
    std::free(heapBase);
}

// Load code into the code segment
void MemoryManager::loadCode(const std::vector<uint8_t>& program) {
    if (program.size() > code.size()) {
        throw std::runtime_error("Program too large for code segment");
    }
    std::copy(program.begin(), program.end(), code.begin());
}

// Allocate from the heap (bump allocator)
uint64_t MemoryManager::alloc(size_t size) {
    if (heapOffset + size > heapSize) throw std::bad_alloc();
    uint64_t vaddr = HEAP_BASE + heapOffset;
    heapOffset += size;
    return vaddr;
}

// Unified memory access
uint8_t MemoryManager::read8(uint64_t addr) const {
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

uint16_t MemoryManager::read16(uint64_t addr) const {
    return static_cast<uint16_t>(read8(addr)) |
        (static_cast<uint16_t>(read8(addr + 1)) << 8);
}

uint32_t MemoryManager::read32(uint64_t addr) const {
    return static_cast<uint32_t>(read8(addr)) |
        (static_cast<uint32_t>(read8(addr + 1)) << 8) |
        (static_cast<uint32_t>(read8(addr + 2)) << 16) |
        (static_cast<uint32_t>(read8(addr + 3)) << 24);
}

uint64_t MemoryManager::read64(uint64_t addr) const {
    uint64_t result = 0;
    for (int i = 0; i < 8; ++i) {
        result |= static_cast<uint64_t>(read8(addr + i)) << (i * 8);
    }
    return result;
}

void MemoryManager::write8(uint64_t addr, uint8_t value) {
    if (inHeap(addr)) {
        heapBase[addr - HEAP_BASE] = value;
    } else if (inStack(addr)) {
        stackBase[STACK_BASE - addr] = value;
    } else {
        throw std::runtime_error("Invalid memory write (read-only or unmapped)");
    }
}

void MemoryManager::write16(uint64_t addr, uint16_t value) {
    write8(addr,     static_cast<uint8_t>(value & 0xFF));
    write8(addr + 1, static_cast<uint8_t>((value >> 8) & 0xFF));
}

void MemoryManager::write32(uint64_t addr, uint32_t value) {
    for (int i = 0; i < 4; ++i) {
        write8(addr + i, static_cast<uint8_t>((value >> (i * 8)) & 0xFF));
    }
}

void MemoryManager::write64(uint64_t addr, uint64_t value) {
    for (int i = 0; i < 8; ++i) {
        write8(addr + i, static_cast<uint8_t>((value >> (i * 8)) & 0xFF));
    }
}

// Stack access helpers (used by VM with its own SP)
uint64_t MemoryManager::readStack64(uint64_t sp) const {
    checkStackBounds(sp, sizeof(uint64_t));
    return *reinterpret_cast<uint64_t*>(stackBase + stackOffset(sp));
}

void MemoryManager::writeStack64(uint64_t sp, uint64_t value) {
    checkStackBounds(sp, sizeof(uint64_t));
    *reinterpret_cast<uint64_t*>(stackBase + stackOffset(sp)) = value;
}

// Private
// Region checks
bool MemoryManager::inCode(uint64_t addr) const {
    return addr >= CODE_BASE && addr < CODE_BASE + code.size();
}

bool MemoryManager::inHeap(uint64_t addr) const {
    return addr >= HEAP_BASE && addr < HEAP_BASE + heapSize;
}

bool MemoryManager::inStack(uint64_t addr) const {
    return addr >= STACK_BASE - stackSize && addr <= STACK_BASE;
}

// Stack helpers
size_t MemoryManager::stackOffset(uint64_t sp) const {
    return STACK_BASE - sp;
}

void MemoryManager::checkStackBounds(uint64_t sp, size_t size) const {
    if (sp < STACK_BASE - stackSize + size || sp > STACK_BASE) {
        throw std::runtime_error("Stack access out of bounds");
    }
}