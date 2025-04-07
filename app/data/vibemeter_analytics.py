import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import os
from pathlib import Path

def analyze_vibemeter(csv_path: str = None) -> Tuple[List[Dict[str, int]], List[Dict[str, int]]]:
    """
    Analyzes vibemeter data to identify employees who need attention.
    
    Args:
        csv_path: Path to the CSV file containing vibemeter data.
                 If None, uses the default path in the app/data directory.
    
    Returns:
        A tuple containing two lists of dictionaries:
        - low_vibe_json: List of employees with consistently low vibe scores
        - high_emotion_diff_json: List of employees with high emotional variability
    """
    if csv_path is None:
        # Use the default path relative to this file
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        csv_path = current_dir / "vibemeter_dataset.csv"
    
    # Read the CSV data
    vibemeter = pd.read_csv(csv_path)
    
    # Convert Employee_ID column if it doesn't start with 'EMP'
    if not pd.isna(vibemeter['Employee_ID'].iloc[0]) and not str(vibemeter['Employee_ID'].iloc[0]).startswith('EMP'):
        vibemeter['Employee_ID'] = vibemeter['Employee_ID'].apply(lambda x: f"EMP{x:04d}")
    
    # Count occurrences of each employee ID
    counts = vibemeter['Employee_ID'].value_counts()
    
    # Identify employees with single vs multiple entries
    unique = counts[counts == 1].index
    multiple = counts[counts > 1].index
    
    # Split dataframe based on entry count
    vibe_unique = vibemeter[vibemeter['Employee_ID'].isin(unique)]
    vibe_multi = vibemeter[vibemeter['Employee_ID'].isin(multiple)]
    
    # Analyze emotional variability for employees with multiple entries
    result = []
    for emp_id, group in vibe_multi.groupby('Employee_ID'):
        scores = group['Vibe_Score'].values
        if len(scores) == 2:
            diff = abs(scores[0] - scores[1])
        else:
            mean_score = scores.mean()
            diff = abs((scores - mean_score)).mean()
        result.append({'Employee_ID': emp_id, 'emotion_diff': diff})
    
    vibe_emotion_diff = pd.DataFrame(result)
    
    # Identify employees with low vibe scores (bottom 40%)
    low_vibe_df = vibe_unique[vibe_unique['Vibe_Score'] < vibe_unique['Vibe_Score'].quantile(0.40)][['Employee_ID']]
    
    # Identify employees with high emotional variability (top 15%)
    high_emotion_diff_df = vibe_emotion_diff[vibe_emotion_diff['emotion_diff'] > vibe_emotion_diff['emotion_diff'].quantile(0.85)][['Employee_ID']]
    
    # Convert to JSON format
    low_vibe_json = low_vibe_df.to_dict(orient='records')
    high_emotion_diff_json = high_emotion_diff_df.to_dict(orient='records')
    
    return low_vibe_json, high_emotion_diff_json

def get_employees_for_chat() -> List[Dict[str, int]]:
    """
    Gets the list of employees that should be contacted via chat based on vibemeter analysis.
    
    Returns:
        Combined list of employees (with no duplicates) who need attention via chat.
    """
    low_vibe_json, high_emotion_diff_json = analyze_vibemeter()
    
    # Combine both lists
    all_employees = low_vibe_json + high_emotion_diff_json
    
    # Remove duplicates by converting to a dictionary and back to a list add to database
    unique_employees = list({emp['Employee_ID']: emp for emp in all_employees}.values())
    
    return unique_employees

if __name__ == "__main__":
    # Test the function
    low_json, high_json = analyze_vibemeter()
    # print(f"Employees with low vibe scores: {low_json}")
    # print(f"Employees with high emotional variability: {high_json}")
    
    # Get employees for chat
    employees_for_chat = get_employees_for_chat()
    print(f"Employees to contact via chat: {employees_for_chat}") 