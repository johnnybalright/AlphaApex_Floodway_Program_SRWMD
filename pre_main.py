#!/home/jpournelle/anaconda3/envs/g39/bin/python3
import os
import os.path
from dotenv import load_dotenv
load_dotenv(
    "/home/jpournelle/python_projects/" \
        + "plabz/river_division/main/main.env"
    )
import requests
import time
import subprocess
from datetime import datetime
import glob
import shutil
import sqlite3


def log_message(message, file_path):
    with open(file_path, 'a') as f:
        f.write(f"{datetime.now()}: {message}\n")


def process_db_file(python_script, db_file, log_file, pid):
    try:
        log_message(f"------------------------------------------", log_file)
        log_message(f"------------------------------------------", log_file)
        log_message(f"{str(datetime.now())}", log_file)
        log_message(f"Processing {db_file}", log_file)
        log_message(f"Python3 script initiated", log_file)
        python_3 = "/home/jpournelle/anaconda3/envs/g39/bin/python3"
        command = f"{python_3} {python_script} {db_file} {pid}"
        try:
            with open(log_file, "a") as log_output:
                proc = subprocess.Popen(
                    ["/bin/bash", "-c", command],
                    stdout=log_output,
                    stderr=subprocess.STDOUT
                )
                proc.wait(timeout=1200)
        except subprocess.TimeoutExpired:
            log_message("Subprocess timed out.", log_file)
            script_path = os.path.realpath(__file__)
            source_dir = os.path.dirname(script_path)
            tmp_dir = os.path.join(source_dir, "tmp")
            lock = os.path.join(tmp_dir, "lock.txt")
            bound_coords = os.path.join(tmp_dir, "bound_coords.txt")
            xml_links = os.path.join(tmp_dir, "xml_links.txt")
            pid_dir = os.path.join(source_dir, "*pid")
            pid_dir_path = [d for d in glob.glob(pid_dir) if os.path.isdir(d)]
            if os.path.exists(db_file):
                os.remove(db_file)
            if os.path.exists(lock):
                os.remove(lock)
            if os.path.exists(bound_coords):
                os.remove(bound_coords)
            if os.path.exists(xml_links):
                os.remove(xml_links)
            if os.path.exists(pid_dir_path):
                shutil.rmtree(pid_dir_path)
            proc.terminate()
            with sqlite3.connect(str(db_file)) as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM project_data;")
                project_number = str(c.fetchone()[0])
                c.execute("SELECT lname FROM project_data;")
                l_name = str(c.fetchone()[0])
            url = os.getenv("SLACK_URL")
            headers = {
                "Content-Type": "application/json",
            }
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data = {
                "text":f"AlphApex Floodway Program timed out at {current_time}. Project" \
                    + f" {l_name}-{project_number} needs to be ran again."
                }
            response = requests.post(url, json=data, headers=headers)
            log_message(response.text, log_file)
        if proc.poll() is None:
            proc.kill()
    except Exception as e:
        log_message(f"Error: {e}", log_file)
        script_path = os.path.realpath(__file__)
        source_dir = os.path.dirname(script_path)
        tmp_dir = os.path.join(source_dir, "tmp")
        lock = os.path.join(tmp_dir, "lock.txt")
        bound_coords = os.path.join(tmp_dir, "bound_coords.txt")
        xml_links = os.path.join(tmp_dir, "xml_links.txt")
        pid_dir = os.path.join(source_dir, "*pid")
        pid_dir_path = [d for d in glob.glob(pid_dir) if os.path.isdir(d)]
        if os.path.exists(db_file):
            os.remove(db_file)
        if os.path.exists(lock):
            os.remove(lock)
        if os.path.exists(bound_coords):
            os.remove(bound_coords)
        if os.path.exists(xml_links):
            os.remove(xml_links)
        if os.path.exists(pid_dir_path):
            shutil.rmtree(pid_dir_path)
        proc.terminate()
        with sqlite3.connect(str(db_file)) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM project_data;")
            project_number = str(c.fetchone()[0])
            c.execute("SELECT lname FROM project_data;")
            l_name = str(c.fetchone()[0])
        url = os.getenv("SLACK_URL")
        headers = {
            "Content-Type": "application/json",
        }
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data = {
            "text":f"AlphApex Floodway Program timed out at {current_time}. Project" \
                + f" {l_name}-{project_number} needs to be ran again."
            }
        response = requests.post(url, json=data, headers=headers)
        log_message(response.text, log_file)


def process_existing_files(tmp_dir, python_script, log_file, pid):
    for file in os.listdir(tmp_dir):
        if file.endswith('.db'):
            full_path = os.path.join(tmp_dir, file)
            process_db_file(python_script, full_path, log_file, pid)


def main(pid):
    script_path = os.path.realpath(__file__)
    source_dir = os.path.dirname(script_path)
    tmp_dir = os.path.join(source_dir, "tmp")
    lock = os.path.join(tmp_dir, "lock.txt")
    bound_coords = os.path.join(tmp_dir, "bound_coords.txt")
    xml_links = os.path.join(tmp_dir, "xml_links.txt")
    pid_dir = os.path.join(source_dir, "*pid")
    pid_dir_path = [d for d in glob.glob(pid_dir) if os.path.isdir(d)]
    if os.path.exists(lock):
            os.remove(lock)
    if os.path.exists(bound_coords):
        os.remove(bound_coords)
    if os.path.exists(xml_links):
        os.remove(xml_links)
    if os.path.exists(pid_dir_path):
        shutil.rmtree(pid_dir_path)
    python_script = os.path.join(source_dir, "main.py")
    log_file = os.path.join(source_dir, "logs", "main.log")
    process_existing_files(tmp_dir, python_script, log_file, pid)
    while True:
        process_existing_files(tmp_dir, python_script, log_file, pid)
        time.sleep(5)

if __name__ == "__main__":
    pid = os.getpid()
    main(pid)
