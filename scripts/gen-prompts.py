import json
import random
import argparse

classes = ["asleep", "awake/peaceful", "awake/crying", "not-present"]
ethnicities = ["Caucasian", "Asian", "African American", "Hispanic", "South Asian", "Middle Eastern"]
ages = ["newborn", "1-month-old", "3-month-old", "6-month-old", "9-month-old", "toddler"]
lightings = ["dim nursery light", "soft daylight", "nighttime with nightlight", "infrared-like glow", "bright overhead lamp"]
angles = ["overhead crib view", "angled from baby monitor camera", "side profile in crib", "slightly distorted fisheye lens"]
clothing = ["in a onesie", "wrapped in swaddle", "pajamas", "diaper only", "with bib"]
expressions_asleep = ["eyes closed peacefully", "slight breathing motion", "thumb in mouth"]
expressions_peaceful = ["wide-eyed and calm", "gentle smile", "curious gaze at ceiling"]
expressions_crying = ["mouth open wailing", "tears streaming", "face red and scrunched"]
environments = ["plain white crib sheets", "with patterned blanket", "mobile hanging above", "teddy bear in corner", "scattered soft toys"]
crib_styles = ["wooden crib", "modern white crib", "bassinet", "playpen"]

# more dim lights when asleep
lighting_weights = [0.3, 0.15, 0.25, 0.2, 0.1]  # Higher for dim

def generate_entry(entry_id, class_name):
    ethnicity = random.choice(ethnicities)
    age = random.choice(ages)
    lighting = random.choices(lightings, weights=lighting_weights if class_name == "asleep" else None)[0]
    angle = random.choice(angles)
    cloth = random.choice(clothing)
    env = random.choice(environments)
    crib = random.choice(crib_styles)
    
    if class_name == "asleep":
        expr = random.choice(expressions_asleep)
        description = f"{angle} of a {expr} {ethnicity} {age} baby {cloth} in a {crib}, {lighting}, {env}."
    elif class_name == "awake/peaceful":
        expr = random.choice(expressions_peaceful)
        description = f"{angle} of a {expr} {ethnicity} {age} baby {cloth} in a {crib}, awake but content, {lighting}, {env}."
    elif class_name == "awake/crying":
        expr = random.choice(expressions_crying)
        description = f"{angle} of a {expr} {ethnicity} {age} baby {cloth} in a {crib}, distressed, {lighting}, {env}."
    else:  # not-present
        description = f"{angle} of an empty {crib}, rumpled {env}, {lighting}, no baby visible."
    
    # LLaVA-style conversation
    human_prompt = "<image>\nClassify the baby's state in the crib: asleep, awake/peaceful, awake/crying, or not-present."
    gpt_response = class_name
    
    return {
        "id": f"synth_{entry_id:05d}",
        "image": f"images/synth_{entry_id:05d}.png",
        "prompt": description,  
        "label": class_name,  
        "conversations": [
            {"from": "human", "value": human_prompt},
            {"from": "gpt", "value": gpt_response}
        ]
    }

def main():
    parser = argparse.ArgumentParser(description="Generate image prompts with labels for baby state classification")
    parser.add_argument("--num-per-class", type=int, default=1000, 
                        help="Number of prompts to generate per class (default: 1000)")
    parser.add_argument("--output-json", type=str, default="llava_finetune_dataset.json",
                        help="Output JSON file name (default: llava_finetune_dataset.json)")
    parser.add_argument("--output-prompts", type=str, default="prompts.txt",
                        help="Output prompts file name (default: prompts.txt)")
    parser.add_argument("--class", type=str, default=None, choices=classes,
                        help="Generate prompts for a specific class only (default: all classes)")
    
    args = parser.parse_args()
    
    selected_classes = [args.__dict__["class"]] if args.__dict__["class"] is not None else classes
    
    entries = []
    entry_id = 1
    for class_name in selected_classes:
        for _ in range(args.num_per_class):  
            entries.append(generate_entry(entry_id, class_name))
            entry_id += 1

    # save as JSON (one JSON per line)
    with open(args.output_json, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    # Also save plain prompts for TextUI (extract from entries)
    with open(args.output_prompts, "w") as f:
        for entry in entries:
            f.write(entry["prompt"] + "\n")

    print(f"Generated {len(entries)} entries ({args.num_per_class} per class). Use {args.output_prompts} for TextUI automation.")

if __name__ == "__main__":
    main()
