cmake_minimum_required(VERSION 3.10)
project(CeruleanVM CXX)

set(CMAKE_CXX_STANDARD 17)

# Add the lib directory to the include path
include_directories(${PROJECT_SOURCE_DIR}/lib)

# CeruleanVM
add_executable(ceruleanvm
    src/main.cpp
    src/ceruleanvm.cpp
	src/loader.cpp
)

# Testing
add_executable(test_helloworld tests/test_helloworld.cpp src/ceruleanvm.cpp)
add_executable(test_helloworld2 tests/test_helloworld2.cpp src/ceruleanvm.cpp)
add_executable(test_helloworld3 tests/test_helloworld3.cpp src/ceruleanvm.cpp)

# Tooling
add_executable(emit_helloworld tools/emit_helloworld.cpp)
