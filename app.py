import sys
import boto3
import json
import csv
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QListWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, QListWidgetItem,
    QMessageBox, QSpinBox, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ----------------------------------------------------------
# WORKER THREAD
# ----------------------------------------------------------
class LogWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, session, log_groups, filter_pattern, days):
        super().__init__()
        self.session = session
        self.log_groups = log_groups
        self.filter_pattern = filter_pattern
        self.days = days

    def run(self):
        try:
            client = self.session.client("logs")
            start_time = datetime.now() - timedelta(days=self.days)
            start_ts = int(start_time.timestamp() * 1000)
            
            all_events = []

            for log_group in self.log_groups:
               
                response = client.filter_log_events(
                    logGroupName=log_group,
                    filterPattern=self.filter_pattern,
                    startTime=start_ts
                )
                
                events = response.get("events", [])
                all_events.extend(events)

               
                while "nextToken" in response:
                   
                    if self.isInterruptionRequested():
                        return

                    response = client.filter_log_events(
                        logGroupName=log_group,
                        filterPattern=self.filter_pattern,
                        startTime=start_ts,
                        nextToken=response['nextToken']
                    )
                    events = response.get("events", [])
                    all_events.extend(events)

            self.finished.emit(all_events)

        except Exception as e:
            self.error.emit(str(e))

