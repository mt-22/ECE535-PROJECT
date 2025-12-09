import json
import os
import sys
import base64

# Configuration
JSON_FILE = 'large.json'
IMAGE_DIR = '.'  # Images are relative to this directory based on the JSON "image" field

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_data():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        sys.exit(1)
    with open(JSON_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Failed to decode {JSON_FILE}.")
            sys.exit(1)

def save_data(data):
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_input(prompt_text, default=None, valid_options=None, cast_func=None):
    while True:
        if default is not None:
            display_prompt = f"{prompt_text} [{default}]: "
        else:
            display_prompt = f"{prompt_text}: "
        
        user_input = input(display_prompt).strip()
        
        if user_input == "" and default is not None:
            return default
        
        if valid_options and user_input not in valid_options:
            print(f"Invalid input. Options: {', '.join(valid_options)}")
            continue
            
        if cast_func:
            try:
                return cast_func(user_input)
            except ValueError:
                print("Invalid format.")
                continue
                
        return user_input

def derive_fields(item):
    """Derives baby_present, crying, sleeping from the label."""
    label = item.get('label', '').lower()
    
    baby_present = True
    sleeping = False
    crying = False
    
    if 'not-present' in label or 'empty' in label:
        baby_present = False
    elif 'asleep' in label:
        sleeping = True
    elif 'crying' in label:
        crying = True
        
    return baby_present, sleeping, crying

def main():
    data = load_data()
    total = len(data)
    
    print(f"Loaded {total} records from {JSON_FILE}.")
    
    for i, item in enumerate(data):
        # Check if record is already fully annotated. 
        if 'severity' in item and 'hazards' in item:
            continue
            
        clear_screen()
        print(f"[{i+1}/{total}] Processing ID: {item.get('id', 'Unknown')}")
        
        # Derive fields
        baby_present, sleeping, crying = derive_fields(item)
        print(f"Label: {item.get('label')} -> Present: {baby_present}, Sleeping: {sleeping}, Crying: {crying}")
        print(f"Description (Prompt): {item.get('prompt', 'N/A')}")
        
        # Display image in terminal
        image_path = os.path.join(IMAGE_DIR, item.get('image', ''))
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f_img:
                    img_data = f_img.read()
                    b64data = base64.b64encode(img_data).decode('utf-8')
                    # iTerm2 Inline Image Protocol: width=auto, preserveAspectRatio=1
                    print(f"\033]1337;File=inline=1;width=auto;preserveAspectRatio=1:{b64data}\a")
            except Exception as e:
                print(f"Error displaying image: {e}")
        else:
            print(f"Warning: Image file not found: {image_path}")

        print("\n--- Annotation ---")
        
        face_down_in = get_input("Face Down? (y/n)", default="n", valid_options=['y', 'n', 'yes', 'no'])
        face_down = face_down_in.lower().startswith('y')
        
        severity = get_input("Severity (0-10)", default=0, cast_func=int)
        
        hazards_in = get_input("Hazards (comma separated)", default="None")
        hazards = [h.strip() for h in hazards_in.split(',')] if hazards_in.lower() != "none" else []
        
        default_notify = "y" if severity >= 7 else "n"
        notify_in = get_input("Notify? (y/n)", default=default_notify, valid_options=['y', 'n', 'yes', 'no'])
        notify = notify_in.lower().startswith('y')

        scratchpad = get_input("Scratchpad (optional)", default="")
        
        # Update Item
        item['baby_present'] = baby_present
        item['face_down'] = face_down
        item['crying'] = crying
        item['sleeping'] = sleeping
        item['severity'] = severity
        item['hazards'] = hazards
        item['notify'] = notify
        item['scratchpad'] = scratchpad
        # Use existing prompt as description if not present, or maybe just clean it up?
        if 'description' not in item:
            item['description'] = item.get('prompt', '')

        # Save immediately
        save_data(data)
        print("Saved.")

    print("\nAll images annotated!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
