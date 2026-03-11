#!/usr/bin/env python3
"""
Cerulean Test Runner
Golden file testing system for the Cerulean compiler suite.
Supports multiple frontends (Cerulean, CeruleanIR) and backends (CeruleanRISC, AmyASM).

EXTENSIBILITY GUIDE:
====================

To add a new FRONTEND:
1. Add enum to Frontend class with frontend name
2. Create compile_newfrontend() function (see compile_cerulean as template)
3. Add elif branch in run_test() to call your compile function
4. Create test directory: testing/tests/newfrontend/
5. File extension will be auto-detected as .newfrontend

To add a new BACKEND:
1. Add enum to Backend class with backend name
2. Add branch in get_backend_info() for target name and extension
3. Add branch in postprocess_backend_output() for backend-specific steps (assemble, link, etc)
4. Add branch in execute_program() with execution logic
5. Tests will automatically run against the new backend
"""

import os
import sys
import json
import glob
import subprocess
import argparse
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

# ========================================================================
# Constants
# ========================================================================

TESTS_DIR = "testing/tests"
TEMP_DIR = "testing/test_tmp"

# ========================================================================
# Types
# ========================================================================

class Frontend(Enum):
    """
    Supported frontend languages.
    
    To add a new frontend:
    1. Add enum value here (e.g., NEWFRONTEND = "newfrontend")
    2. Add compilation logic in run_test() function
    3. Create test directory: testing/tests/newfrontend/
    """
    CERULEAN = "cerulean"
    CERULEANIR = "ceruleanir"
    
    @staticmethod
    def from_extension(ext: str):
        """Get frontend from file extension."""
        ext_map = {
            ".cerulean": Frontend.CERULEAN,
            ".ceruleanir": Frontend.CERULEANIR,
        }
        return ext_map.get(ext)

class Backend(Enum):
    """
    Supported backend targets.
    
    To add a new backend:
    1. Add enum value here (e.g., NEWBACKEND = "newbackend")
    2. Add branch in get_backend_info() for target name and extension
    3. Add branch in postprocess_backend_output() for backend-specific steps
    4. Add branch in execute_program() for execution logic
    """
    CERULEANRISC = "ceruleanrisc"
    AMYASM = "amyasm"
    CERULEANIR = "ceruleanir"

@dataclass
class TestConfig:
    """Configuration for a test from test.json."""
    entry: Optional[str] = None
    compile_order: Optional[List[str]] = None
    skip_backends: List[str] = None
    timeout: int = 10
    
    def __post_init__(self):
        """Initialize default values."""
        if self.skip_backends is None:
            self.skip_backends = []
    
    @staticmethod
    def load(test_dir: Path) -> 'TestConfig':
        """Load test config from test.json if it exists."""
        config_file = test_dir / "test.json"
        if not config_file.exists():
            return TestConfig()
        
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        return TestConfig(
            entry=data.get("entry"),
            compile_order=data.get("compile_order"),
            skip_backends=data.get("skip_backends", []),
            timeout=data.get("timeout", 10)
        )

@dataclass
class Test:
    """Represents a single test case (directory-based)."""
    name: str
    path: Path  # Always a directory
    frontend: Frontend
    config: TestConfig
    
    def get_source_files(self) -> List[Path]:
        """Get list of source files for this test."""
        extension = f".{self.frontend.value}"
        
        # Use compile_order if specified
        if self.config.compile_order:
            return [self.path / f for f in self.config.compile_order]
        
        # Otherwise, find all source files
        source_files = list(self.path.glob(f"*{extension}"))
        
        # Prefer main.* as entry point
        main_file = self.path / f"main{extension}"
        if main_file.exists():
            source_files.remove(main_file)
            return [main_file] + source_files
        
        return source_files
    
    def get_entry_file(self) -> Path:
        """Get the entry point file for compilation."""
        extension = f".{self.frontend.value}"
        
        # Use configured entry if specified
        if self.config.entry:
            return self.path / self.config.entry
        
        # Try main.*
        main_file = self.path / f"main{extension}"
        if main_file.exists():
            return main_file
        
        # Use first source file
        sources = self.get_source_files()
        if sources:
            return sources[0]
        
        raise ValueError(f"No source files found in {self.path}")
    
    def get_expected_output(self, backend: Optional[Backend] = None) -> str:
        """Get expected output for this test."""
        # Check for backend-specific expected file
        if backend:
            backend_expected = self.path / f"expected_stdout.{backend.value}.txt"
            if backend_expected.exists():
                return backend_expected.read_text()
        
        # Check for default expected file
        expected_file = self.path / "expected_stdout.txt"
        if expected_file.exists():
            return expected_file.read_text()
        
        raise ValueError(f"No expected output file found for test {self.name}")
    
    def get_stdin(self, backend: Optional[Backend] = None) -> Optional[str]:
        """Get stdin input for this test, if any."""
        # Check for backend-specific stdin file
        if backend:
            backend_stdin = self.path / f"stdin.{backend.value}.txt"
            if backend_stdin.exists():
                return backend_stdin.read_text()
        
        # Check for default stdin file
        stdin_file = self.path / "stdin.txt"
        if stdin_file.exists():
            return stdin_file.read_text()
        
        return None
    
    def should_skip_backend(self, backend: Backend) -> bool:
        """Check if this backend should be skipped for this test.""" 
        return backend.value in self.config.skip_backends

