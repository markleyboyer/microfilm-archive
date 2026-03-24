#!/usr/bin/env python3
"""
Extract and count unique names from filenames.
Counts unique values between the underscore and .jpg extension.
"""

import os
import sys
from pathlib import Path
from collections import Counter


def extract_name(filename):
    """
    Extract the name between underscore and .jpg
    Example: IMG_7885_1829FairfieldAcademy.JPG -> 1829FairfieldAcademy
    """
    # Remove extension
    name_without_ext = filename.rsplit('.', 1)[0]
    
    # Split by underscore and get the last part
    parts = name_without_ext.split('_')
    if len(parts) >= 3:
        # Return everything after the second underscore
        return '_'.join(parts[2:])
    elif len(parts) == 2:
        # If only one underscore, return the part after it
        return parts[1]
    else:
        return None


def parse_name_date_academy(name):
    """
    Parse the name to extract date and academy.
    Example: 1829FairfieldAcademy -> date=1829, academy=FairfieldAcademy
    """
    # Extract leading digits as date
    date_str = ""
    academy_str = ""
    
    for i, char in enumerate(name):
        if char.isdigit():
            date_str += char
        else:
            academy_str = name[i:]
            break
    
    return date_str, academy_str


def analyze_directory(directory):
    """
    Analyze all files in directory and count unique names.
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return
    
    # Find all JPG files
    jpg_files = list(directory_path.glob("*.jpg")) + list(directory_path.glob("*.JPG")) + \
                list(directory_path.glob("*.jpeg")) + list(directory_path.glob("*.JPEG"))
    
    if not jpg_files:
        print(f"No JPEG files found in '{directory}'")
        return
    
    print(f"Found {len(jpg_files)} JPEG files\n")
    
    # Extract names and count
    names = []
    invalid = []
    
    for filepath in jpg_files:
        name = extract_name(filepath.name)
        if name:
            names.append(name)
        else:
            invalid.append(filepath.name)
    
    # Count unique names
    unique_names = set(names)
    name_counts = Counter(names)
    
    print(f"Total files: {len(jpg_files)}")
    print(f"Unique academy/date combinations: {len(unique_names)}")
    print(f"Invalid filenames (couldn't extract name): {len(invalid)}\n")
    
    # Parse and organize by academy/date
    records = []
    for name in sorted(unique_names):
        date, academy = parse_name_date_academy(name)
        count = name_counts[name]
        records.append({
            'academy': academy,
            'date': date,
            'count': count
        })
    
    # Sort by academy, then date
    records.sort(key=lambda x: (x['academy'], x['date']))
    
    # Display as table
    print("Academy                          | Date | File Count")
    print("-" * 60)
    for record in records:
        print(f"{record['academy']:32s} | {record['date']:4s} | {record['count']:6d}")
    
    print("-" * 60)
    print(f"Total: {len(records)} unique combinations\n")
    
    # Save to file
    output_file = directory_path / "unique_names_report.txt"
    with open(output_file, 'w') as f:
        f.write(f"Academy/Date Report\n")
        f.write(f"Total files: {len(jpg_files)}\n")
        f.write(f"Unique academy/date combinations: {len(unique_names)}\n")
        f.write(f"Invalid filenames: {len(invalid)}\n\n")
        f.write("Academy                          | Date | File Count\n")
        f.write("-" * 60 + "\n")
        for record in records:
            f.write(f"{record['academy']:32s} | {record['date']:4s} | {record['count']:6d}\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total: {len(records)} unique combinations\n")
    
    print(f"Report saved to: {output_file}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_filenames.py <directory>")
        print("\nExample:")
        print('  python analyze_filenames.py "D:\\Farmscape Weather Data\\Copy of some files"')
        sys.exit(1)
    
    directory = sys.argv[1]
    analyze_directory(directory)


if __name__ == "__main__":
    main()
