#!/usr/bin/env python3
Import("env")

import shutil
import sys
from colors import *
import os
from pathlib import Path
from ntpath import basename
from zipfile import ZipFile
import json
from shutil import copyfile, make_archive

def _build_manifest_json(env, partitions):
    archive_outputs = {}
    
    parts = []

    name = "OpenIris"
    version = env["PROGNAME"].split("-")[1]
    new_install_prompt_erase = True

    print("Creating manifest.json")

    temp = []
    for [offset, path] in partitions:
        # join the offset and path into a space separated string
        temp.append("{} {}".format(offset, path))

    # detect if the PIOENV has QIO flash mode
    flash_mode = env["BOARD_FLASH_MODE"]

    flash_freq = env["BOARD_F_FLASH"]

    if flash_freq == "80000000L":
        flash_freq = "80m"
    elif flash_freq == "40000000L":
        flash_freq = "40m"

    # detect the chip type
    chip_type = env["BOARD_MCU"]

    if chip_type == "esp32":
        flash_size = '4'
    elif chip_type == "esp32s2":
        flash_size = '2'
    elif chip_type == "esp32c3":
        flash_size = '2'
    elif chip_type == "esp32s3":
        flash_size = '8'


    if chip_type == "esp32c3" or chip_type == "esp32s3" or chip_type == "esp32s2":
        chip_type = chip_type.replace("esp32", "esp32-")

    # capitalize the chip type
    chip_type = chip_type.upper()

    sys.stdout.write(BLUE)
    print("Flash Mode: %s" % flash_mode)
    print("Chip Type: %s" % chip_type)
    print("Flash Frequency: %s" % flash_freq)
    print("Flash Size: %s" % flash_size)

    """
    python esptool.py --chip ESP32 merge_bin -o merged-firmware.bin --flash_mode dio --flash_freq 40m --flash_size 4MB
    0x1000 bootloader.bin 0x8000 partitions.bin 0xe000 boot.bin 0x10000 OpenIris-v1.3.0-esp32AIThinker-8229a3a-master.bin
    """
    execute_cmd = "$PYTHONEXE $PROJECT_PACKAGES_DIR/tool-esptoolpy/esptool.py --chip {chip} merge_bin -o merged-firmware.bin --flash_mode {flash_mode} --flash_freq {flash_freq} --flash_size {flash_size}MB %s" % (
        " ".join(temp)
    )

    print("Executing: %s" % execute_cmd)

    sys.stdout.write(RESET)

    env.Execute(
        execute_cmd.format(
            chip=chip_type, flash_mode=flash_mode, flash_freq=flash_freq, flash_size=flash_size)
    )

    filename = basename("merged-firmware.bin")
    # archive.write("merged-firmware.bin", filename)
    archive_outputs["merged-firmware.bin"] = filename
    
    partition = {
        "path": filename,
        "offset": 0,
    }
    parts.append(partition)

    manifest = {
        "name": name,
        "version": version,
        "new_install_prompt_erase": new_install_prompt_erase,
        "builds": [
            {
                "chipFamily": chip_type,
                "parts": parts,
            }
        ],
    }
    # archive.writestr("manifest.json", json.dumps(manifest))
    archive_outputs["manifest.json"] = json.dumps(manifest)
    sys.stdout.write(RESET)
    return archive_outputs

