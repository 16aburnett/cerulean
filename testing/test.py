# Cerulean Testing Framework

from enum import Enum 

class TestTarget (Enum):
    AMYASM = 0
    X86    = 1
    PYTHON = 2
    CPP    = 3
    ALL    = 4 # tests all targets

# Defines what language/compiler a test is for
class TestSource (Enum):
    Cerulean   = 0
    CeruleanIR = 1

class Test:
    def __init__(self, 
        name:str,
        code:str="",
        sourceLang:TestSource=TestSource.Cerulean,
        expectedOutput:str="",
        expectedOutputAMYASM:str=None,
        expectedOutputX86:str=None,
        expectedOutputPython:str=None,
        expectedOutputCPP:str=None,
        expectedCompilerOutput:str=None,
        shouldCompile:bool=True
    ):
        self.name = name
        self.code = code
        self.sourceLang = sourceLang
        self.expectedOutput = expectedOutput
        self.expectedOutputAMYASM = expectedOutputAMYASM if expectedOutputAMYASM != None else expectedOutput
        self.expectedOutputX86    = expectedOutputX86    if expectedOutputX86    != None else expectedOutput
        self.expectedOutputPython = expectedOutputPython if expectedOutputPython != None else expectedOutput
        self.expectedOutputCPP    = expectedOutputCPP    if expectedOutputCPP    != None else expectedOutput
        self.expectedCompilerOutput = expectedCompilerOutput
        self.shouldCompile = shouldCompile

class MultiFileTest (Test):
    def __init__(self, 
        name: str, 
        code: str = "", 
        expectedOutput: str = "", 
        expectedOutputAMYASM: str = None, 
        expectedOutputX86: str = None, 
        expectedOutputPython: str = None, 
        expectedOutputCPP:str=None,
        expectedCompilerOutput: str = None, 
        shouldCompile: bool = True
    ):
        super().__init__(name, code, expectedOutput, expectedOutputAMYASM, expectedOutputX86, expectedOutputPython, expectedOutputCPP, expectedCompilerOutput, shouldCompile)

class TestGroup:
    def __init__(self, name:str, sharedCode:str="", tests:list=[]):
        self.name = name
        self.sharedCode = sharedCode
        self.tests = tests
