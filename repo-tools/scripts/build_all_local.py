import os
import subprocess
import sys
from shutil import copyfile, make_archive
from pathlib import Path

# Define the target environments
# targets = ["esp32AIThinker", "esp32M5Stack", "esp32Cam", "esp_eye", "wrover", "wrooms3QIO", "wrooms3QIOUSB", "wrooms3", "wrooms3USB", "xiaosenses3", "xiaosenses3_USB"]
targets = ["xiaosenses3_phoeyeleft", "xiaosenses3_phoeyeright", "xiaosenses3_phoeyew"]

# Set the CI build environment variable
os.environ["OPENIRIS_CI_BUILD"] = "1"

esp_dir = Path(r'C:\Users\pho\repos\ExternalTesting\OpenIris\ESP').resolve() #os.getcwd()
assert esp_dir.exists()

# Create the build directory if it doesn't exist
build_dir = os.path.join(esp_dir, "build")
if not os.path.exists(build_dir):
    os.makedirs(build_dir)

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=esp_dir.as_posix())
    if result.returncode != 0:
        print(f"Command failed with error: {result.stderr}")
        sys.exit(1)
    print(result.stdout)

# Loop through each target and build
for target in targets:
    print(f"Building for environment: {target}")
    run_command(f"pio run --environment {target}")
    print(f"Build for {target} completed.")

    # # Create target directory if it doesn't exist
    # target_dir = os.path.join(build_dir, target)
    # if not os.path.exists(target_dir):
    #     os.makedirs(target_dir)

    # # Locate the firmware binary
    # firmware_bin = os.path.join(esp_dir, ".pio", "build", target, "firmware.bin")
    # if not os.path.exists(firmware_bin):
    #     print(f"No firmware binary found for {target}")
    #     continue

    # # Copy firmware binary to target directory
    # firmware_bin_dst = os.path.join(target_dir, "firmware.bin")
    # copyfile(firmware_bin, firmware_bin_dst)
    # print(f"Copied firmware binary to {firmware_bin_dst}")

    # # Copy firmware_name.txt to the target directory
    # firmware_name_src = os.path.join(esp_dir, "tools", "firmware_name.txt")
    # firmware_name_dst = os.path.join(target_dir, "firmware_name.txt")
    # copyfile(firmware_name_src, firmware_name_dst)
    # print(f"Copied firmware_name.txt to {firmware_name_dst}")

    # # Create a zip archive of the target directory
    # zip_name = os.path.join(build_dir, f"{target}.zip")
    # make_archive(zip_name.replace('.zip', ''), 'zip', target_dir)
    # print(f"Created zip archive {zip_name}.zip")
    

    # # Create zip file for the build
    # target_dir = os.path.join(build_dir, target)
    # zip_files = [f for f in os.listdir(target_dir) if f.endswith(".zip")]
    # if not zip_files:
    #     print(f"No zip files found in {target_dir}")
    #     continue

    # for zip_file in zip_files:
    #     zip_path = os.path.join(target_dir, zip_file)
    #     run_command(f"unzip -l {zip_path}")

    # # Copy firmware_name.txt to the target directory
    # firmware_name_src = os.path.join(esp_dir, "tools", "firmware_name.txt")
    # firmware_name_dst = os.path.join(target_dir, "firmware_name.txt")
    # copyfile(firmware_name_src, firmware_name_dst)
    # print(f"Copied firmware_name.txt to {firmware_name_dst}")
