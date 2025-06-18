# Cerulean Testing Framework
# ========================================================================

import os
import subprocess
import argparse
from .test import *
# Test Cases
from .testCases.cerulean.testCases import allCeruleanTests
from .testCases.ceruleanIR.testCases import allCeruleanIRTests

# ========================================================================

TEST_TEMP_DIR = "testing/test_tmp"

# ========================================================================

def runTestCeruleanIRToAmyAssembly (test, code:str, testTarget:TestTarget, level:int, groupChain:str="", shouldBreakOnFail=False):
    fullCode = code + test.code
    sourceCodeFilename = TEST_TEMP_DIR + "/test.ceruleanir"
    # NOTE: -o field to compiler does not work so this just aligns with what is automatically generated
    destCodeFilename = TEST_TEMP_DIR + "/test.ceruleanir.amyasm"

    # === Write source code to file
    with open (sourceCodeFilename, "w") as file:
        file.write (fullCode)

    # === Compiling
    compilerOutput = subprocess.run ([f'python3', '-m', 'backend.ceruleanIRCompiler', sourceCodeFilename, '--target', 'amyasm', '-o', destCodeFilename], capture_output=True, text=True)
    isCompiled = (compilerOutput.returncode == 0)

    # 1. Failed to Compile when expecting fail
    if not isCompiled and not test.shouldCompile:
        # ensure expectedCompilerOutput exists
        if test.expectedCompilerOutput not in compilerOutput.stdout:
            print (f"=== FAILED =====================")
            print (f"Test Group: {groupChain}")
            print (f"Test: {test.name}")
            print (f"Target: {TestTarget.AMYASM}")
            print ("Code:")
            print (fullCode)
            print (f"Compiled? {isCompiled}")
            print ("Expected Compiler Output:")
            print (test.expectedCompilerOutput)
            print ("Actual Compiler Output:")
            print (compilerOutput.stdout)
            print (f"--- STDERR ---------------------")
            print (compilerOutput.stderr)
            print (f"--------------------------------")
            print (f"================================")
            return False
        return True
    
    # 2. Failed to Compile when expecting success
    elif not isCompiled and test.shouldCompile:
        print (f"=== FAILED =====================")
        print (f"Test Group: {groupChain}")
        print (f"Test: {test.name}")
        print (f"Target: {TestTarget.AMYASM}")
        print ("Code:")
        print (fullCode)
        print (f"Compiled? {isCompiled}")
        print ("Compiler Output:")
        print (compilerOutput.stdout)
        print (f"--- STDERR ---------------------")
        print (compilerOutput.stderr)
        print (f"--------------------------------")
        print (f"================================")
        return False
    
    # 3. Compiles when expecting fail
    elif isCompiled and not test.shouldCompile:
        print (f"=== FAILED =====================")
        print (f"Reason: Should have failed to compile")
        print (f"Test Group: {groupChain}")
        print (f"Test: {test.name}")
        print (f"Target: {TestTarget.AMYASM}")
        print ("Code:")
        print (fullCode)
        print (f"Compiled? {isCompiled}")
        print ("Expected Compiler Output:")
        print (test.expectedCompilerOutput)
        print ("Compiler Output:")
        print (compilerOutput.stdout)
        print (f"================================")
        return False

    # 4. Compiles when expecting success
    # === Running compiled program
    result = subprocess.run (['python3', '../AmyAssembly/code/amyAssemblyInterpreter.py', destCodeFilename], capture_output=True, text=True)
    # ensure it was successful
    wasTestSuccessful = result.stdout == test.expectedOutputAMYASM
    if not wasTestSuccessful:
        print (f"=== FAILED =====================")
        print (f"Test Group: {groupChain}")
        print (f"Test: {test.name}")
        print (f"Target: {TestTarget.AMYASM}")
        print ("Code:")
        print (fullCode)
        print (f"Compiled? {isCompiled}")
        print ("Expected Output:")
        print (test.expectedOutputAMYASM)
        print ("Actual Output:")
        print (result.stdout)
        print (f"================================")
        return False
    return True

# ========================================================================

