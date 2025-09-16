#!/usr/bin/env python3
"""
Script to clear all .bin files in the current directory and subdirectories.
"""

import os
import glob

def clear_bin_files():
    """Remove all .bin and .hex files in current directory and subdirectories."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Find all .bin and .hex files recursively
    bin_files = glob.glob("**/*.bin", recursive=True)
    hex_files = glob.glob("**/*.hex", recursive=True)
    all_files = bin_files + hex_files
    
    if not all_files:
        print("No .bin or .hex files found to delete.")
        return
    
    print(f"Found {len(bin_files)} .bin files and {len(hex_files)} .hex files to delete:")
    
    deleted_count = 0
    for file_path in all_files:
        try:
            print(f"  Deleting: {file_path}")
            os.remove(file_path)
            deleted_count += 1
        except OSError as e:
            print(f"  Error deleting {file_path}: {e}")
    
    print(f"\nSuccessfully deleted {deleted_count} files.")

if __name__ == "__main__":
    clear_bin_files()
