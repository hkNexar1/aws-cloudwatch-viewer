## 🚀 Features

🖥️ User-Friendly Interface: Clean and modern PyQt5 GUI.

🔍 Advanced Filtering: Search logs by patterns and date ranges.

📂 Multi-Group Support: Select and fetch logs from multiple log groups simultaneously.

🌍 Multi-Region Support: Dynamically switch between AWS regions (us-east-1, eu-west-1, etc.).

⚡ Asynchronous Loading: Uses QThread to fetch logs in the background without freezing the UI.

💾 Export Options: Export fetched logs as CSV, JSON, or TXT.

🔐 Secure: Uses AWS Access Keys locally for the current session only.

📦 Installation
1. Clone the repository
```bash
git clone https://github.com/hknexar1/aws-cloudwatch-viewer.git
cd aws-cloudwatch-viewer
```
2. Install dependencies
```bash
pip install boto3 PyQt5
```
3. Run the application
```bash
python src/app.py
```
## 📝 Usage
```bash
Launch the application.

Select an AWS Region (e.g., eu-west-1).

Enter your Access Key ID and Secret Access Key.

Click "Verify AWS Keys & Load Groups".

Select one or multiple Log Groups from the list.

(Optional):

Enter a filter pattern (ERROR, Exception, JSON filter expressions, etc.).

Select how many days back you want to fetch logs.

Click "Download Logs (Async)" to fetch logs in the background.

Export the fetched logs as CSV, JSON, or TXT.
```
## 📁 Project Structure
```bash
aws-cloudwatch-viewer/
│
├── src/
│   |── app.py          # Main PyQt5 application
│
├── README.md
└── requirements.txt
```
## 📄 License

This project is licensed under the MIT License.