# ========================================================================
# Test Discovery
# ========================================================================

def discover_tests(frontend_filter: Optional[str] = None,
                  test_names: Optional[List[str]] = None) -> List[Test]:
    """Discover all tests in the tests directory."""
    tests = []
    tests_path = Path(TESTS_DIR)
    
    if not tests_path.exists():
        return tests
    
    # Determine which frontends to scan
    frontends_to_scan = [Frontend.CERULEAN, Frontend.CERULEANIR]
    if frontend_filter:
        try:
            frontends_to_scan = [Frontend(frontend_filter)]
        except ValueError:
            print(f"Warning: Unknown frontend '{frontend_filter}'")
            return tests
    
    for frontend in frontends_to_scan:
        frontend_dir = tests_path / frontend.value
        if not frontend_dir.exists():
            continue
        
        # Find all items in frontend directory
        for item in frontend_dir.iterdir():
            # Skip __pycache__ and other special directories
            if item.name.startswith('_') or item.name.startswith('.'):
                continue
            
            # Only process directories (all tests are directory-based)
            if not item.is_dir():
                continue
            
            test_name = item.name
            
            # Filter by test names if specified
            if test_names:
                # Support glob patterns
                matches = any(
                    test_name == pattern or 
                    glob.fnmatch.fnmatch(test_name, pattern)
                    for pattern in test_names
                )
                if not matches:
                    continue
            
            extension = f".{frontend.value}"
            
            # Look for source files in directory
            source_files = list(item.glob(f"*{extension}"))
            if not source_files:
                continue
            
            config = TestConfig.load(item)
            tests.append(Test(
                name=test_name,
                path=item,
                frontend=frontend,
                config=config
            ))
    
    return sorted(tests, key=lambda t: (t.frontend.value, t.name))

# ========================================================================
# Compilation & Execution
# ========================================================================

def get_backend_info(backend: Backend) -> tuple[str, str]:
    """
    Get target name and file extension for a backend.
    
    To add a new backend: add elif branch here with target name and extension.
    Returns: (target_name, file_extension)
    """
    if backend == Backend.CERULEANRISC:
        return "ceruleanrisc", ".crisc"
    elif backend == Backend.AMYASM:
        return "amyasm", ".amyasm"
    elif backend == Backend.CERULEANIR:
        return "ceruleanir", ".ceruleanir"
    else:
        raise ValueError(f"Unknown backend: {backend}")

