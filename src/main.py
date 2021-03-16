## All of my prefered apps and programs
## that i would need when setting up a new system.
from concurrent.futures import ThreadPoolExecutor # for speed
import threading # get thread ID
import platform  # for OS name check
import UPL       # My tool kit

## check UPL.Core.upl_web class
def downloadStuff(data):
    url         = data["url"]
    filename    = data["outname"]
    extension   = data["type"]
    UPL.Core.upl_web.download_url(url=url, outname=filename, outType=extension)
    print(f"{filename}.{extension} has downloaded correctly")

def call_program(program):
    print(f"Trying to install {program} on thread {threading.current_thread()}")
    UPL.Core.system_tools.call_windows_executable(program, None)

def loop_startup(logger):
    tmp_dir = f"{UPL.Core.currentDir()}"
    items   = UPL.Core.scan_dir(tmp_dir, True)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in items:
            if i.endswith(".exe"):
                logger.add_log(logType="INFO", LogData=f"Running {i}")
                try:
                    executor.submit(call_program, (i))

                except Exception as e:
                    logger.add_log(logType="ERROR", LogData=e)
                    logger.end_logger()
                    raise e


def main(json_data):
    runtime_id   = UPL.Core.generate_uuid() # just for logging

    ## Logging
    UPL_LOGGER   = UPL.upl_logger.logger(log_file=f"{runtime_id}.log")
    UPL_LOGGER.start_logger()    
    

    with ThreadPoolExecutor(max_workers=10) as executor:
        ## loop for downloads
        for item in json_data.keys():
            print(f"Downloading {item}")
            UPL_LOGGER.add_log(logType="INFO", LogData=f"Downloading {item} from {json_data[item]['url']}")

            try:
                executor.submit(downloadStuff, (json_data[item]))

            except Exception as e:
                UPL_LOGGER.add_log(logType="ERROR", LogData=str(e))
                UPL_LOGGER.end_logger()
                raise UPL.upl_errors.download_exception(e)
    
    ## passing logger
    loop_startup(UPL_LOGGER)

    UPL_LOGGER.end_logger()
    

if __name__ == "__main__":
    json_File = UPL.Core.ainput(prompt="JSON File> ", outType=str, ending=".json")
    json_data = UPL.Core.file_manager.getData_json(json_File)

    system_os = platform.system()
    if system_os in json_data.keys():
        main(json_data[system_os])

    else:
        raise Exception("OS Not found")