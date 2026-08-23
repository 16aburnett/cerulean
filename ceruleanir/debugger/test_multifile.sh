#!/bin/bash
# Test script for multi-file debugger functionality

cd "$(dirname "$0")/../.." || exit

echo "=== CeruleanIR Debugger - Multi-File Testing ==="
echo

# Test 1: Load multi-file program
echo "Test 1: Load multi-file program"
echo "-----------------------------------"
echo -e "help\nquit" | python3 -m ceruleanir.debugger \
    ceruleanir/test_files/helloworld5.ceruleanir \
    ceruleanir/test_files/print_string.ceruleanir | grep -E "(CeruleanIR|Type|quit)"
echo

# Test 2: Breakpoint in main (first file)
echo "Test 2: Breakpoint in main (first file)"
echo "-----------------------------------"
echo -e "break @main\nrun\ninfo locals\nquit" | python3 -m ceruleanir.debugger \
    ceruleanir/test_files/helloworld5.ceruleanir \
    ceruleanir/test_files/print_string.ceruleanir | grep -E "(Breakpoint|Local|%)"
echo

# Test 3: Breakpoint in function from second file
echo "Test 3: Breakpoint in function from second file"
echo "-----------------------------------"
echo -e "break @println_string\nrun\nwhere\nquit" | python3 -m ceruleanir.debugger \
    ceruleanir/test_files/helloworld5.ceruleanir \
    ceruleanir/test_files/print_string.ceruleanir | grep -E "(Breakpoint|Call stack|#[0-9])"
echo

# Test 4: Step across files
echo "Test 4: Step across files"
echo "-----------------------------------"
echo -e "break @main.entry.2\nrun\nstep\nwhere\nquit" | python3 -m ceruleanir.debugger \
    ceruleanir/test_files/helloworld5.ceruleanir \
    ceruleanir/test_files/print_string.ceruleanir | grep -E "(Breakpoint|@|Call)"
echo

# Test 5: Multiple breakpoints across files with continue
echo "Test 5: Multiple breakpoints across files"
echo "-----------------------------------"
echo -e "break @main\nbreak @println_string\ninfo breakpoints\nrun\ncontinue\nquit" | python3 -m ceruleanir.debugger \
    ceruleanir/test_files/helloworld5.ceruleanir \
    ceruleanir/test_files/print_string.ceruleanir | grep -E "(Breakpoint|@)"
echo

# Test 6: Continue through execution
echo "Test 6: Continue through execution"
echo "-----------------------------------"
echo -e "break @println_string.for_body\nrun\ncontinue\ncontinue\nquit" | python3 -m ceruleanir.debugger \
    ceruleanir/test_files/helloworld5.ceruleanir \
    ceruleanir/test_files/print_string.ceruleanir | grep -E "(Breakpoint|@println|Hello)"
echo

echo "=== All multi-file debugger tests completed ==="
