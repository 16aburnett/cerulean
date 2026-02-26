# Cerulean Testing System

A golden file testing system for the Cerulean compiler suite that supports multiple frontends and backends.

## Quick Start

Run all tests:
```bash
python testing/run_tests.py
```

Run a specific test:
```bash
python testing/run_tests.py helloworld
```

Run tests for a specific frontend:
```bash
python testing/run_tests.py --frontend cerulean
```

Run tests for a specific backend:
```bash
python testing/run_tests.py --backend ceruleanrisc
```

## Test Structure

All tests are directory-based. Each test is a directory containing source files and expected output:

```
testing/tests/cerulean/
└── helloworld/
    ├── main.cerulean        # Source code
    └── expected_stdout.txt  # Expected stdout
```

For tests with multiple source files:

```
testing/tests/cerulean/
└── multi_file_example/
    ├── main.cerulean        # Entry point
    ├── math.cerulean        # Additional file
    ├── expected_stdout.txt  # Expected stdout
    └── test.json            # Optional: test configuration
```

### Backend-Specific Output

If a test produces different output for different backends, provide backend-specific expected files:

```
testing/tests/cerulean/
└── mytest/
    ├── main.cerulean
    ├── expected_stdout.ceruleanrisc.txt  # For CeruleanRISC backend
    └── expected_stdout.amyasm.txt        # For AmyASM backend
```

### Tests with Input (stdin)

For tests that require stdin input, add a `stdin.txt` file:

```
testing/tests/cerulean/
└── test_input/
    ├── main.cerulean
    ├── stdin.txt            # Input to provide to the program
    └── expected_stdout.txt  # Expected output
```

The contents of `stdin.txt` will be piped to the program when it runs. You can also have backend-specific stdin files like `stdin.{backend}.txt`.

Example `stdin.txt`:
```
Alice
42
3.14
```

## Test Configuration

For advanced control, create a `test.json` file in a multi-file test directory:

```json
{
  "entry": "main.cerulean",
  "compile_order": ["math.cerulean", "main.cerulean"],
  "skip_backends": ["amyasm"],
  "timeout": 10
}
```

**Configuration Options:**
- `entry` - Specifies the entry point file to compile (defaults to `main.*`)
- `compile_order` - Explicit order for compiling source files
- `skip_backends` - List of backends to skip for this test
- `timeout` - Execution timeout in seconds (default: 10)

## CLI Options

```bash
python testing/run_tests.py [options] [test_names...]
```

**Arguments:**
- `test_names` - Specific tests to run (supports glob patterns like `test_*`)

**Options:**
- `--frontend {cerulean,ceruleanir}` - Run only tests for a specific frontend
- `--backend {ceruleanrisc,amyasm}` - Run only tests for a specific backend
- `--list` - List all available tests without running them
- `--update-expected` - Update expected output files with actual output
- `--verbose, -v` - Show detailed compilation and execution output
- `--fail-fast` - Stop on first failure

## Examples

List all available tests:
```bash
python testing/run_tests.py --list
```

Run all control flow tests:
```bash
python testing/run_tests.py "control_*"
```

Run helloworld with only CeruleanRISC backend:
```bash
python testing/run_tests.py helloworld --backend ceruleanrisc
```

Update expected output for all tests (use with caution!):
```bash
python testing/run_tests.py --update-expected
```

Debug a failing test with verbose output:
```bash
python testing/run_tests.py factorial --verbose
```

## Adding New Tests

1. Create test directory: `testing/tests/cerulean/mytest/`
2. Add source file(s): `main.cerulean`, `module.cerulean`, etc.
3. Run the test to see output: `python testing/run_tests.py mytest --verbose`
4. Add `expected_stdout.txt` file with expected output
5. Run again to verify: `python testing/run_tests.py mytest`

Or use `--update-expected` to automatically create the expected file:
```bash
python testing/run_tests.py mytest --update-expected
```

Optionally add `test.json` for advanced configuration (compilation order, backend skipping, etc.).

## Prerequisites

### CeruleanRISC Backend

The CeruleanRISC VM must be built before running tests:

```bash
cd ceruleanrisc/vm
cmake -B build
cmake --build build
```

### AmyASM Backend

The AmyAssembly interpreter must be available at:
```
../AmyAssembly/code/amyAssemblyInterpreter.py
```

## Directory Structure

```
testing/
├── run_tests.py          # Test runner script
├── tests/                # Test files
│   ├── cerulean/         # Cerulean frontend tests
│   │   ├── helloworld.cerulean
│   │   ├── helloworld.expected
│   │   └── ...
│   └── ceruleanir/       # CeruleanIR frontend tests
│       ├── helloworld.ceruleanir
│       ├── helloworld.expected
│       └── ...
└── test_tmp/             # Temporary compilation artifacts (auto-created)
```

## Tips

- Use `--verbose` when debugging test failures to see compilation errors
- Use `--fail-fast` when working on a specific issue to stop at the first failure
- Backend-specific expected files are useful when backends have slightly different output formats
- The testing system automatically handles the full compilation pipeline (compile → assemble → link → execute)
- Test names are derived from filenames (without extension) or directory names