def runTestCeruleanToAmyAssembly (test, code:str, testTarget:TestTarget, level:int, groupChain:str="", shouldBreakOnFail=False):
    fullCode = code + test.code
    sourceCodeFilename = TEST_TEMP_DIR + "/test.cerulean"
    irCodeFilename = TEST_TEMP_DIR + "/test.cerulean.ir"
    # NOTE: -o field to compiler does not work so this just aligns with what is automatically generated
    destCodeFilename = TEST_TEMP_DIR + "/test.cerulean.ir.amyasm"

    # === Write source code to file
    with open (sourceCodeFilename, "w") as file:
        file.write (fullCode)

    # === Compiling
    compilerOutput = subprocess.run ([f'python3', '-m', 'cerulean.ceruleanCompiler', sourceCodeFilename, '--target', 'amyasm', '-o', destCodeFilename, '--emitIR'], capture_output=True, text=True)
    isCompiled = (compilerOutput.returncode == 0)

    # 1. Failed to Compile when expecting fail
    if not isCompiled and not test.shouldCompile:
        # ensure expectedCompilerOutput exists
        if test.expectedCompilerOutput not in compilerOutput.stdout:
            print (f"=== FAILED =====================")
            print (f"Test Group: {groupChain}")
            print (f"Test: {test.name}")
            print (f"Target: {TestTarget.AMYASM}")
            print ("Code:")
            print (fullCode)
            print (f"Compiled? {isCompiled}")
            print ("Expected Compiler Output:")
            print (test.expectedCompilerOutput)
            print ("Actual Compiler Output:")
            print (compilerOutput.stdout)
            print (f"--- STDERR ---------------------")
            print (compilerOutput.stderr)
            print (f"--------------------------------")
            print (f"================================")
            return False
        return True
    
    # 2. Failed to Compile when expecting success
    elif not isCompiled and test.shouldCompile:
        print (f"=== FAILED =====================")
        print (f"Test Group: {groupChain}")
        print (f"Test: {test.name}")
        print (f"Target: {TestTarget.AMYASM}")
        print ("Code:")
        print (fullCode)
        print (f"Compiled? {isCompiled}")
        print ("Compiler Output:")
        print (compilerOutput.stdout)
        print (f"--- STDERR ---------------------")
        print (compilerOutput.stderr)
        print (f"--------------------------------")
        print (f"================================")
        return False
    
    # 3. Compiles when expecting fail
    elif isCompiled and not test.shouldCompile:
        print (f"=== FAILED =====================")
        print (f"Reason: Should have failed to compile")
        print (f"Test Group: {groupChain}")
        print (f"Test: {test.name}")
        print (f"Target: {TestTarget.AMYASM}")
        print ("Code:")
        print (fullCode)
        print (f"Compiled? {isCompiled}")
        print ("Expected Compiler Output:")
        print (test.expectedCompilerOutput)
        print ("Compiler Output:")
        print (compilerOutput.stdout)
        print (f"================================")
        return False

    # 4. Compiles when expecting success

    # === Compile IR to target (NOTE this is not the intended path)
    compilerOutput = subprocess.run ([f'python3', '-m', 'backend.ceruleanIRCompiler', irCodeFilename, '--target', 'amyasm', '-o', destCodeFilename], capture_output=True, text=True)
    isCompiled = (compilerOutput.returncode == 0)
    if not isCompiled:
        print (f"FAILED to compile IR->Target")
        return False

    # === Running compiled program
    # run the code
    result = subprocess.run (['python3', '../AmyAssembly/code/amyAssemblyInterpreter.py', destCodeFilename], capture_output=True, text=True)
    # ensure it was successful
    wasTestSuccessful = result.stdout == test.expectedOutputAMYASM
    if not wasTestSuccessful:
        print (f"=== FAILED =====================")
        print (f"Test Group: {groupChain}")
        print (f"Test: {test.name}")
        print (f"Target: {TestTarget.AMYASM}")
        print ("Code:")
        print (fullCode)
        print (f"Compiled? {isCompiled}")
        print ("Expected Output:")
        print (test.expectedOutputAMYASM)
        print ("Actual Output:")
        print (result.stdout)
        print (f"================================")
        return False
    return True

# ========================================================================

def runTest (test, code:str, testTarget:TestTarget, level:int, groupChain:str="", shouldBreakOnFail=False):
    fullCode = code + test.code
    numTests = 0
    numSuccessfulTests = 0
    if testTarget == TestTarget.AMYASM or testTarget == TestTarget.ALL:
        if test.sourceLang == TestSource.Cerulean:
            wasSuccessful = runTestCeruleanToAmyAssembly (test, code, testTarget, level, groupChain, shouldBreakOnFail)
        else: # test.sourceLang == TestSource.CeruleanIR
            wasSuccessful = runTestCeruleanIRToAmyAssembly (test, code, testTarget, level, groupChain, shouldBreakOnFail)
        if wasSuccessful: numSuccessfulTests += 1
        numTests += 1

    for i in range(level):
        print ('| ', end='')
    print ('> ', end='')
    print (f"{test.name} {numSuccessfulTests} / {numTests} passed")

    if numSuccessfulTests != numTests and shouldBreakOnFail:
        print ("Error: Exiting due to failed test")
        exit (1)

    return [numSuccessfulTests, numTests]

# ========================================================================

def runTestGroupHelper (test, code:str, testTarget:TestTarget, level:int, groupChain:str="", shouldBreakOnFail=False):
    if isinstance(test, TestGroup):
        for i in range(level):
            print ('| ', end='')
        print ('v ', end='')
        print (test.name)

        numSuccessful = 0
        numTests = 0
        for subtest in test.tests:
            [numSuccessfulSubtests, numSubtests] = runTestGroupHelper (subtest, code + test.sharedCode, testTarget, level+1, f"{groupChain} > {test.name}", shouldBreakOnFail=shouldBreakOnFail)
            numSuccessful += numSuccessfulSubtests
            numTests += numSubtests

        for i in range(level):
            print ('| ', end='')
        print ('^ ', end='')
        print (test.name, numSuccessful, '/', numTests, "passed")

        return [numSuccessful, numTests]

    elif isinstance(test, Test):
        return runTest (test, code, testTarget, level, groupChain, shouldBreakOnFail=False)

# ========================================================================

def runTestGroup (test, testTarget:TestTarget.AMYASM, shouldBreakOnFail=False):
    return runTestGroupHelper (test, "", testTarget, 0, shouldBreakOnFail=shouldBreakOnFail)

# ========================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cerulean Testing Suite")
    parser.add_argument("--frontend", type=lambda s: s.lower(), choices=["all", "cerulean", "ceruleanir"], required=True, help="Specify which frontend's tests to run")
    args = parser.parse_args()
    
    tests = TestGroup ("Tests", "", [])
    if args.frontend == "all" or args.frontend == "cerulean":
        tests.tests += [allCeruleanTests]
    if args.frontend == "all" or args.frontend == "ceruleanir":
        tests.tests += [allCeruleanIRTests]

    [numSuccessful, numTests] = runTestGroup (tests, TestTarget.AMYASM)

    if numSuccessful == numTests:
        print (f"SUCCESS: All tests passed")
    else:
        numFailed = numTests - numSuccessful
        print (f"FAILED: {numFailed} test{'s' if numFailed > 1 else ''} failed")
