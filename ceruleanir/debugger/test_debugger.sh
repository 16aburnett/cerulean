#!/bin/bash
# Test script to demonstrate CeruleanIR debugger capabilities

cd "$(dirname "$0")/../.." || exit

echo "=== CeruleanIR Debugger Test Suite ==="
echo

# Test 1: Basic breakpoint
echo "Test 1: Basic breakpoint at @main"
echo "-----------------------------------"
echo -e "break @main\nrun\nquit" | python3 -m ceruleanir.debugger ceruleanir/test_files/helloworld.ceruleanir
echo

# Test 2: Variable inspection
echo "Test 2: Variable inspection"
echo "-----------------------------------"
echo -e "break @main.entry.2\nrun\ninfo locals\nquit" | python3 -m ceruleanir.debugger ceruleanir/test_files/helloworld.ceruleanir
echo

# Test 3: Call stack
echo "Test 3: Call stack display"
echo "-----------------------------------"
echo -e "break @print_greeting\nrun\nwhere\ninfo locals\nquit" | python3 -m ceruleanir.debugger ceruleanir/test_files/helloworld.ceruleanir
echo

# Test 4: Multiple breakpoints and restart
echo "Test 4: Multiple breakpoints and restart"
echo "-----------------------------------"
echo -e "break @main\nbreak @main.entry.2\nrun\nrun\nquit" | python3 -m ceruleanir.debugger ceruleanir/test_files/helloworld.ceruleanir
echo

# Test 5: Run without breakpoints
echo "Test 5: Run without breakpoints (full execution)"
echo "-----------------------------------"
echo -e "run\nquit" | python3 -m ceruleanir.debugger ceruleanir/test_files/helloworld.ceruleanir
echo

echo "=== All tests completed ==="