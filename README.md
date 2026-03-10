# EP Inspection Tool Prototype

This repository contains a prototype for an inspection tool that analyzes prompts for quality and effectiveness.

## Project Structure

- `prompt.txt` - The prompt file to be inspected
- `inspection-app/` - Main application directory
  - `app/main.py` - Main application logic
  - `requirements.txt` - Python dependencies

## Usage

To run the inspection tool:

```bash
cd inspection-app
python app/main.py
```

## Features

- Prompt quality analysis based on clarity, completeness, specificity, and context
- Detailed feedback on prompt improvements
- Simple command-line interface

## CI/CD

The repository is configured with GitHub Actions workflows for:
- Claude Code Review
- Claude Code Assistant

These workflows will analyze the code and provide feedback on quality and best practices.