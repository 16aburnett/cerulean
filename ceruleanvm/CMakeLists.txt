cmake_minimum_required(VERSION 3.10)
project(CeruleanVM CXX)

set(CMAKE_CXX_STANDARD 17)

# Add the lib directory to the include path
include_directories(${PROJECT_SOURCE_DIR}/lib)

# Add the executable
add_executable(ceruleanvm
    src/main.cpp
    src/ceruleanvm.cpp
	src/loader.cpp
)

add_executable(emit_helloworld tools/emit_helloworld.cpp)
