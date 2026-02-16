#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <functional>
#include <chrono>

#define COLOR_RESET   "\033[0m"
#define COLOR_GREEN   "\033[32m"
#define COLOR_RED     "\033[31m"
#define COLOR_YELLOW  "\033[33m"
#define COLOR_CYAN    "\033[36m"

struct TestCase {
    std::string name;
    std::function<void()> func;
};

inline std::vector<TestCase>& getTestRegistry() {
    static std::vector<TestCase> tests;
    return tests;
}

inline void registerTest(const std::string& name, std::function<void()> func) {
    getTestRegistry().push_back({name, func});
}

#define TEST_CASE(name) \
    void name(); \
    struct name##_registrar { \
        name##_registrar() { registerTest(#name, name); } \
    } name##_instance; \
    void name()

#define REQUIRE(cond) \
    do { \
        if (!(cond)) { \
            throw std::runtime_error( \
                std::string("REQUIRE failed: ") + #cond + \
                " at " + __FILE__ + ":" + std::to_string(__LINE__) \
            ); \
        } \
    } while (0)


inline void runAllTests(const std::string& filter = "") {
    int passed = 0;
    int total = 0;

    auto suiteStart = std::chrono::high_resolution_clock::now();

    for (const auto& test : getTestRegistry()) {
        if (!filter.empty() && test.name.find(filter) == std::string::npos) {
            continue;
        }

        ++total;
        std::cout << COLOR_CYAN << "[RUN ] " << COLOR_RESET << test.name << "\n";

        auto start = std::chrono::high_resolution_clock::now();

        try {
            test.func();
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();

            std::cout << COLOR_GREEN << "[ OK ] " << COLOR_RESET << test.name
                      << " (" << duration << " µs)\n";
            ++passed;
        } catch (const std::exception& e) {
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();

            std::cout << COLOR_RED << "[FAIL] " << COLOR_RESET << test.name
                      << " (" << duration << " µs)\n";
            std::cerr << "       " << e.what() << "\n";
        } catch (...) {
            std::cout << COLOR_RED << "[FAIL] " << COLOR_RESET << test.name
                      << " (unknown exception)\n";
        }
    }

    auto suiteEnd = std::chrono::high_resolution_clock::now();  // ⏱️ End total timer
    auto totalDuration = std::chrono::duration_cast<std::chrono::milliseconds>(suiteEnd - suiteStart).count();

    std::cout << "\n"
              << (passed == total ? COLOR_GREEN : COLOR_YELLOW)
              << passed << "/" << total << " tests passed."
              << COLOR_RESET << " (total time: " << totalDuration << " ms)\n";

}
