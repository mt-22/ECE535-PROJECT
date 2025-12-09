#!/usr/bin/env python3
"""
Script to parse and compare model_predictions against ground truth in large.json.
This version accommodates newly added labels: baby_present, face_down, crying, sleeping, severity, hazards, notify.
It provides a detailed and verbose output with classification metrics (Precision, Recall, F1, etc.).
"""

import json
import re
import statistics
import argparse
from pathlib import Path

def load_json(file_path):
    """Load JSON from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_prediction(prediction_str):
    """Parse the prediction string into a dictionary."""
    if isinstance(prediction_str, dict):
        return prediction_str

    # Handle escaped characters in the prediction string
    prediction_str = prediction_str.replace(r'\_', '_')  # Fix escaped underscores
    # Remove trailing commas before closing brackets
    prediction_str = re.sub(r',(\s*[}\]])', r'\1', prediction_str)

    try:
        return json.loads(prediction_str)
    except json.JSONDecodeError as e:
        # Fallback: try to find the JSON object if there is extra text
        try:
            match = re.search(r'(\{.*\})', prediction_str, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except:
            pass
        
        print(f"Error parsing prediction string: {e}")
        return None

def calculate_metrics(y_true, y_pred, label_name):
    """Calculate and print classification metrics."""
    tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
    tn = sum(1 for t, p in zip(y_true, y_pred) if not t and not p)
    fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)
    
    total = len(y_true)
    if total == 0:
        return

    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f"\n--- {label_name.upper().replace('_', ' ')} ---")
    print(f"  Accuracy:  {accuracy:.2%} ({tp+tn}/{total})")
    print(f"  Precision: {precision:.2%}")
    print(f"  Recall:    {recall:.2%}")
    print(f"  F1 Score:  {f1:.2f}")
    print(f"  Confusion Matrix: [TP={tp}, TN={tn}, FP={fp}, FN={fn}]")
    
    return {
        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
        'accuracy': accuracy, 'precision': precision, 'recall': recall
    }

def compare_predictions(large_json_path, predictions_json_path):
    print(f"Loading ground truth from: {large_json_path}")
    large_data = load_json(large_json_path)
    
    print(f"Loading predictions from: {predictions_json_path}")
    predictions_data = load_json(predictions_json_path)
    
    # Map ground truth by filename
    large_map = {}
    for item in large_data:
        # Extract filename from "images/synth_00001.png" -> "synth_00001.png"
        fname = Path(item['image']).name
        large_map[fname] = item
    
    # Map predictions by filename
    prediction_map = {}
    for item in predictions_data:
        fname = item['filename']
        # Handle cases where filename might be a path in the prediction file
        fname = Path(fname).name
        
        pred = parse_prediction(item['prediction'])
        if pred:
            prediction_map[fname] = pred
    
    # Find intersection
    common_keys = sorted(list(set(large_map.keys()) & set(prediction_map.keys())))
    print(f"\nFound {len(common_keys)} matching entries (Ground Truth: {len(large_map)}, Predictions: {len(prediction_map)}).")

    if not common_keys:
        print("No matching entries found to compare.")
        return

    # Initialize data collectors
    categories = ['baby_present', 'face_down', 'crying', 'sleeping', 'notify']
    data = {cat: {'true': [], 'pred': [], 'errors': []} for cat in categories}
    
    severity_true = []
    severity_pred = []
    severity_errors = []

    hazards_stats = {'exact_match': 0, 'partial_match': 0, 'no_match': 0, 'total': 0}
    hazard_errors = []

    # Iterate over matches
    for key in common_keys:
        truth = large_map[key]
        pred = prediction_map[key]

        # 1. Boolean Categories
        for cat in categories:
            # Default to False if key missing (safe assumption for boolean flags?)
            # Or skip? Let's assume keys should exist, otherwise default False.
            t_val = truth.get(cat, False)
            p_val = pred.get(cat, False)
            
            data[cat]['true'].append(t_val)
            data[cat]['pred'].append(p_val)
            
            if t_val != p_val:
                data[cat]['errors'].append(f"{key}: Expected {t_val}, Got {p_val}")

        # 2. Severity
        # Severity might be strings in prediction, cast to float/int
        if 'severity' in truth and 'severity' in pred:
            try:
                t_sev = float(truth['severity'])
                p_sev = float(pred['severity'])
                severity_true.append(t_sev)
                severity_pred.append(p_sev)
                if t_sev != p_sev:
                    severity_errors.append(f"{key}: Expected {t_sev}, Got {p_sev}")
            except (ValueError, TypeError):
                pass

        # 3. Hazards
        if 'hazards' in truth and 'hazards' in pred:
            hazards_stats['total'] += 1
            # Normalize hazards: lowercase, strip
            t_haz = set(h.lower().strip() for h in truth['hazards'])
            p_haz = set(h.lower().strip() for h in pred['hazards'])
            
            if t_haz == p_haz:
                hazards_stats['exact_match'] += 1
            elif not t_haz.isdisjoint(p_haz):
                hazards_stats['partial_match'] += 1
                hazard_errors.append(f"{key}: Partial. Exp {t_haz}, Got {p_haz}")
            else:
                hazards_stats['no_match'] += 1
                # Only log error if one of them is not empty (ignoring empty vs empty which is exact match)
                if t_haz or p_haz:
                    hazard_errors.append(f"{key}: Mismatch. Exp {t_haz}, Got {p_haz}")

    # --- PRINT DETAILED REPORT ---
    print("\n" + "="*60)
    print("DETAILED COMPARISON REPORT")
    print("="*60)

    # Print Metrics for each category
    for cat in categories:
        calculate_metrics(data[cat]['true'], data[cat]['pred'], cat)
        
        # Show a few errors if any
        errors = data[cat]['errors']
        if errors:
            print(f"  Top 5 Errors: {errors[:5]}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more.")

    # Severity Analysis
    print("\n--- SEVERITY ---")
    if severity_true:
        mae = statistics.mean([abs(t - p) for t, p in zip(severity_true, severity_pred)])
        mse = statistics.mean([(t - p)**2 for t, p in zip(severity_true, severity_pred)])
        print(f"  Mean Absolute Error (MAE): {mae:.4f}")
        print(f"  Mean Squared Error (MSE):  {mse:.4f}")
        
        # Optional: Distribution of diffs
        diffs = [p - t for t, p in zip(severity_true, severity_pred)]
        print(f"  Prediction Bias (Mean Diff): {statistics.mean(diffs):.4f} (Positive means over-predicting)")
        
        if severity_errors:
            print(f"  Total Mismatches: {len(severity_errors)}")
            print(f"  Top 5 Errors: {severity_errors[:5]}")
    else:
        print("  No valid severity data found.")

    # Hazard Analysis
    print("\n--- HAZARDS ---")
    h_total = hazards_stats['total']
    if h_total > 0:
        print(f"  Exact Matches:   {hazards_stats['exact_match']} ({hazards_stats['exact_match']/h_total:.2%})")
        print(f"  Partial Matches: {hazards_stats['partial_match']} ({hazards_stats['partial_match']/h_total:.2%})")
        print(f"  No Matches:      {hazards_stats['no_match']} ({hazards_stats['no_match']/h_total:.2%})")
        
        if hazard_errors:
            print(f"  Top 5 Mismatches: {hazard_errors[:5]}")
    else:
        print("  No hazard data found.")

    print("\n" + "="*60)
    print("END OF REPORT")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Compare predictions against ground truth.")
    parser.add_argument("predictions_file", help="Path to the predictions JSON file")
    parser.add_argument("--ground-truth", default="large/large.json", help="Path to ground truth (default: large/large.json)")
    
    args = parser.parse_args()
    
    try:
        compare_predictions(args.ground_truth, args.predictions_file)
    except FileNotFoundError as e:
        print(f"File Error: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()