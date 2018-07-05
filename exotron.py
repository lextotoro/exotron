# !/usr/bin/python3
__AUTHOR__ = 'Florian Roth'
__VERSION__ = "0.1.0"

import logging
import argparse
import subprocess
import configparser
from pathlib import Path
import traceback
import tkinter
from tkinter.filedialog import askopenfilename
import shutil, os, sys

SW_DOWNLOAD_LINKS = {'7zip':
                         {'link': 'http://www.7-zip.org/download.html',
                          'comment': 'Download the 7Zip command line version or make sure that 7z is in PATH'},
                     '7sfx':
                         {'link': 'http://www.7-zip.org/download.html',
                          'comment': 'Download 7-Zip Extra: 7z Library, SFXs for installers'},
                     'sysmon_exe':
                         {'link': 'https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon',
                          'comment': 'Download Sysmon EXE from the Microsoft Website'},
                     'sysmon_config':
                         {'link': 'https://github.com/SwiftOnSecurity/sysmon-config',
                          'comment': 'Download Sysmon Config from SwiftOnSecurity\'s github repo'},
                     }


class ExoTron(object):

    def createPackage(self):
        """
        Create a SFX package
        :return:
        """
        logging.info("Creating ExoTron Archive ...")
        try:
            command = [str(software['7zip']),
                       'a',
                       'archive.7z',
                       'exotron.bat',
                       'tools',
                       'Sysmon',
                       'samples'
                       ]
            output = runProcess(command)
        except Exception as e:
            if args.debug:
                traceback.print_exc()
            sys.exit(1)

    def writeConfig(self):
        """
        Writes a config file for the SFX archive
        :return:
        """
        configString = ";!@Install@!UTF-8!\n" \
                       "Title=\"Exotron\"\n" \
                       "ExecuteFile=\"exotron.bat\"\n" \
                       "ExecuteParameters=\"XXX\"\n" \
                       ";!@InstallEnd@!\n"
        # Replace the parameters with the ones from the config file
        configStringModified = configString.replace("XXX", config["params"])
        # Write the config file
        with open('config.txt', 'w') as f:
            f.write(configStringModified)

    def createSFX(self):
        """
        Creates a self-extracting and self-executing package
        :return:
        """
        logging.info("Creating SFX ...")
        try:
            sfx_data = bytearray()
            components = [software['7sfx'], 'config.txt', 'archive.7z']
            for c in components:
                with open(c, 'rb') as f:
                    sfx_data.extend(f.read())
            # Write blob
            with open('exotron-package.exe', 'wb') as f:
                f.write(sfx_data)
        except Exception as e:
            if args.debug:
                traceback.print_exc()
            sys.exit(1)


def checkRequirements(required_software):
    """
    Checking the existence of all required tools
    :return:
    """
    for rs in required_software:
        # Check if auxiliary file exists
        if not os.path.exists(required_software[rs]):
            # If not, print a download description
            print("Missing {0} : {1} {2}".format(required_software[rs],
                                                 SW_DOWNLOAD_LINKS[rs]['comment'],
                                                 SW_DOWNLOAD_LINKS[rs]['link']))


def runProcess(command):
    """
    Run a process and check it's output
    :param command:
    :return output:
    """
    output = ""
    returnCode = 0
    if args.debug:
        logging.info("Running command: {0}".format(command))
    try:
        output = subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        if args.debug:
            traceback.print_exc()
    return output


def cleanUp():
    """
    Cleanup previous packages
    :return:
    """
    oldFiles = ["archive.7z", "exotron-package.exe"]
    for file in oldFiles:
        if os.path.exists(file):
            os.remove(file)
def gui():
    if not os.path.exists('samples'):
        os.makedirs('samples')

    top = tkinter.Tk()
    top.title("Submit File")
    top.geometry("150x150")

    def file_chooser():
        file_to_add = askopenfilename()
        shutil.move(file_to_add,'samples')
        print("File added: " + file_to_add)


    def clear_files():
        shutil.rmtree('samples')
        os.makedirs('samples')


    def exotron_call():
        print("RUN EXOTRON")
        top.destroy()

    B = tkinter.Button(top, text="Clear_files", command=clear_files)
    B2 = tkinter.Button(top, text="Choose a file", command=file_chooser)
    B3 = tkinter.Button(top, text="Wrap and submit", command=exotron_call)

    B.place(x=25, y=25)
    B2.place(x=25, y=55)
    B3.place(x=25, y=85)

    top.mainloop()
    return

def submit_file():
    print("Submit to sandbox of choice...")
    
if __name__ == '__main__':

    print("                                    ".ljust(80))
    print("     ____        ______             ".ljust(80))
    print("    / __/_ _____/_  __/______  ___  ".ljust(80))
    print("   / _/ \\ \\ / _ \/ / / __/ _ \\/ _ \\ ".ljust(80))
    print("  /___//_\\_\\\\___/_/ /_/  \\___/_//_/ ".ljust(80))
    print("                                    ".ljust(80))
    print(" ".ljust(80))
    print("  Sandbox Feature Upgrader".ljust(80))
    print(("  " + __AUTHOR__ + " - " + __VERSION__ + "").ljust(80))
    print("                                    ".ljust(80))

    parser = argparse.ArgumentParser(description='ExoTron')
    parser.add_argument('-i', help='Config file', metavar='config-file', default='exotron.cfg')
    parser.add_argument('--debug', action='store_true', default=False, help='Debug output')
    parser.add_argument('--gui', action='store_true', default=False, help='Management gui')
    parser.add_argument('--submit', action='store_true', default=False, help='Submit to sandbox')


    args = parser.parse_args()

    # Logging
    if args.gui:
        gui()
    logLevel = logging.INFO
    if args.debug:
        logLevel = logging.DEBUG
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s",
                                     "%Y-%m-%d %H:%M:%S")
    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logLevel)

    # Read the config file
    configFile = configparser.ConfigParser()
    try:
        configFile.read(args.i)
        software = {}
        config = {}
        # File locations
        software['7zip'] = Path(configFile['LOCATIONS']['7ZIP_LOCATION'])
        software['7sfx'] = Path(configFile['LOCATIONS']['7Z_SFX_HEADER_LOCATION'])
        software['sysmon_exe'] = Path(configFile['LOCATIONS']['SYSMON_EXE'])
        software['sysmon_config'] = Path(configFile['LOCATIONS']['SYSMON_CONFIG'])
        # Params
        config["params"] = configFile['EXE']['PARAMS']
    except Exception as e:
        traceback.print_exc()
        print("[E] Error reading config file '{0}'".format(args.i))
        sys.exit(1)

    # Check the requirements
    checkRequirements(software)
    cleanUp()

    # Exotron
    exo = ExoTron()
    exo.writeConfig()
    exo.createPackage()
    exo.createSFX()

    if args.submit:
        submit_file()