def postprocess_backend_output(compile_output: Path, output_file: Path, 
                               backend: Backend, temp_dir: Path, 
                               timeout: int, verbose: bool) -> bool:
    """
    Post-process compilation output for specific backend (assemble, link, etc).
    
    To add a new backend: add elif branch here with backend-specific post-processing.
    Some backends may need additional steps like assembly/linking (CeruleanRISC),
    while others may just need a simple rename (AmyASM).
    """
    if backend == Backend.CERULEANRISC:
        # Assemble
        object_file = temp_dir / "output.crisco"
        cmd = [
            sys.executable, "-m", "ceruleanrisc.assembler.assembler",
            str(compile_output),
            "-o", str(object_file)
        ]
        
        if verbose:
            print(f"  Assembling: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            if verbose:
                print(f"  Assembly failed:")
                print(f"  stdout: {result.stdout}")
                print(f"  stderr: {result.stderr}")
            return False
        
        # Link
        cmd = [
            sys.executable, "-m", "ceruleanrisc.linker.linker",
            str(object_file),
            "-o", str(output_file)
        ]
        
        if verbose:
            print(f"  Linking: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            if verbose:
                print(f"  Linking failed:")
                print(f"  stdout: {result.stdout}")
                print(f"  stderr: {result.stderr}")
            return False
        
        return True
    
    elif backend == Backend.AMYASM:
        # For AmyASM, just rename to expected output file name
        if compile_output != output_file:
            shutil.move(compile_output, output_file)
        return True
    
    elif backend == Backend.CERULEANIR:
        # For CeruleanIR interpreter, no post-processing needed
        # Files are already in the right place for interpretation
        return True
    
    else:
        print(f"Error: Unknown backend {backend}")
        return False

def compile_cerulean(test: Test, backend: Backend, output_file: Path,
                    temp_dir: Path, verbose: bool = False) -> bool:
    """Compile a Cerulean source file."""
    entry_file = test.get_entry_file()
    source_files = test.get_source_files()
    
    # Get backend-specific info
    try:
        target, output_ext = get_backend_info(backend)
    except ValueError as e:
        print(f"Error: {e}")
        return False
    
    # CeruleanIR interpreter backend: compile Cerulean to CeruleanIR
    if backend == Backend.CERULEANIR:
        # Compile each Cerulean file to CeruleanIR
        for source_file in source_files:
            ir_file = temp_dir / f"{source_file.stem}.ceruleanir"
            cmd = [
                sys.executable, "-m", "cerulean.compiler",
                str(source_file),
                "--target", "ceruleanir",
                "-o", str(ir_file)
            ]
            
            if verbose:
                print(f"  Compiling to IR: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
            if result.returncode != 0:
                if verbose:
                    print(f"  Compilation to IR failed:")
                    print(f"  stdout: {result.stdout}")
                    print(f"  stderr: {result.stderr}")
                return False
        
        # For CeruleanIR interpreter, output_file is a marker file
        # The actual .ceruleanir files are in temp_dir
        output_file.write_text("ceruleanir")
        return True
    
    # CeruleanRISC backend with multiple files: compile and assemble each separately, then link
    if backend == Backend.CERULEANRISC and len(source_files) > 1:
        object_files = []
        
        # Compile and assemble each source file separately
        for i, source_file in enumerate(source_files):
            # Compile to .crisc
            crisc_file = temp_dir / f"{source_file.stem}.crisc"
            cmd = [
                sys.executable, "-m", "cerulean.compiler",
                str(source_file),
                "--target", target,
                "-o", str(crisc_file)
            ]
            
            if verbose:
                print(f"  Compiling: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
            if result.returncode != 0:
                if verbose:
                    print(f"  Compilation failed:")
                    print(f"  stdout: {result.stdout}")
                    print(f"  stderr: {result.stderr}")
                return False
            
            # Assemble to .crisco
            crisco_file = temp_dir / f"{source_file.stem}.crisco"
            cmd = [
                sys.executable, "-m", "ceruleanrisc.assembler.assembler",
                str(crisc_file),
                "-o", str(crisco_file)
            ]
            
            if verbose:
                print(f"  Assembling: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
            if result.returncode != 0:
                if verbose:
                    print(f"  Assembly failed:")
                    print(f"  stdout: {result.stdout}")
                    print(f"  stderr: {result.stderr}")
                return False
            
            object_files.append(crisco_file)
        
        # Link all object files
        cmd = [
            sys.executable, "-m", "ceruleanrisc.linker.linker"
        ]
        for obj_file in object_files:
            cmd.append(str(obj_file))
        cmd.extend(["-o", str(output_file)])
        
        if verbose:
            print(f"  Linking: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
        if result.returncode != 0:
            if verbose:
                print(f"  Linking failed:")
                print(f"  stdout: {result.stdout}")
                print(f"  stderr: {result.stderr}")
            return False
        
        return True
    
    # Single file or AmyASM backend: compile all files in one invocation
    compile_output = temp_dir / f"output{output_ext}"
    
    # Build command
    cmd = [
        sys.executable, "-m", "cerulean.compiler",
    ]
    
    # Add all source files (entry file first, then others)
    for source_file in source_files:
        cmd.append(str(source_file))
    
    # Add target and output options
    cmd.extend([
        "--target", target,
        "-o", str(compile_output)
    ])
    
    if verbose:
        print(f"  Compiling: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
    
    if result.returncode != 0:
        if verbose:
            print(f"  Compilation failed:")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
        return False
    
    # Post-process for specific backend
    return postprocess_backend_output(compile_output, output_file, backend, 
                                     temp_dir, test.config.timeout, verbose)

def compile_ceruleanir(test: Test, backend: Backend, output_file: Path,
                      temp_dir: Path, verbose: bool = False) -> bool:
    """Compile a CeruleanIR source file."""
    source_files = test.get_source_files()
    
    # Get backend-specific info
    try:
        target, output_ext = get_backend_info(backend)
    except ValueError as e:
        print(f"Error: {e}")
        return False
    
    # CeruleanIR interpreter backend: just copy CeruleanIR files to temp directory
    if backend == Backend.CERULEANIR:
        if verbose:
            print(f"  Copying CeruleanIR files for interpretation")
        
        for source_file in source_files:
            dest_file = temp_dir / source_file.name
            shutil.copy(source_file, dest_file)
        
        # For CeruleanIR interpreter, output_file is a marker file
        output_file.write_text("ceruleanir")
        return True
    
    # CeruleanIR compiler doesn't support multi-file compilation in a single invocation
    # For CeruleanRISC backend with multiple files: compile and assemble each separately, then link
    if backend == Backend.CERULEANRISC and len(source_files) > 1:
        object_files = []
        
        # Compile and assemble each source file separately
        for i, source_file in enumerate(source_files):
            # Compile to .crisc
            crisc_file = temp_dir / f"{source_file.stem}.crisc"
            cmd = [
                sys.executable, "-m", "ceruleanir.compiler",
                str(source_file),
                "--target", target,
                "-o", str(crisc_file)
            ]
            
            if verbose:
                print(f"  Compiling: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
            if result.returncode != 0:
                if verbose:
                    print(f"  Compilation failed:")
                    print(f"  stdout: {result.stdout}")
                    print(f"  stderr: {result.stderr}")
                return False
            
            # Assemble to .crisco
            crisco_file = temp_dir / f"{source_file.stem}.crisco"
            cmd = [
                sys.executable, "-m", "ceruleanrisc.assembler.assembler",
                str(crisc_file),
                "-o", str(crisco_file)
            ]
            
            if verbose:
                print(f"  Assembling: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
            if result.returncode != 0:
                if verbose:
                    print(f"  Assembly failed:")
                    print(f"  stdout: {result.stdout}")
                    print(f"  stderr: {result.stderr}")
                return False
            
            object_files.append(crisco_file)
        
        # Link all object files
        cmd = [
            sys.executable, "-m", "ceruleanrisc.linker.linker"
        ]
        for obj_file in object_files:
            cmd.append(str(obj_file))
        cmd.extend(["-o", str(output_file)])
        
        if verbose:
            print(f"  Linking: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
        if result.returncode != 0:
            if verbose:
                print(f"  Linking failed:")
                print(f"  stdout: {result.stdout}")
                print(f"  stderr: {result.stderr}")
            return False
        
        return True
    
    # Single file or AmyASM backend: compile all files in one invocation
    compile_output = temp_dir / f"output{output_ext}"
    
    cmd = [
        sys.executable, "-m", "ceruleanir.compiler",
        str(source_files[0]),  # CeruleanIR compiler only takes one file
        "--target", target,
        "-o", str(compile_output)
    ]
    
    if verbose:
        print(f"  Compiling: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=test.config.timeout)
    
    if result.returncode != 0:
        if verbose:
            print(f"  Compilation failed:")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
        return False
    
    # Post-process for specific backend
    return postprocess_backend_output(compile_output, output_file, backend, 
                                     temp_dir, test.config.timeout, verbose)

def execute_program(executable: Path, backend: Backend, timeout: int = 10,
                   stdin_input: Optional[str] = None, verbose: bool = False) -> Optional[str]:
    """Execute a compiled program and return its output."""
    
    # To add a new backend: add elif branch here with execution logic
    if backend == Backend.CERULEANRISC:
        # Find the VM binary
        vm_paths = [
            "ceruleanrisc/vm/build/criscvm",
            "ceruleanrisc/vm/build/Debug/criscvm",
            "ceruleanrisc/vm/build/Release/criscvm",
            "ceruleanrisc/vm/build/criscvm.exe",
        ]
        
        vm_binary = None
        for path in vm_paths:
            if os.path.exists(path):
                vm_binary = path
                break
        
        if not vm_binary:
            print("Error: CeruleanRISC VM not found. Please build it first:")
            print("  cd ceruleanrisc/vm && cmake -B build && cmake --build build")
            return None
        
        cmd = [vm_binary, str(executable)]
    
    elif backend == Backend.AMYASM:
        # Check if AmyAssembly interpreter exists
        amyasm_path = "../AmyAssembly/code/amyAssemblyInterpreter.py"
        if not os.path.exists(amyasm_path):
            print(f"Error: AmyAssembly interpreter not found at {amyasm_path}")
            return None
        
        cmd = [sys.executable, amyasm_path, str(executable)]
    
    elif backend == Backend.CERULEANIR:
        # For CeruleanIR interpreter, executable is a marker file
        # The actual .ceruleanir files are in the same directory
        temp_dir = executable.parent
        ceruleanir_files = sorted(temp_dir.glob("*.ceruleanir"))
        
        if not ceruleanir_files:
            print(f"Error: No .ceruleanir files found in {temp_dir}")
            return None
        
        cmd = [sys.executable, "-m", "ceruleanir.interpreter"]
        for f in ceruleanir_files:
            cmd.append(str(f))
    
    else:
        print(f"Error: Unknown backend {backend}")
        return None
    
    if verbose:
        print(f"  Executing: {' '.join(cmd)}")
        if stdin_input:
            print(f"  With stdin: {repr(stdin_input[:50])}..." if len(stdin_input) > 50 else f"  With stdin: {repr(stdin_input)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, 
                               input=stdin_input, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"  Execution timed out after {timeout}s")
        return None

# ========================================================================
# Test Execution
# ========================================================================

@dataclass
class TestResult:
    """Result of running a single test."""
    test_name: str
    frontend: str
    backend: str
    passed: bool
    error_msg: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None
    time: float = 0.0

def run_test(test: Test, backend: Backend, verbose: bool = False,
            update_expected: bool = False) -> TestResult:
    """Run a single test with a specific backend."""
    import time
    
    start_time = time.time()
    
    # Check if backend should be skipped
    if test.should_skip_backend(backend):
        return TestResult(
            test_name=test.name,
            frontend=test.frontend.value,
            backend=backend.value,
            passed=True,  # Skipped tests count as passed
            error_msg="skipped"
        )
    
    # Create temporary directory for compilation artifacts
    with tempfile.TemporaryDirectory(prefix="cerulean_test_") as temp:
        temp_dir = Path(temp)
        
        # Determine output filename
        if backend == Backend.CERULEANRISC:
            output_file = temp_dir / "output.criscbc"
        elif backend == Backend.AMYASM:
            output_file = temp_dir / "output.amyasm"
        elif backend == Backend.CERULEANIR:
            # For CeruleanIR interpreter, use a marker file
            # Actual .ceruleanir files will be in temp_dir
            output_file = temp_dir / "ceruleanir.marker"
        else:
            return TestResult(
                test_name=test.name,
                frontend=test.frontend.value,
                backend=backend.value,
                passed=False,
                error_msg=f"Unknown backend: {backend}"
            )
        
        # Compile based on frontend
        # To add a new frontend: add elif branch here with compile_newfrontend() function
        if test.frontend == Frontend.CERULEAN:
            success = compile_cerulean(test, backend, output_file, temp_dir, verbose)
        elif test.frontend == Frontend.CERULEANIR:
            success = compile_ceruleanir(test, backend, output_file, temp_dir, verbose)
        else:
            return TestResult(
                test_name=test.name,
                frontend=test.frontend.value,
                backend=backend.value,
                passed=False,
                error_msg=f"Unknown frontend: {test.frontend}"
            )
        
        if not success:
            return TestResult(
                test_name=test.name,
                frontend=test.frontend.value,
                backend=backend.value,
                passed=False,
                error_msg="Compilation failed",
                time=time.time() - start_time
            )
        
        # Execute
        stdin_input = test.get_stdin(backend)
        actual_output = execute_program(output_file, backend, 
                                       timeout=test.config.timeout, 
                                       stdin_input=stdin_input, verbose=verbose)
        
        if actual_output is None:
            return TestResult(
                test_name=test.name,
                frontend=test.frontend.value,
                backend=backend.value,
                passed=False,
                error_msg="Execution failed",
                time=time.time() - start_time
            )
        
        # Update expected output if requested
        if update_expected:
            expected_file = test.path / "expected_stdout.txt"
            expected_file.write_text(actual_output)
            print(f"Updated expected output for {test.name}")
            
            return TestResult(
                test_name=test.name,
                frontend=test.frontend.value,
                backend=backend.value,
                passed=True,
                error_msg="updated",
                time=time.time() - start_time
            )
        
        # Compare with expected output
        try:
            expected_output = test.get_expected_output(backend)
        except ValueError as e:
            return TestResult(
                test_name=test.name,
                frontend=test.frontend.value,
                backend=backend.value,
                passed=False,
                error_msg=str(e),
                time=time.time() - start_time
            )
        
        passed = actual_output == expected_output
        
        return TestResult(
            test_name=test.name,
            frontend=test.frontend.value,
            backend=backend.value,
            passed=passed,
            expected=expected_output if not passed else None,
            actual=actual_output if not passed else None,
            time=time.time() - start_time
        )

# ========================================================================
# Reporting
# ========================================================================

def print_test_result(result: TestResult, verbose: bool = False):
    """Print a test result."""
    status = "✓" if result.passed else "✗"
    time_str = f"({result.time:.2f}s)" if result.time > 0 else ""
    
    test_desc = f"{result.frontend}/{result.test_name} → {result.backend}"
    
    if result.error_msg == "skipped":
        print(f"  {test_desc} (skipped)")
    elif result.error_msg == "updated":
        print(f"  {test_desc} (updated expected output)")
    elif result.passed:
        print(f"{status} {test_desc} {time_str}")
    else:
        print(f"{status} {test_desc} {time_str}")
        
        if result.error_msg:
            print(f"  Error: {result.error_msg}")
        elif result.expected is not None and result.actual is not None:
            print(f"  Expected:")
            for line in result.expected.splitlines():
                print(f"    {repr(line)}")
            print(f"  Got:")
            for line in result.actual.splitlines():
                print(f"    {repr(line)}")

def print_summary(results: List[TestResult]):
    """Print a summary of all test results."""
    total = len([r for r in results if r.error_msg not in ("skipped", "updated")])
    passed = len([r for r in results if r.passed and r.error_msg not in ("skipped", "updated")])
    
    print()
    print("=" * 60)
    
    if passed == total:
        print(f"✓ All tests passed! ({passed}/{total})")
    else:
        failed = total - passed
        print(f"✗ {failed} test{'s' if failed != 1 else ''} failed ({passed}/{total} passed)")
    
    print("=" * 60)

# ========================================================================
# Main
# ========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Cerulean Test Runner - Golden file testing system"
    )
    
    parser.add_argument("tests", nargs="*", 
                       help="Specific tests to run (supports glob patterns)")
    parser.add_argument("--frontend", choices=[f.value for f in Frontend],
                       help="Run only tests for a specific frontend")
    parser.add_argument("--backend", choices=[b.value for b in Backend],
                       help="Run only tests for a specific backend")
    parser.add_argument("--list", action="store_true",
                       help="List all available tests")
    parser.add_argument("--update-expected", action="store_true",
                       help="Update expected output files with actual output")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed compilation and execution output")
    parser.add_argument("--fail-fast", action="store_true",
                       help="Stop on first failure")
    
    args = parser.parse_args()
    
    # Discover tests
    test_names = args.tests if args.tests else None
    tests = discover_tests(frontend_filter=args.frontend, test_names=test_names)
    
    if not tests:
        print("No tests found.")
        if test_names:
            print(f"No tests matching: {', '.join(test_names)}")
        return 1
    
    # List tests if requested
    if args.list:
        print(f"Found {len(tests)} test(s):")
        for test in tests:
            print(f"  {test.frontend.value}/{test.name}")
        return 0
    
    # Determine backends to test
    backends = []
    if args.backend:
        backends = [Backend(args.backend)]
    else:
        backends = list(Backend)  # Test all available backends
    
    # Run tests
    print(f"Running {len(tests)} test(s) with {len(backends)} backend(s)...")
    print()
    
    results = []
    
    for test in tests:
        for backend in backends:
            result = run_test(test, backend, verbose=args.verbose,
                            update_expected=args.update_expected)
            results.append(result)
            print_test_result(result, verbose=args.verbose)
            
            if args.fail_fast and not result.passed and result.error_msg != "skipped":
                print()
                print("Stopping due to --fail-fast")
                print_summary(results)
                return 1
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    failed = [r for r in results if not r.passed and r.error_msg not in ("skipped", "updated")]
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
