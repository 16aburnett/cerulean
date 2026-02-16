#include <cstdint>
#include <bit>
#include <cstddef>

// We are limited to 4-bits for identifying registers so we can only have 16 registers
constexpr size_t numRegisters = 16;
constexpr size_t registerSize = sizeof(uint64_t);

// Performance notes
// - All methods are inlined so the compiler should optimize away the overhead of this class
// - Each access should compile to a single load/store
// - The register array is aligned by the regSize to ensure lookups of different types have the
// correct alignment to avoid crashes and performance issues with some systems.
// - The registers are stored as a byte array to allow for read/write without masking, and
// to allow accessing separate bytes of a register for vectorization or lane access.

class RegisterFile {
public:
    // Generic getters/setters
    template<typename T>
    inline T get (size_t index) const {
        static_assert(std::is_trivially_copyable_v<T>, "T must be trivially copyable");
        static_assert(alignof(T) <= alignof(std::max_align_t), "T must be safely aligned");
        return *reinterpret_cast<const T*>(data + index * registerSize);
    }

    template<typename T>
    inline void set (size_t index, T value) {
        static_assert(std::is_trivially_copyable_v<T>, "T must be trivially copyable");
        static_assert(alignof(T) <= alignof(std::max_align_t), "T must be safely aligned");
        *reinterpret_cast<T*>(data + index * registerSize) = value;
    }

    // 32-bit low half
    inline uint32_t getLo32(size_t index) const {
        return *reinterpret_cast<const uint32_t*>(&data[index * registerSize]);
    }

    inline void setLo32(size_t index, uint32_t value) {
        *reinterpret_cast<uint32_t*>(&data[index * registerSize]) = value;
    }

    // 32-bit high half
    inline uint32_t getHi32(size_t index) const {
        return *reinterpret_cast<const uint32_t*>(&data[index * registerSize + 4]);
    }

    inline void setHi32(size_t index, uint32_t value) {
        *reinterpret_cast<uint32_t*>(&data[index * registerSize + 4]) = value;
    }

private:
    // NOTE: Needs to be aligned to the registerSize to avoid issues
    // Also, zero-initialized
    alignas(uint64_t) uint8_t data[numRegisters * registerSize]{};
};
