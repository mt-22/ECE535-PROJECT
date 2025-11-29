#!/usr/bin/env python3
"""
Script to parse and compare model_predictions_1-1.json against large.json
This script compares various fields like baby-present, is-crying, severity score,
description, notification, and hazards.
"""

import json
import re
import statistics
from pathlib import Path


def load_json(file_path):
    """Load JSON from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_prediction(prediction_str):
    """Parse the prediction string into a dictionary."""
    # Handle escaped characters in the prediction string
    prediction_str = prediction_str.replace('\\_', '_')  # Fix escaped underscores

    # remove trailing commas before closing brackets or braces
    prediction_str = re.sub(r',(\s*[}\]])', r'\1', prediction_str)

    try:
        return json.loads(prediction_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing prediction: {e}")
        print(f"Problematic string: {prediction_str}")
        return None


def extract_label_info(label):
    """Extract information from the label in large.json."""
    baby_present = label != "not-present"
    crying = label == "awake/crying"
    sleeping = label == "asleep"
    awake_peaceful = label == "awake/peaceful"

    return {
        'baby_present': baby_present,
        'crying': crying,
        'sleeping': sleeping,
        'awake_peaceful': awake_peaceful
    }


def compare_predictions(large_json_path, predictions_json_path):
    """Compare predictions against the ground truth."""
    # load both JSON files
    large_data = load_json(large_json_path)
    predictions_data = load_json(predictions_json_path)
    
    large_map = {}
    for item in large_data:
        # Extract filename from image path (e.g., "images/synth_00001.png" -> "synth_00001.png")
        filename = Path(item['image']).name
        large_map[filename] = item
    
    prediction_map = {}
    for item in predictions_data:
        filename = item['filename']
        prediction = parse_prediction(item['prediction'])
        if prediction:
            prediction_map[filename] = prediction
    
    # find matching entries
    matching_keys = set(large_map.keys()) & set(prediction_map.keys())
    
    print(f"Found {len(matching_keys)} matching entries out of {len(large_map)} in large.json and {len(prediction_map)} in predictions")
    
    total_matches = len(matching_keys)
    baby_present_correct = 0
    crying_correct = 0
    sleeping_correct = 0
    severity_matches = []

    incorrect_baby_present = []
    incorrect_crying = []
    incorrect_sleeping = []

    for key in matching_keys:
        large_item = large_map[key]
        pred_item = prediction_map[key]

        # extract label information
        label_info = extract_label_info(large_item['label'])

        if label_info['baby_present'] == pred_item['baby_present']:
            baby_present_correct += 1
        else:
            incorrect_baby_present.append({
                'id': large_item['id'],
                'expected': label_info['baby_present'],
                'predicted': pred_item['baby_present']
            })

        if label_info['crying'] == pred_item['crying']:
            crying_correct += 1
        else:
            incorrect_crying.append({
                'id': large_item['id'],
                'expected': label_info['crying'],
                'predicted': pred_item['crying']
            })

        if label_info['sleeping'] == pred_item['sleeping']:
            sleeping_correct += 1
        else:
            incorrect_sleeping.append({
                'id': large_item['id'],
                'expected': label_info['sleeping'],
                'predicted': pred_item['sleeping']
            })

        severity_matches.append({
            'id': large_item['id'],
            'expected_label': large_item['label'],
            'predicted_severity': pred_item['severity'],
            'predicted_crying': pred_item['crying'],
            'predicted_baby_present': pred_item['baby_present']
        })
    
    # print summary
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)

    print(f"\nBaby Present Detection:")
    print(f"  Correct: {baby_present_correct}/{total_matches} ({baby_present_correct/total_matches*100:.2f}%)")

    print(f"\nCrying Detection:")
    print(f"  Correct: {crying_correct}/{total_matches} ({crying_correct/total_matches*100:.2f}%)")

    print(f"\nSleeping Detection:")
    print(f"  Correct: {sleeping_correct}/{total_matches} ({sleeping_correct/total_matches*100:.2f}%)")

    severity_values = [item['predicted_severity'] for item in severity_matches]

    avg_severity = statistics.mean(severity_values) if severity_values else 0
    std_severity = statistics.stdev(severity_values) if len(severity_values) > 1 else 0
    sorted_severity = sorted(severity_values)

    if severity_values:
        q1 = statistics.quantiles(sorted_severity, n=4)[0] if len(severity_values) > 1 else sorted_severity[0]
        median = statistics.median(sorted_severity)
        q3 = statistics.quantiles(sorted_severity, n=4)[2] if len(severity_values) > 1 else sorted_severity[0]
        min_severity = min(severity_values)
        max_severity = max(severity_values)
    else:
        q1 = median = q3 = min_severity = max_severity = 0

    print(f"\nSeverity Statistics:")
    print(f"  Average predicted severity: {avg_severity:.2f}")
    print(f"  Standard deviation: {std_severity:.2f}")
    print(f"  Quartiles: Q1={q1:.2f}, Median={median:.2f}, Q3={q3:.2f}")
    print(f"  Range: {min_severity:.2f} - {max_severity:.2f}")

    total_hazards = sum([len(pred_item['hazards']) for key, pred_item in prediction_map.items() if key in matching_keys])
    print(f"\nHazard Detection:")
    print(f"  Total hazards detected: {total_hazards}")
    print(f"  Images with hazards: {len([key for key, pred_item in prediction_map.items() if key in matching_keys and pred_item['hazards']])}")

    if incorrect_baby_present:
        false_negatives = sum(1 for item in incorrect_baby_present if item['expected'] == True and item['predicted'] == False)  # Missed babies (predicted no when actual yes)
        false_positives = sum(1 for item in incorrect_baby_present if item['expected'] == False and item['predicted'] == True)  # False alarms (predicted yes when actual no)

        print(f"\nBaby Present Error Analysis:")
        print(f"  Missed actual babies (false negatives): {false_negatives}/{len(incorrect_baby_present)} ({false_negatives/len(incorrect_baby_present)*100:.2f}%)")
        print(f"  False alarms (no baby detected as present) (false positives): {false_positives}/{len(incorrect_baby_present)} ({false_positives/len(incorrect_baby_present)*100:.2f}%)")

    print(f"\nIncorrect Baby Present Predictions (showing first 5):")
    for i, item in enumerate(incorrect_baby_present[:5]):
        expected_text = "Baby Present" if item['expected'] else "No Baby"
        predicted_text = "Baby Present" if item['predicted'] else "No Baby"
        print(f"  {item['id']}: Expected {expected_text}, Got {predicted_text}")

    if incorrect_crying:
        false_negatives = sum(1 for item in incorrect_crying if item['expected'] == True and item['predicted'] == False)  # Missed crying (predicted no when actual yes)
        false_positives = sum(1 for item in incorrect_crying if item['expected'] == False and item['predicted'] == True)  # False alarms (predicted yes when actual no)

        print(f"\nCrying Error Analysis:")
        print(f"  Missed actual crying (false negatives): {false_negatives}/{len(incorrect_crying)} ({false_negatives/len(incorrect_crying)*100:.2f}%)")
        print(f"  False alarms - peaceful/quiet detected as crying (false positives): {false_positives}/{len(incorrect_crying)} ({false_positives/len(incorrect_crying)*100:.2f}%)")

    print(f"\nIncorrect Crying Predictions (showing first 5):")
    for i, item in enumerate(incorrect_crying[:5]):
        expected_text = "Crying" if item['expected'] else "Not Crying"
        predicted_text = "Crying" if item['predicted'] else "Not Crying"
        print(f"  {item['id']}: Expected {expected_text}, Got {predicted_text}")

    if incorrect_sleeping:
        false_negatives = sum(1 for item in incorrect_sleeping if item['expected'] == True and item['predicted'] == False)  # Missed sleeping (predicted no when actual yes)
        false_positives = sum(1 for item in incorrect_sleeping if item['expected'] == False and item['predicted'] == True)  # False alarms (predicted yes when actual no)

        print(f"\nSleeping Error Analysis:")
        print(f"  Missed actual sleeping (false negatives): {false_negatives}/{len(incorrect_sleeping)} ({false_negatives/len(incorrect_sleeping)*100:.2f}%)")
        print(f"  False alarms - awake detected as sleeping (false positives): {false_positives}/{len(incorrect_sleeping)} ({false_positives/len(incorrect_sleeping)*100:.2f}%)")

    print(f"\nIncorrect Sleeping Predictions (showing first 5):")
    for i, item in enumerate(incorrect_sleeping[:5]):
        expected_text = "Sleeping" if item['expected'] else "Awake"
        predicted_text = "Sleeping" if item['predicted'] else "Awake"
        print(f"  {item['id']}: Expected {expected_text}, Got {predicted_text}")

    return {
        'total_matches': total_matches,
        'accuracy': {
            'baby_present': baby_present_correct / total_matches,
            'crying': crying_correct / total_matches,
            'sleeping': sleeping_correct / total_matches,
        },
        'incorrect_predictions': {
            'baby_present': incorrect_baby_present,
            'crying': incorrect_crying,
            'sleeping': incorrect_sleeping,
        },
        'severity_stats': severity_matches
    }


def main():
    """Main function to run the comparison."""
    large_json_path = "large/large.json"
    predictions_json_path = "large/model_predictions_1-1.json"
    
    print("Comparing model predictions against ground truth...")
    print(f"Ground truth file: {large_json_path}")
    print(f"Predictions file: {predictions_json_path}")
    
    try:
        results = compare_predictions(large_json_path, predictions_json_path)
        
        print(f"\nDetailed analysis complete. Processed {results['total_matches']} matching entries.")
        
        # Optionally, save detailed results to a file
        output_file = "comparison_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        print("Make sure both JSON files exist in the expected locations.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
