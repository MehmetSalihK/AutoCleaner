import logging
import os
import json
import time
from datetime import datetime

LOG_FILE = os.path.join(os.path.expanduser("~"), f"autocleaner_v6_{int(time.time())}.log")
DELETIONS_LOG = os.path.join(os.path.expanduser("~"), "autocleaner_deletions.jsonl")

# Standard Logger
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutoCleaner")

class ActionLogger:
    @staticmethod
    def log_deletion(path, size, category, action="deleted", error=None):
        """Log a deletion event to JSONL file."""
        entry = {
            "timestamp": time.time(),
            "timestamp_iso": datetime.now().isoformat(),
            "path": path,
            "size": size,
            "category": category,
            "action": action,
            "error": str(error) if error else None
        }
        
        try:
            with open(DELETIONS_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write to deletions log: {e}")

    @staticmethod
    def export_to_csv(output_path):
        """Export JSONL logs to CSV."""
        import csv
        try:
            if not os.path.exists(DELETIONS_LOG):
                return False
                
            with open(DELETIONS_LOG, "r", encoding="utf-8") as f_in, \
                 open(output_path, "w", newline="", encoding="utf-8") as f_out:
                
                writer = csv.writer(f_out)
                writer.writerow(["Timestamp", "Category", "Action", "Size (Bytes)", "Path", "Error"])
                
                for line in f_in:
                    try:
                        data = json.loads(line)
                        writer.writerow([
                            data.get("timestamp_iso"),
                            data.get("category"),
                            data.get("action"),
                            data.get("size"),
                            data.get("path"),
                            data.get("error")
                        ])
                    except:
                        continue
            return True
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return False
