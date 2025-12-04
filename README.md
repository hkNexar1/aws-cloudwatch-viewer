# AWS CloudWatch Log Viewer PRO

A desktop GUI application built with Python (PyQt5) to view, filter, and export AWS CloudWatch logs comfortably without logging into the AWS Console.

## Features
- 🖥️ **User-Friendly Interface:** Clean PyQt5 GUI.
- 🔍 **Advanced Filtering:** Filter logs by patterns and date ranges.
- 📂 **Multi-Group Support:** Select and fetch logs from multiple log groups simultaneously.
- 🌍 **Multi-Region Support:** Dynamically switch between AWS regions (us-east-1, eu-west-1, etc.).
- ⚡ **Asynchronous Loading:** Implements QThread to fetch logs in the background without freezing the UI.
- 💾 **Export Options:** Export logs to CSV, JSON, or TXT formats.
- 🔐 **Secure:** Uses AWS Access Keys (session-based) locally.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hknexar1/aws-cloudwatch-viewer.git
   cd aws-cloudwatch-viewer```
Install the required dependencies:

```Bash

pip install boto3 PyQt5```
Run the application:

```Bash

python src/app.py
(Note: Adjust the path if your file is named differently)
```
```Usage
Launch the App: Run the script to open the GUI.

Credentials & Region: - Select your AWS Region (e.g., eu-west-1).

Enter your Access Key ID and Secret Access Key.

Click "Verify AWS Keys & Load Groups".

Select Logs: Once connected, your Log Groups will appear in the list. Select one or multiple groups (Ctrl/Cmd + Click).

Filter (Optional):

Enter a text pattern (e.g., ERROR or Exception).

Select how many days back you want to search using the spinner.

Download: Click "Download Logs (Async)". The logs will be fetched in the background.

Export: Use the buttons at the bottom to save the fetched logs as CSV, JSON, or TXT.
```

