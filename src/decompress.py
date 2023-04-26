"""
this is a simple script for executing the pcdcomp.exe utility across many
instances of DOSBox (an DOS emulator) to decompress the EDRs. INPUT_ROOT and
OUTPUT_ROOT must be immediate subdirectories of STORAGE_ROOT. INPUT_ROOT
should contain all the EDRs you wish to decompress. The DOSBox executable must
be available in your PATH as `dosbox`. This script will only work on Linux or
MacOS.
"""
from _socket import gethostname
import datetime as dt
from multiprocessing import Semaphore
import time

from fs.osfs import OSFS
import sh

from pathlib import Path


# change this as needed for your environment
STORAGE_ROOT = "/mnt/storage"
DECOMPRESSOR = "pcdcomp.exe"
INPUT_ROOT = "edr_raw"
OUTPUT_ROOT = "edr_dcmp"
LOGFILE = "decompress.log"
storage_fs = OSFS(STORAGE_ROOT)


def stamp() -> str:
    return f"{gethostname()} {dt.datetime.utcnow().isoformat()[:-7]}: "


def dosbox_batch(directory, command, drive_letter="d"):
    return (
        "-c",
        f"mount {drive_letter} {directory}",
        "-c",
        f"{drive_letter}:",
        "-c",
        f"{command}",
        "-c",
        "exit"
    )


def pcdcomp_cmd(target_path):
    pc_target = str(target_path).replace('/', '\\')
    pc_output = "\\".join(
        [OUTPUT_ROOT, *target_path.parts[1:]]
    ).replace("imq", "img")
    return f"{DECOMPRESSOR} {pc_target} {pc_output}"


def release_semaphore(semaphore):
    def release_when_done(*_, **__):
        semaphore.release()
    return release_when_done


def stamplog(message):
    with open(LOGFILE, "a") as stream:
        stream.write(f"{stamp()[-21:-2]},{message}\n")


def prune_process_records(process_records, timeout=15):
    deletions = []
    for ix, record in enumerate(process_records):
        record['duration'] = time.time() - record['start']
        if not record['process'].is_alive():
            try:
                code = record['process'].exit_code
            except sh.SignalException as se:
                code = record['process'].exit_code
            if code == 0:
                stamplog(f"{record['path']},successful,{record['duration']}")
            else:
                stamplog(f"{record['path']},{code},{record['duration']}")
            deletions.append(ix) 
            continue
        if record['duration'] > timeout:
            record['process'].kill()
            stamplog(f"{record['path']},timed out,{record['duration']}")
            deletions.append(ix)
    return [pr for ix, pr in enumerate(process_records) if ix not in deletions] 


if __name__ == '__main__':
    process_records = []
    flag_count = 4
    polling_interval = 0.1
    sem = Semaphore(flag_count)
    for volume_number in reversed(range(1, 63)):
        volume_path = f"vo_10{str(volume_number).zfill(2)}"
        if not Path(STORAGE_ROOT, INPUT_ROOT, volume_path).exists():
            continue
        print(f"*******volume #{volume_number}*******")
        image_paths = tuple(
            map(Path, storage_fs.walk.files(f"{INPUT_ROOT}/{volume_path}", filter=["*.imq"])))
        for image in image_paths:
            output_dir = Path(STORAGE_ROOT, OUTPUT_ROOT, *image.parts[1:-1])
            output_dir.mkdir(parents=True, exist_ok=True)
            if Path(output_dir, image.parts[-1].replace('imq', 'img').upper()).exists():
                continue
            while sem.get_value() == 0:
                process_records = prune_process_records(process_records)
                time.sleep(polling_interval)
            sem.acquire()
            process = sh.dosbox(
                *dosbox_batch(STORAGE_ROOT, pcdcomp_cmd(image)),
                _bg=True,
                _bg_exc=False,
                _done=release_semaphore(sem)
            )
            process_records.append(
                {"process": process, "start": time.time(), "path": str(image)}
            )
            process_records = prune_process_records(process_records)
    process_records = prune_process_records(process_records)
    while sem.get_value() < flag_count:
        process_records = prune_process_records(process_records)
        time.sleep(polling_interval)