# ----------------------------------------------------------
# MAIN VIEWER CLASS
# ----------------------------------------------------------
class CloudWatchViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.session = None
        self.last_events = []
        self.worker = None 

        self.setWindowTitle("AWS CloudWatch Log Viewer PRO (v2.0)")
        self.setGeometry(200, 150, 950, 750)

        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout()

        # ---------------- AWS KEYS & REGION ----------------
        key_layout = QHBoxLayout()
        
        # Region Selection
        self.region_combo = QComboBox()
        regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", 
                   "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1"]
        self.region_combo.addItems(regions)
        self.region_combo.setCurrentText("eu-west-1") 

        self.access_key_input = QLineEdit()
        self.access_key_input.setPlaceholderText("Access Key ID")
        
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Secret Access Key")
        self.secret_key_input.setEchoMode(QLineEdit.Password)

        key_layout.addWidget(QLabel("Region:"))
        key_layout.addWidget(self.region_combo)
        key_layout.addWidget(QLabel("Access Key:"))
        key_layout.addWidget(self.access_key_input)
        key_layout.addWidget(QLabel("Secret Key:"))
        key_layout.addWidget(self.secret_key_input)

        main_layout.addLayout(key_layout)

        verify_button = QPushButton("Verify AWS Keys & Load Groups")
        verify_button.clicked.connect(self.verify_keys)
        main_layout.addWidget(verify_button)

        # ---------------- LOG GROUPS ----------------
        main_layout.addWidget(QLabel("Select Log Groups (Multi-select):"))

        self.log_group_list = QListWidget()
        self.log_group_list.setSelectionMode(QListWidget.MultiSelection)
        main_layout.addWidget(self.log_group_list)

        # ---------------- FILTER ----------------
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText('e.g. "ERROR" or { $.status = 404 }')
        
        self.days_input = QSpinBox()
        self.days_input.setValue(1)
        self.days_input.setRange(1, 30)

        filter_layout.addWidget(QLabel("Filter Pattern:"))
        filter_layout.addWidget(self.filter_input)

        filter_layout.addWidget(QLabel("Days Back:"))
        filter_layout.addWidget(self.days_input)

        main_layout.addLayout(filter_layout)

        # ---------------- BUTTONS ----------------
        self.fetch_button = QPushButton("Download Logs (Async)")
        self.fetch_button.clicked.connect(self.start_log_download)
        self.fetch_button.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        main_layout.addWidget(self.fetch_button)

        # ---------------- TEXT AREA ----------------
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        main_layout.addWidget(self.text_area)

        # ---------------- EXPORT BUTTONS ----------------
        export_layout = QHBoxLayout()

        csv_btn = QPushButton("Export CSV")
        csv_btn.clicked.connect(self.export_csv)

        json_btn = QPushButton("Export JSON")
        json_btn.clicked.connect(self.export_json)

        txt_btn = QPushButton("Export TXT")
        txt_btn.clicked.connect(self.export_txt)

        export_layout.addWidget(csv_btn)
        export_layout.addWidget(json_btn)
        export_layout.addWidget(txt_btn)

        main_layout.addLayout(export_layout)

        self.setLayout(main_layout)

    # ----------------------------------------------------------
    # AWS VERIFY
    # ----------------------------------------------------------
    def verify_keys(self):
        access_key = self.access_key_input.text().strip()
        secret_key = self.secret_key_input.text().strip()
        region = self.region_combo.currentText()

        if not access_key or not secret_key:
            return QMessageBox.warning(self, "Warning", "Please enter Access Key and Secret Key.")

        try:
            
            self.session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )

            
            sts = self.session.client("sts")
            identity = sts.get_caller_identity()

            QMessageBox.information(self, "Success", f"Connected as: {identity['Arn']}")
            self.load_log_groups()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection Failed:\n{str(e)}")
            print(e)

    # ----------------------------------------------------------
    # LOAD LOG GROUPS
    # ----------------------------------------------------------
    def load_log_groups(self):
        self.log_group_list.clear()
        client = self.session.client("logs")

        try:
            response = client.describe_log_groups()
            groups = []
            
            while True:
                groups.extend([g['logGroupName'] for g in response['logGroups']])
                if "nextToken" in response:
                    response = client.describe_log_groups(nextToken=response['nextToken'])
                else:
                    break

            
            groups.sort()
            for g in groups:
                item = QListWidgetItem(g)
                self.log_group_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load groups: {e}")

    # ----------------------------------------------------------
    # START DOWNLOAD (THREADING)
    # ----------------------------------------------------------
    def start_log_download(self):
        if not self.session:
            return QMessageBox.warning(self, "Error", "Please verify AWS keys first.")

        selected_items = self.log_group_list.selectedItems()
        if not selected_items:
            return QMessageBox.warning(self, "Error", "Please select at least one log group.")

        
        log_groups = [item.text() for item in selected_items]
        filter_pattern = self.filter_input.text().strip()
        days = self.days_input.value()

        
        self.text_area.clear()
        self.text_area.setText("Downloading logs... Please wait...")
        self.fetch_button.setEnabled(False)
        self.fetch_button.setText("Downloading... (Please Wait)")

        
        self.worker = LogWorker(self.session, log_groups, filter_pattern, days)
        self.worker.finished.connect(self.on_download_complete)
        self.worker.error.connect(self.on_download_error)
        self.worker.start()

    # ----------------------------------------------------------
    # THREAD CALLBACKS
    # ----------------------------------------------------------
    def on_download_complete(self, events):
        self.last_events = events
        self.display_logs(events)
        
        
        self.fetch_button.setEnabled(True)
        self.fetch_button.setText("Download Logs (Async)")
        
        QMessageBox.information(self, "Done", f"{len(events)} log events downloaded.")

    def on_download_error(self, error_msg):
        self.fetch_button.setEnabled(True)
        self.fetch_button.setText("Download Logs (Async)")
        self.text_area.setText("Error occurred.")
        QMessageBox.critical(self, "Error", f"Download failed:\n{error_msg}")

    # ----------------------------------------------------------
    # DISPLAY LOGS
    # ----------------------------------------------------------
    def display_logs(self, events):
        self.text_area.clear()
        
        
        events.sort(key=lambda x: x['timestamp'])

        html_output = ""
        for e in events:
            timestamp = e["timestamp"]
            msg = e["message"]

            dt = datetime.fromtimestamp(timestamp / 1000)
            human_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            formatted_msg = self.pretty_print(msg)
            
           
            html_output += f"<b style='color:#2c3e50'>[{human_date}]</b><br><pre>{formatted_msg}</pre><hr>"

        self.text_area.setHtml(html_output)

    # ----------------------------------------------------------
    # UTILS & EXPORT
    # ----------------------------------------------------------
    def pretty_print(self, msg):
        try:
            parsed = json.loads(msg)
            return json.dumps(parsed, indent=4)
        except:
            return msg

    def export_csv(self):
        if not self.last_events: return
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "message"])
                for e in self.last_events:
                    ts = datetime.fromtimestamp(e["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([ts, e["message"]])
            QMessageBox.information(self, "Success", "CSV exported.")

    def export_json(self):
        if not self.last_events: return
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.last_events, f, indent=4)
            QMessageBox.information(self, "Success", "JSON exported.")

    def export_txt(self):
        if not self.last_events: return
        path, _ = QFileDialog.getSaveFileName(self, "Save TXT", "", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                for e in self.last_events:
                    ts = datetime.fromtimestamp(e["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{ts}] {e['message']}\n")
            QMessageBox.information(self, "Success", "TXT exported.")

# ------------------------------ RUN APP ------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CloudWatchViewer()
    viewer.show()
    sys.exit(app.exec_())
