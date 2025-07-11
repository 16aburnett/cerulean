cmake_minimum_required(VERSION 3.10)
project(CeruleanVM CXX)

set(CMAKE_CXX_STANDARD 20)

# Add the lib directory to the include path
include_directories(${PROJECT_SOURCE_DIR}/lib)

# CeruleanVM
add_executable(ceruleanvm
    src/main.cpp
    src/ceruleanvm.cpp
	src/loader.cpp
	src/memory_manager.cpp
)

# Debugger
add_executable(ceruleandbg
    tools/ceruleanvm_dbg.cpp
    src/debugger.cpp
	src/ceruleanvm.cpp
	src/loader.cpp
	src/memory_manager.cpp
)

# Testing
option(BUILD_TESTS "Build unit tests" OFF)
if(BUILD_TESTS)
    add_executable(run_tests
		tests/main.cpp
		src/ceruleanvm.cpp
		src/memory_manager.cpp
	)
endif()

# Tooling
add_executable(emit_helloworld tools/emit_helloworld.cpp)
