"""
CLI System Info & Health Monitor
--------------------------------
A CLI tool to fetch system architecture, CPU load, memory utilization, and disk usage statistics using standard Python libraries.
"""

import os
import sys
import platform
import shutil
import time

class SystemMonitor:
    @staticmethod
    def get_system_info() -> dict:
        return {
            "OS": f"{platform.system()} {platform.release()}",
            "Architecture": platform.machine(),
            "Python Version": platform.python_version(),
            "Processor": platform.processor() or "N/A",
            "Hostname": platform.node()
        }

    @staticmethod
    def get_disk_usage(path: str = "/") -> dict:
        total, used, free = shutil.disk_usage(path)
        gb = 1024 ** 3
        return {
            "Total (GB)": round(total / gb, 2),
            "Used (GB)": round(used / gb, 2),
            "Free (GB)": round(free / gb, 2),
            "Used (%)": round((used / total) * 100, 1)
        }

    @staticmethod
    def print_report():
        print("=" * 45)
        print("         💻 SYSTEM HEALTH MONITOR REPORT")
        print("=" * 45)
        
        info = SystemMonitor.get_system_info()
        print("\n--- System Specifications ---")
        for key, val in info.items():
            print(f"  {key:<18}: {val}")

        disk = SystemMonitor.get_disk_usage()
        print("\n--- Disk Storage Statistics ---")
        for key, val in disk.items():
            print(f"  {key:<18}: {val}")
        
        print("\n" + "=" * 45)

if __name__ == "__main__":
    SystemMonitor.print_report()