def createZip(source, target, env):
    if os.getenv("OPENIRIS_CI_BUILD", False):
        if (not sys.platform.lower().startswith(("ubuntu", "linux"))):
            sys.stdout.write(BLUE)
            print("WARNING: createzip.py: Not running on Linux, used to skip zip creation, but not it will continue carefully.")
            sys.stdout.write(RESET)
        
        sys.stdout.write(GREEN)
        print("Program has been built, creating zip archive!")
        program_path = target[0].get_abspath()

        array_args = [env["FLASH_EXTRA_IMAGES"]]

        for offset, image in env["FLASH_EXTRA_IMAGES"]:
            print("\nImage: %s" % str(image))
            array_args.extend([str(offset), str(image)])

        array_args.append(env["ESP32_APP_OFFSET"])
        array_args.append(program_path)

        n = 2
        partitions_arg = array_args[1:]
        sys.stdout.write(CYAN)
        print(f"partitions_args: {partitions_arg}")
        partitions = final = [
            partitions_arg[i * n : (i + 1) * n]
            for i in range((len(partitions_arg) + n - 1) // n)
        ]
        print(f"partitions: {partitions}")
        # file_name = "./build/{0}/{1}.zip".format(
        file_name = "{0}/{1}.zip".format(
            str(env["PIOENV"]), env["PROGNAME"]
        )
        _out_zip_parent_path = Path(r"C:\Users\pho\repos\ExternalTesting\OpenIris\ESP\build")
        assert _out_zip_parent_path.exists()
        print(f"_out_zip_parent_path: '{_out_zip_parent_path}'\nfile_name: '{file_name}'")
        zip_file_path = _out_zip_parent_path.joinpath(file_name).resolve()
        print(f"zip_file_path: '{zip_file_path.as_posix()}'")
        # ensure that the parent directory exists!
        _immediate_parent_directory = zip_file_path.parent.resolve()
        if _immediate_parent_directory.is_dir():
            print(f'creating parent dir: "{_immediate_parent_directory.as_posix()}" because it did not exist.')
            _immediate_parent_directory.mkdir(parents=True, exist_ok=True) # create the parent directory if needed

        print(f'building manifest...\n')
        # print("Creating manifest.json")
        archive_folder = zip_file_path.with_suffix('') # no suffix
        
        print('\nCreating archive_folder "' + archive_folder.as_posix() + '"', end="\n")
        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)
        
        # with ZipFile(zip_file_path, "w") as archive:
        #     print('\nCreating "' + archive.filename + '"', end="\n")
        #     parts = []

        #     name = "OpenIris"
        #     version = env["PROGNAME"].split("-")[1]
        #     new_install_prompt_erase = True

        #     print("Creating manifest.json")

        #     temp = []
        #     for [offset, path] in partitions:
        #         # join the offset and path into a space separated string
        #         temp.append("{} {}".format(offset, path))

        #     # detect if the PIOENV has QIO flash mode
        #     flash_mode = env["BOARD_FLASH_MODE"]

        #     flash_freq = env["BOARD_F_FLASH"]

        #     if flash_freq == "80000000L":
        #         flash_freq = "80m"
        #     elif flash_freq == "40000000L":
        #         flash_freq = "40m"

        #     # detect the chip type
        #     chip_type = env["BOARD_MCU"]

        #     if chip_type == "esp32":
        #         flash_size = '4'
        #     elif chip_type == "esp32s2":
        #         flash_size = '2'
        #     elif chip_type == "esp32c3":
        #         flash_size = '2'
        #     elif chip_type == "esp32s3":
        #         flash_size = '8'


        #     if chip_type == "esp32c3" or chip_type == "esp32s3" or chip_type == "esp32s2":
        #         chip_type = chip_type.replace("esp32", "esp32-")

        #     # capitalize the chip type
        #     chip_type = chip_type.upper()

        #     sys.stdout.write(BLUE)
        #     print("Flash Mode: %s" % flash_mode)
        #     print("Chip Type: %s" % chip_type)
        #     print("Flash Frequency: %s" % flash_freq)
        #     print("Flash Size: %s" % flash_size)

        #     """
        #     python esptool.py --chip ESP32 merge_bin -o merged-firmware.bin --flash_mode dio --flash_freq 40m --flash_size 4MB
        #     0x1000 bootloader.bin 0x8000 partitions.bin 0xe000 boot.bin 0x10000 OpenIris-v1.3.0-esp32AIThinker-8229a3a-master.bin
        #     """
        #     execute_cmd = "$PYTHONEXE $PROJECT_PACKAGES_DIR/tool-esptoolpy/esptool.py --chip {chip} merge_bin -o merged-firmware.bin --flash_mode {flash_mode} --flash_freq {flash_freq} --flash_size {flash_size}MB %s" % (
        #         " ".join(temp)
        #     )

        #     print("Executing: %s" % execute_cmd)

        #     sys.stdout.write(RESET)

        #     env.Execute(
        #         execute_cmd.format(
        #             chip=chip_type, flash_mode=flash_mode, flash_freq=flash_freq, flash_size=flash_size)
        #     )

        #     filename = basename("merged-firmware.bin")
        #     # filename = f"{}/merged-firmware.bin"
        #     archive.write("merged-firmware.bin", filename)

        #     partition = {
        #         "path": filename,
        #         "offset": 0,
        #     }
        #     parts.append(partition)

        #     manifest = {
        #         "name": name,
        #         "version": version,
        #         "new_install_prompt_erase": new_install_prompt_erase,
        #         "builds": [
        #             {
        #                 "chipFamily": chip_type,
        #                 "parts": parts,
        #             }
        #         ],
        #     }
        #     archive.writestr("manifest.json", json.dumps(manifest))
        archive_outputs = _build_manifest_json(env, partitions)
        print(f'archive_outputs: {archive_outputs}')
        
        archive_folder

        _out_merged_firmware_path = Path(archive_outputs["merged-firmware.bin"]).resolve()
        assert _out_merged_firmware_path.exists()
        # copy it
        archive_folder = Path(archive_folder).resolve()
        archive_folder_out_merged_firmware_path = archive_folder.joinpath(_out_merged_firmware_path.name).resolve()
        shutil.copy(_out_merged_firmware_path, archive_folder_out_merged_firmware_path)
        print(f"Copied '{_out_merged_firmware_path.as_posix()}' to '{archive_folder_out_merged_firmware_path.as_posix()}'")        

        
        manifest_txt_path = archive_folder.joinpath("manifest.json").resolve()
        print(f'writing out manifest.json to "{manifest_txt_path.as_posix()}"...')
        manifest_txt_path.write_text(archive_outputs["manifest.json"]) # write to file 
        # archive_outputs["manifest.json"]


        sys.stdout.write(RESET)

    else:
        sys.stdout.write(BLUE)
        print("CI build not detected, skipping zip creation")
        sys.stdout.write(RESET)


env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", createZip)
