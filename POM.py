import requests
import urllib.parse as parse
import urllib.request as request
import json
from sys import path as sys_path, argv
import os
import zipfile
import shutil
import logging

BASE_URL = "http://pyge.pythonanywhere.com/"
API_URL = BASE_URL + "api/"
logging.basicConfig(format='[%(asctime)s] (%(levelname)s) - %(message)s', level=logging.INFO, datefmt='%Y/%d/%m %H:%M:%S')


def get_site_packages_path():
    logging.info("Locating Python site-packages Directory...")
    site_packages = None

    for p in sys_path:
        if p.lower().replace("\\", "/").endswith("lib/site-packages"):
            site_packages = p
            break

    if site_packages is None:
        raise OSError("Python3 Is Not In Your PATH!")
    site_packages = os.path.join(site_packages, "PyGEObjects")

    if not os.path.isdir(site_packages):
        os.makedirs(site_packages)

    init = os.path.join(site_packages, "__init__.py")

    if not os.path.isfile(init):
        t = open(init, 'w')
        t.close()

    logging.info("Found Python site-packages Directory")
    return site_packages


def get_package_info(package:str, version:str=None):
    logging.info("Checking POM Server For Information On Package {}...".format(package))
    v = {"name": package}
    if version is not None:
        v["version"] = version
    r = requests.get(API_URL + "pom?" + parse.urlencode(v))
    logging.info("Finished Checking POM Server For Information On Package {}".format(package))
    return dict(json.loads(r.text))


def read_package_info(package:str, path:str=None):
    logging.info("Reading .info File For Package {}".format(package))
    if path is None:
        path = get_site_packages_path()
    logging.info("Finished Reading .info File For Package {}".format(package))
    return dict(json.load(open(os.path.join(path, package, package + ".info"))))


def install(package:str, version:str=None, path:str=None):
    """
    Installs The Specified Package At The Specified Version
    
    POM install [package] (version)
        package - the name of the package to install
        version - the version number of the package to install (default is latest version)
    """
    v = version
    if v is None:
        v = "Latest"
    logging.info("Installing Package {} - Version: {}...".format(package, v))

    if path is None:
        path = get_site_packages_path()
    data = get_package_info(package, version)
    dst = os.path.join(path, data["name"])
    filename = data["name"] + ".zip"

    if os.path.isdir(dst):
        raise IOError("The Package You Have Attempted To Install Is Already Installed. Use 'update' To Check For Package Updates")

    logging.info("Downloading Package Data From PyGE Server...")
    request.urlretrieve(data["url"], os.path.join(path, filename))
    logging.info("Finished Downloading Package Data From PyGE Server")

    logging.info("Extracting Downloaded Package Data...")
    with zipfile.ZipFile(os.path.join(path, filename), 'r') as zip_ref:
        zip_ref.extractall(path)
        d = zip_ref.filelist[0].filename.replace("\\", "").replace("/", "")        # type: str
    logging.info("Finished Extracting Downloaded Package Data")

    logging.info("Cleaning Up Extra Package Files...")
    os.rename(os.path.join(path, d), dst)
    json.dump(data, open(os.path.join(dst, package + ".info"), 'w'))
    os.remove(os.path.join(path, filename))
    logging.info("Finished Cleaning Up Extra Package Files")
    logging.info("Finished Installing Package {} - Version: {}".format(package, v))


def uninstall(package:str, path:str=None):
    """
    Removes The Specified Package

    POM uninstall [package]
        package - the name of the package to uninstall
    """
    logging.info("Uninstalling Package {}...".format(package))
    if path is None:
        path = get_site_packages_path()
    dst = os.path.join(path, package)

    if not os.path.isdir(dst):
        raise IOError("The Package You Have Attempted To Install Is Not Installed On Your Machine. Use 'install' To Install Packages")

    shutil.rmtree(dst)
    logging.info("Finished Uninstalling Package {}".format(package))


def query(package:str, path:str=None):
    """
    Returns The Version Number Of The Specified Package

    POM query [package]
        package - the name of the package to query
    """
    data = read_package_info(package, path)
    logging.info("{0} - v{1}".format(data["name"], data['version']))

def export_packages(output:str, path:str=None):
    """
    Writes Each Package And Version To A File With .PROPERTIES format (package=version)

    POM export [filename]
        filename - the name of the file to export to
    """
    logging.info("Exporting Package List To '{}'...".format(output))
    if path is None:
        path = get_site_packages_path()
    out = open(output, 'w')
    for d in os.listdir(path):
        p = os.path.join(path, d)
        if os.path.isdir(p):
            data = read_package_info(d, path)
            out.write("{}={}".format(data["name"], data["version"]))
    out.close()
    logging.info("Finished Exporting Package List To '{}'".format(output))


def import_packages(filename:str, path:str=None):
    """
    Installs Each Packages At The Specified Version From A .PROPERTIES formatted File (package=version)

    POM import [filename]
        filename - the name of the file to import from
    """
    logging.info("Importing Package List From '{}'...".format(filename))
    if path is None:
        path = get_site_packages_path()

    i = 1
    packages = open(filename, 'r').readlines()
    for p in packages:
        package, version = p.split("=")
        logging.info("Installing Package {} ({} of {})...".format(package, i, len(packages)))
        install(package, version, path)
        i += 1
    logging.info("Finished Importing Package List From '{}'".format(filename))


def update(package:str, path:str=None):
    """
    Checks For And Installs Updates For The Specified Package

    POM update [package]
        package - the name of the package to update
    """
    logging.info("Checking For Updates On Package {}".format(package))

    if path is None:
        path = get_site_packages_path()
    current = read_package_info(package, path)
    new = get_package_info(package)

    if current["version"] != new["version"]:
        logging.info("Updating Package {} From v{} To v{}...".format(package, current["version"], new["version"]))
        uninstall(package, path)
        install(package, None, path)
        logging.info("Finished Updating Package {} From v{} To v{}".format(package, current["version"], new["version"]))
    else:
        logging.info("No Updates Found For Package {}".format(package))


def help_util():
    """
    Displays Information On Each Command

    POM help
    """
    for cmd, f in COMMANDS.items():
        print("POM " + cmd + ":")
        print(f.__doc__.lstrip("\n"))

def interpret_command(cmd):
    if cmd == "":
        return
    if type(cmd) is str:
        cmd = cmd.split(" ")

    root = cmd[0]
    if root not in COMMANDS:
        logging.error("Unknown Command. Use 'help' For A List Of Commands")
        quit(-1)
    COMMANDS[root](*cmd[1:])

def console():
    """
    Runs POM As An Interactive Console Application

    POM console
    """
    while True:
        interpret_command(input("POM> "))

COMMANDS = {
    "install": install,
    "uninstall": uninstall,
    "query": query,
    "import": import_packages,
    "export": export_packages,
    "update": update,
    "help": help_util,
    # "console": console
}

if __name__ == '__main__':
    interpret_command(argv[1:])
