#!/usr/bin/env python3
"""
Script to automatically run and grade test suite
"""

import sys
import os
import io
from isa import ISA

class TestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def capture_output(self, test_func):
        """Capture stdout from test execution"""
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        try:
            test_func()
            output = captured_output.getvalue()
        finally:
            sys.stdout = old_stdout
        return output.strip()

    def run_isa_test(self, test_name):
        """Run a single ISA test and return output"""
        def test_execution():
            try:
                isa = ISA(f"tests/{test_name}")
                isa.assemble(f"tests/{test_name}", False)
                isa.run(f"tests/{test_name}", False)
            except Exception as e:
                print(f"Error: {e}")
        
        return self.capture_output(test_execution)

    def run_isa_test_with_args(self, test_name, args):
        """Run a single ISA test with command line arguments and return output"""
        def test_execution():
            try:
                isa = ISA(f"tests/{test_name}")
                isa.assemble(f"tests/{test_name}", False)
                argc = len(args)
                isa.run(f"tests/{test_name}", False, argc, args)
            except Exception as e:
                print(f"Error: {e}")
        
        return self.capture_output(test_execution)

    def verify_register_state(self, test_name, expected_reg_values):
        """Verify final register state for tests that don't produce output"""
        try:
            isa = ISA(f"tests/{test_name}")
            isa.assemble(f"tests/{test_name}", False)
            isa.run(f"tests/{test_name}", False)
            
            for reg, expected_val in expected_reg_values.items():
                actual_val = isa.reg[reg]
                if actual_val != expected_val:
                    return False, f"R{reg}: expected {expected_val}, got {actual_val}"
            return True, "Register state correct"
        except Exception as e:
            return False, f"Error: {e}"

    def run_test(self, test_name, expected_output=None, expected_registers=None):
        """Run a test and verify results"""
        print(f"Running {test_name}...", end=" ")
        
        if expected_output is not None:
            # Test produces output
            try:
                output = self.run_isa_test(test_name)
                if output == expected_output:
                    print("PASS")
                    self.tests_passed += 1
                    self.test_results.append((test_name, "PASS", ""))
                else:
                    print("FAIL")
                    self.tests_failed += 1
                    self.test_results.append((test_name, "FAIL", f"Expected '{expected_output}', got '{output}'"))
            except Exception as e:
                print("ERROR")
                self.tests_failed += 1
                self.test_results.append((test_name, "ERROR", str(e)))
        
        elif expected_registers is not None:
            # Test modifies registers
            success, message = self.verify_register_state(test_name, expected_registers)
            if success:
                print("PASS")
                self.tests_passed += 1
                self.test_results.append((test_name, "PASS", ""))
            else:
                print("FAIL")
                self.tests_failed += 1
                self.test_results.append((test_name, "FAIL", message))
        
        else:
            # Test just needs to run without error
            try:
                self.run_isa_test(test_name)
                print("PASS")
                self.tests_passed += 1
                self.test_results.append((test_name, "PASS", ""))
            except Exception as e:
                print("ERROR")
                self.tests_failed += 1
                self.test_results.append((test_name, "ERROR", str(e)))

    def run_test_with_args(self, test_name, args, expected_output):
        """Run a test with command line arguments and verify results"""
        print(f"Running {test_name} with args {args}...", end=" ")
        
        try:
            output = self.run_isa_test_with_args(test_name, args)
            if output == expected_output:
                print("PASS")
                self.tests_passed += 1
                self.test_results.append((test_name, "PASS", ""))
            else:
                print("FAIL")
                self.tests_failed += 1
                self.test_results.append((test_name, "FAIL", f"Expected '{expected_output}', got '{output}'"))
        except Exception as e:
            print("ERROR")
            self.tests_failed += 1
            self.test_results.append((test_name, "ERROR", str(e)))

    def run_all_tests(self):
        """Run all tests with their expected outcomes"""
        print("Running ISA Tests...")
        print("=" * 50)
        
        # Tests that modify registers only
        register_tests = [
            ("nop", {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}),  # No change
            ("load", {0: 42}),
            ("mov", {0: 123, 1: 123}),
            ("inc", {0: 6}),
            ("add", {0: 30, 1: 20}),
            ("sub", {0: 20, 1: 10}),
            ("mul", {0: 42, 1: 7}),
            ("div", {0: 5, 1: 4}),
            ("and", {0: 7, 1: 7}),
            ("or", {0: 12, 1: 4}),
            ("xor", {0: 9, 1: 5}),
            ("not", {0: 65365}),
            ("shl", {0: 10}),
            ("shr", {0: 4}),
            ("jmp", {0: 1}),
            ("jz", {0: 99}),
            ("jnz", {0: 99}),
            ("jc", {0: 99}),
            ("jnc", {0: 99}),
            ("pop", {0: 42, 1: 42}),
            ("call", {0: 3}),
            ("ret", {0: 42}),
            ("halt", {0: 1}),
        ]
        
        # Tests that produce output
        output_tests = [
            ("sys", "A"),
            ("data_word", "1024"),
            ("data_byte", "A"),
            ("data_string", "Hello"),
            ("file", "HelloWorld!"),
        ]
        
        # Tests that just need to run without error
        basic_tests = [
            "store",
            "lb", 
            "sb",
            "cmp",
            "push",
        ]
        
        # Run register tests
        for test_name, expected_regs in register_tests:
            self.run_test(test_name, expected_registers=expected_regs)
        
        # Run output tests
        for test_name, expected_output in output_tests:
            self.run_test(test_name, expected_output=expected_output)
        
        # Run basic tests
        for test_name in basic_tests:
            self.run_test(test_name)
        
        # Run tests with command line arguments
        self.run_test_with_args("concat", ["Hello", "World"], "HelloWorld")
        
        # Print summary
        print("=" * 50)
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_failed}")
        print(f"Total tests: {self.tests_passed + self.tests_failed}")
        
        if self.tests_failed > 0:
            print("\nFailed tests:")
            for test_name, status, message in self.test_results:
                if status in ["FAIL", "ERROR"]:
                    print(f"  {test_name}: {message}")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)