cmake_minimum_required(VERSION 3.10)
project(CeruleanRISC_VM CXX)

set(CMAKE_CXX_STANDARD 20)

# Add the lib directory to the include path
include_directories(${PROJECT_SOURCE_DIR}/lib)

# CeruleanRISC VM
add_executable(criscvm
    src/main.cpp
    src/criscvm.cpp
	src/loader.cpp
	src/memory_manager.cpp
	src/instruction_registry.cpp
	src/disassembler.cpp
)

# CeruleanRISC Debugger
add_executable(criscdbg
    tools/criscdbg.cpp
    src/debugger.cpp
	src/criscvm.cpp
	src/loader.cpp
	src/memory_manager.cpp
	src/instruction_registry.cpp
	src/disassembler.cpp
)

# Testing
option(BUILD_TESTS "Build unit tests" OFF)
if(BUILD_TESTS)
    add_executable(run_tests
		tests/main.cpp
		src/criscvm.cpp
		src/memory_manager.cpp
		src/instruction_registry.cpp
		src/disassembler.cpp
	)
endif()

# Tooling
add_executable(emit_helloworld tools/emit_helloworld.cpp)
