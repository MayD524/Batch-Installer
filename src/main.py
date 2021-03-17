#!/env/bin python3 
# -*- coding: utf-8 -*-

"""
    Made By       : Ryan Draskovics
    Created On    : 3/16/2021
    Inital Commit : 3/16/2021
    GitHub        : https://github.com/RyanD524/Batch-Installer
"""

## All of my prefered apps and programs
## that i would need when setting up a new system.
from concurrent.futures import ThreadPoolExecutor # for speed
import threading # get thread ID
import platform  # for OS name check
import UPL       # My tool kit

## if you are reading this. HI! :)

## check UPL.Core.upl_web class
def downloadStuff(data):
    url         = data["url"]
    filename    = data["outname"]
    extension   = data["type"]
    UPL.Core.upl_web.download_url(url=url, outname=filename, outType=extension)
    print(f"{filename}.{extension} has downloaded correctly")


## call a program
def call_program(program):
    print(f"Trying to install {program} on thread {threading.current_thread()}")
    UPL.Core.system_tools.call_windows_executable(program, None)

## call the exe files (for windows (linux & mac later))
def loop_startup(logger):
    ## scan current directory
    tmp_dir = f"{UPL.Core.currentDir()}"
    items   = UPL.Core.scan_dir(tmp_dir, True)
    
    ## making new thread pool with 10 threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in items:
            if i.endswith(".exe"):
                logger.add_log(logType="INFO", LogData=f"Running {i}")
                try:
                    ## call a thread if we can
                    executor.submit(call_program, (i))

                ## most likely lack of permission or file not found
                ## ¯\_(ツ)_/¯
                except Exception as e:
                    logger.add_log(logType="ERROR", LogData=e)
                    logger.end_logger()
                    raise e


## takes dict returns None
def main(json_data:dict) -> UPL.void:
    runtime_id   = UPL.Core.generate_uuid() # just for logging

    ## Logging
    UPL_LOGGER   = UPL.upl_logger.logger(log_file=f"{runtime_id}.log")
    UPL_LOGGER.start_logger()    
    
    ## Threading for speed and making life easier
    with ThreadPoolExecutor(max_workers=10) as executor:
        ## loop for downloads
        for item in json_data.keys():
            print(f"Downloading {item}")
            UPL_LOGGER.add_log(logType="INFO", LogData=f"Downloading {item} from {json_data[item]['url']}")

            try:
                ## calling download on a new thread
                executor.submit(downloadStuff, (json_data[item]))

            ## something went wrong oops 
            ##¯\_(ツ)_/¯##
            except Exception as e:
                UPL_LOGGER.add_log(logType="ERROR", LogData=str(e))
                UPL_LOGGER.end_logger()
                raise UPL.upl_errors.download_exception(e)
    
    ## passing logger
    loop_startup(UPL_LOGGER)


    ## end logging
    UPL_LOGGER.end_logger()
    

    ## just cause
    return UPL.void

## start of script
if __name__ == "__main__":
    ## getting the json file data (dict)
    json_File = UPL.Core.ainput(prompt="JSON File> ", outType=str, ending=".json")
    json_data = UPL.Core.file_manager.getData_json(json_File)

    ## getting the current OS
    system_os = platform.system()

    ## check if current OS is handled
    if system_os in json_data.keys():
        main(json_data[system_os])

    ## the json file doesn't have a mode for the current OS
    else:
        raise Exception("Current OS was not found in the provided JSON File")
