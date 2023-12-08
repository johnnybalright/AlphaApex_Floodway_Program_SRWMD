import os
from datetime import datetime

def log_message(message, file_path):
    with open(file_path, 'a') as f:
        f.write(f"{datetime.now()}: {message}\n")


script_path = os.path.realpath(__file__)
source_dir = os.path.dirname(script_path)
tmp_dir = os.path.join(source_dir, "tmp")
lock = os.path.join(tmp_dir, "lock.txt")
bound_coords = os.path.join(tmp_dir, "bound_coords.txt")
xml_links = os.path.join(tmp_dir, "xml_links.txt")
pid_dir = os.path.join(source_dir, "*pid")
pid_dir_path = [d for d in glob.glob(pid_dir) if os.path.isdir(d)]
# if os.path.exists(db_file):
#     os.remove(db_file)
# if os.path.exists(lock):
#     os.remove(lock)
if os.path.exists(bound_coords):
    os.remove(bound_coords)
if os.path.exists(xml_links):
    os.remove(xml_links)
if os.path.exists(pid_dir_path):
    shutil.rmtree(pid_dir_path)
log_file = "/home/jpournelle/python_projects/plabz/river_division/" \
    + "main/logs/pre_main_service.log"
if os.path.exists(lock):
    os.remove(lock)
    log_message("lock.txt removed", log_file)
else:
    log_message("lock.txt not found", log_file)
