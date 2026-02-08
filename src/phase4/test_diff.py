#!/usr/bin/env python3
"""
Script to test asm_compiler.bin against regular assembler.py
Compares binary outputs using hexdump and reports statistics
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from assembler import Assembler

class BinaryComparisonTester:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.assembly_errors = 0
        self.comparison_errors = 0
        self.test_results = []
        
        # Ensure we're in the right directory
        self.base_dir = Path(__file__).parent
        os.chdir(self.base_dir)
        
        # Check if asm_compiler.bin exists
        if not os.path.exists("asm_compiler.bin"):
            raise FileNotFoundError("asm_compiler.bin not found in current directory")
        
        # Check if isa.py exists
        if not os.path.exists("isa.py"):
            raise FileNotFoundError("isa.py not found in current directory")

    def run_asm_compiler(self, asm_file, output_file):
        """Run asm_compiler.bin on an assembly file using subprocess with timeout"""
        try:
            # asm_compiler.bin creates output in same directory as input with .bin extension
            asm_path = Path(asm_file)
            expected_output = asm_path.with_suffix('.bin')
            
            # Remove existing output file if it exists
            if expected_output.exists():
                expected_output.unlink()
            
            # Create a temporary isa script that doesn't use step mode
            temp_isa_content = '''#!/usr/bin/env python3
import sys
from isa import ISA

if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_fn = sys.argv[1]
        isa = ISA()
        if len(sys.argv) > 2:
            argv = sys.argv[2:]
            argc = len(argv)
            isa.run(input_fn, debug_mode=False, step_mode=False, argc=argc, argv=argv)
        else:
            isa.run(input_fn, debug_mode=False, step_mode=False)
'''
            
            # Write temporary isa script
            temp_isa_path = "temp_isa_no_step.py"
            with open(temp_isa_path, 'w') as f:
                f.write(temp_isa_content)
            
            try:
                # Use the temporary script with timeout
                cmd = ["python3", temp_isa_path, "asm_compiler.bin", asm_file]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    return False, f"asm_compiler.bin failed: {result.stderr.strip()}"
                
                # Check if output file was created where expected
                if not expected_output.exists():
                    return False, f"asm_compiler.bin did not create expected output file: {expected_output}"
                
                # Copy the created file to our desired output location
                shutil.copy2(str(expected_output), output_file)
                
                # Clean up the created file
                expected_output.unlink()
                
                return True, "Success"
            finally:
                # Clean up temporary script
                if os.path.exists(temp_isa_path):
                    os.unlink(temp_isa_path)
                    
        except subprocess.TimeoutExpired:
            return False, "asm_compiler.bin timed out (likely infinite loop)"
        except Exception as e:
            return False, f"Error running asm_compiler.bin: {str(e)}"

    def run_regular_assembler(self, asm_file, output_file):
        """Run regular assembler.py on an assembly file"""
        try:
            assembler = Assembler(asm_file)
            assembler.assemble(output_file)
            
            if not os.path.exists(output_file):
                return False, f"assembler.py did not create output file: {output_file}"
            
            return True, "Success"
        except Exception as e:
            return False, f"assembler.py failed: {str(e)}"

    def create_hexdump(self, binary_file, hex_file):
        """Create hexdump of binary file"""
        try:
            cmd = ["hexdump", "-C", binary_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"hexdump failed: {result.stderr.strip()}"
            
            with open(hex_file, 'w') as f:
                f.write(result.stdout)
            
            return True, "Success"
        except Exception as e:
            return False, f"Error creating hexdump: {str(e)}"

    def compare_hexdumps(self, hex_file1, hex_file2):
        """Compare two hexdump files using diff"""
        try:
            cmd = ["diff", hex_file1, hex_file2]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Files are identical"
            else:
                return False, f"Files differ:\n{result.stdout}"
        except Exception as e:
            return False, f"Error comparing files: {str(e)}"

    def test_single_file(self, asm_file):
        """Test a single assembly file"""
        test_name = Path(asm_file).stem
        print(f"Testing {test_name}...", end=" ")
        
        # Create temporary directory for this test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Output files
            asm_compiler_bin = temp_path / f"{test_name}_asm_compiler.bin"
            regular_bin = temp_path / f"{test_name}_regular.bin"
            asm_compiler_hex = temp_path / f"{test_name}_asm_compiler.hex"
            regular_hex = temp_path / f"{test_name}_regular.hex"
            
            # Test asm_compiler.bin
            success1, msg1 = self.run_asm_compiler(asm_file, str(asm_compiler_bin))
            if not success1:
                print("ERROR (asm_compiler)")
                self.assembly_errors += 1
                self.test_results.append((test_name, "ERROR", f"asm_compiler.bin: {msg1}"))
                return
            
            # Test regular assembler
            success2, msg2 = self.run_regular_assembler(asm_file, str(regular_bin))
            if not success2:
                print("ERROR (assembler)")
                self.assembly_errors += 1
                self.test_results.append((test_name, "ERROR", f"assembler.py: {msg2}"))
                return
            
            # Create hexdumps
            success3, msg3 = self.create_hexdump(str(asm_compiler_bin), str(asm_compiler_hex))
            if not success3:
                print("ERROR (hexdump1)")
                self.comparison_errors += 1
                self.test_results.append((test_name, "ERROR", f"hexdump asm_compiler: {msg3}"))
                return
            
            success4, msg4 = self.create_hexdump(str(regular_bin), str(regular_hex))
            if not success4:
                print("ERROR (hexdump2)")
                self.comparison_errors += 1
                self.test_results.append((test_name, "ERROR", f"hexdump regular: {msg4}"))
                return
            
            # Compare hexdumps
            success5, msg5 = self.compare_hexdumps(str(asm_compiler_hex), str(regular_hex))
            if success5:
                print("PASS")
                self.tests_passed += 1
                self.test_results.append((test_name, "PASS", ""))
            else:
                print("FAIL")
                self.tests_failed += 1
                self.test_results.append((test_name, "FAIL", msg5))

    def run_all_tests(self):
        """Run tests on all assembly files"""
        print("Binary Comparison Tests - asm_compiler.bin vs assembler.py")
        print("=" * 60)
        
        # Get all test files from tests directory
        test_files = []
        tests_dir = Path("tests")
        if tests_dir.exists():
            test_files.extend(sorted(tests_dir.glob("*.asm")))
        
        # Get all program files from programs directory  
        programs_dir = Path("programs")
        if programs_dir.exists():
            test_files.extend(sorted(programs_dir.glob("*.asm")))
        
        if not test_files:
            print("No .asm files found in tests/ or programs/ directories")
            return False
        
        print(f"Found {len(test_files)} assembly files to test")
        print("-" * 60)
        
        # Test each file
        for asm_file in test_files:
            self.test_single_file(str(asm_file))
        
        # Print detailed results
        self.print_results()
        
        return self.tests_failed == 0 and self.assembly_errors == 0 and self.comparison_errors == 0

    def print_results(self):
        """Print comprehensive test results and statistics"""
        print("=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = self.tests_passed + self.tests_failed + self.assembly_errors + self.comparison_errors
        
        print(f"Total files tested: {total_tests}")
        print(f"Binary matches (PASS): {self.tests_passed}")
        print(f"Binary differences (FAIL): {self.tests_failed}")
        print(f"Assembly errors: {self.assembly_errors}")
        print(f"Comparison errors: {self.comparison_errors}")
        
        if total_tests > 0:
            pass_rate = (self.tests_passed / total_tests) * 100
            print(f"Success rate: {pass_rate:.1f}%")
        
        # Detailed breakdown
        if self.tests_failed > 0:
            print("\n" + "=" * 60)
            print("BINARY DIFFERENCES (FAIL)")
            print("=" * 60)
            for test_name, status, message in self.test_results:
                if status == "FAIL":
                    print(f"\n{test_name}:")
                    # Truncate long diff outputs for readability
                    if len(message) > 500:
                        lines = message.split('\n')
                        if len(lines) > 10:
                            truncated = '\n'.join(lines[:10]) + f"\n... ({len(lines)-10} more lines)"
                            print(f"  {truncated}")
                        else:
                            print(f"  {message}")
                    else:
                        print(f"  {message}")
        
        if self.assembly_errors > 0:
            print("\n" + "=" * 60)
            print("ASSEMBLY ERRORS")
            print("=" * 60)
            for test_name, status, message in self.test_results:
                if status == "ERROR" and ("asm_compiler" in message or "assembler.py" in message):
                    print(f"{test_name}: {message}")
        
        if self.comparison_errors > 0:
            print("\n" + "=" * 60)
            print("COMPARISON ERRORS")
            print("=" * 60)
            for test_name, status, message in self.test_results:
                if status == "ERROR" and ("hexdump" in message or "diff" in message):
                    print(f"{test_name}: {message}")
        
        if self.tests_passed > 0:
            print("\n" + "=" * 60)
            print("SUCCESSFUL MATCHES (PASS)")
            print("=" * 60)
            passed_tests = [test_name for test_name, status, _ in self.test_results if status == "PASS"]
            for i, test_name in enumerate(passed_tests):
                if i % 5 == 0:
                    print()
                print(f"{test_name:<15}", end=" ")
            print()

def main():
    """Main function"""
    try:
        tester = BinaryComparisonTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
