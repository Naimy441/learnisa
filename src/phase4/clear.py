#!/usr/bin/env python3
"""
Script to clear all .bin, .hex, .dbg, .symbols files and debug_log.txt in the current directory and subdirectories.
"""

import os
import glob

def clear_bin_files():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # File patterns to delete
    patterns = ["**/*.bin", "**/*.hex", "**/*.dbg", "**/*.symbols", "**/debug_log.txt", "**/test_file.txt"]
    all_files = []
    counts = {}

    # Collect files and count by type
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        all_files.extend(files)
        counts[pattern] = len(files)
    
    if not all_files:
        print("No files found to delete.")
        return
    
    print("Files to delete:")
    for pattern in patterns:
        print(f"  {pattern}: {counts[pattern]} files")
    
    deleted_count = 0
    for file_path in all_files:
        # Skip asm_compiler.bin
        if os.path.basename(file_path) == "asm_compiler.bin":
            print(f"  Skipping: {file_path}")
            continue
        
        try:
            print(f"  Deleting: {file_path}")
            os.remove(file_path)
            deleted_count += 1
        except OSError as e:
            print(f"  Error deleting {file_path}: {e}")
    
    print(f"\nSuccessfully deleted {deleted_count} files.")

if __name__ == "__main__":
    clear_bin_files()