#!/usr/bin/env python3
"""
EP Inspection Tool - Main Application
"""

import os
import sys
from typing import Dict, Any

def load_prompt(file_path: str) -> str:
    """Load prompt from file."""
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "No prompt file found."

def analyze_prompt(prompt: str) -> Dict[str, Any]:
    """Analyze prompt quality."""
    analysis = {
        "clarity": "Good",
        "completeness": "Good",
        "specificity": "Good",
        "context": "Good",
        "overall_score": 4.5,
        "feedback": "Prompt is well-structured and provides clear instructions."
    }

    # Basic analysis logic
    if len(prompt) < 50:
        analysis["clarity"] = "Poor"
        analysis["feedback"] = "Prompt is too short. Consider adding more detail."

    return analysis

def main():
    """Main application entry point."""
    prompt_file = "prompt.txt"

    prompt = load_prompt(prompt_file)
    analysis = analyze_prompt(prompt)

    print("EP Inspection Tool Results")
    print("=" * 30)
    print(f"Prompt: {prompt[:100]}...")
    print(f"Clarity: {analysis['clarity']}")
    print(f"Completeness: {analysis['completeness']}")
    print(f"Specificity: {analysis['specificity']}")
    print(f"Context: {analysis['context']}")
    print(f"Overall Score: {analysis['overall_score']}")
    print(f"Feedback: {analysis['feedback']}")

if __name__ == "__main__":
    main()