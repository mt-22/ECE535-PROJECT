#!/usr/bin/env python3
"""
a script to find missing images by comparing images in a folder with entries in a JSON file.
creates a new JSON file containing the missing entries.
"""
import os
import json
import argparse
from pathlib import Path

def read_json_entries(json_file):
    """read entries from a JSON file"""
    entries = []
    with open(json_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entry = json.loads(line)
                entries.append(entry)
    return entries

def extract_image_names_from_folder(folder_path):
    """extract image names (without extensions) from a folder"""
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
    image_names = set()
    
    for file_path in Path(folder_path).iterdir():
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in image_extensions:
                # get the filename without extension
                image_name = file_path.stem
                image_names.add(image_name)
    
    return image_names

def extract_image_names_from_json_entries(entries):
    """extract image names from JSON entries based on the 'image' field or 'id' field"""
    image_names = set()
    
    for entry in entries:
        # prioritize 'image' field, fall back to 'id'
        image_path = entry.get('image', entry.get('id', ''))
        # Extract just the filename without extension
        if image_path:
            # get the basename and remove extension
            base_name = os.path.basename(image_path)
            image_name = os.path.splitext(base_name)[0]
            image_names.add(image_name)
    
    return image_names

def find_missing_entries(json_file, images_folder):
    """find entries in JSON file that don't have corresponding images in the folder"""
    # read entries from the JSON file
    all_entries = read_json_entries(json_file)
    
    # extract image names from the folder
    folder_image_names = extract_image_names_from_folder(images_folder)
    
    # extract image names from the JSON entries
    json_image_names = extract_image_names_from_json_entries(all_entries)
    
    # find missing entries
    missing_image_names = json_image_names - folder_image_names
    
    # filter entries that are missing from the folder
    missing_entries = []
    for entry in all_entries:
        image_path = entry.get('image', entry.get('id', ''))
        base_name = os.path.basename(image_path)
        image_name = os.path.splitext(base_name)[0]
        
        if image_name in missing_image_names:
            missing_entries.append(entry)
    
    return missing_entries, all_entries, len(folder_image_names)

def main():
    parser = argparse.ArgumentParser(description='Find missing images by comparing JSON entries with images in a folder.')
    parser.add_argument('json_file', help='Path to the JSON file with image entries')
    parser.add_argument('images_folder', help='Path to the folder containing generated images')
    parser.add_argument('--output-file', '-o', help='Output JSON file for missing entries (default: missing_entries.json)', 
                        default='missing_entries.json')
    
    args = parser.parse_args()
    
    # check if the JSON file exists
    if not os.path.exists(args.json_file):
        print(f"Error: JSON file '{args.json_file}' does not exist.")
        exit(1)
    
    # check if the images folder exists
    if not os.path.exists(args.images_folder):
        print(f"Error: Images folder '{args.images_folder}' does not exist.")
        exit(1)
    
    print(f"Reading entries from {args.json_file}...")
    print(f"Checking images in {args.images_folder}...")
    
    missing_entries, all_entries, folder_image_count = find_missing_entries(args.json_file, args.images_folder)
    
    print(f"Total entries in JSON file: {len(all_entries)}")
    print(f"Total images in folder: {folder_image_count}")
    print(f"Missing entries: {len(missing_entries)}")
    
    if missing_entries:
        print(f"Writing missing entries to {args.output_file}...")
        
        # Write missing entries to the output file
        with open(args.output_file, 'w', encoding='utf-8') as f:
            for entry in missing_entries:
                f.write(json.dumps(entry) + '\n')
        
        print(f"Successfully wrote {len(missing_entries)} missing entries to {args.output_file}")
    else:
        print("No missing entries found!")

if __name__ == "__main__":
    main()
