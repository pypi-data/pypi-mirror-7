from marionette import Marionette
import mozdevice

import json
from optparse import OptionParser
import os
import pkg_resources
import sys
from zipfile import ZipFile

APP_TYPES = ["certified", "web", "privileged"]

def cli():
    parser = OptionParser(usage="usage: %prog [options] app_name " \
                                "permission_file", description="app_name "\
                                "is the name of the app you want to generate " \
                                "and permission_file is the path to the " \
                                "details file.")
    # TODO: take in device serial and marionette port, though likely won't be useful
    parser.add_option("--adb-path", dest="adb_path",
                        help="path to adb executable. If not passed, we assume"\
                        " that 'adb' is on the path")
    parser.add_option("--app-path", dest="app_path",
                        help="If passed, the app's zip file will be stored at" \
                        " the given filepath. Otherwise, it will be in the"\
                        " current working directory as app.zip")
    parser.add_option("--uninstall", dest="uninstall", default=False,
                        action="store_true", help="If passed, we will uninstall " \
                        " the app if it was already installed")
    parser.add_option("--install", dest="install", default=False,
                        action="store_true", help="If passed, the app will be" \
                        " installed on your phone")
    parser.add_option("--type", dest="type", default="certified",
                        help="Application type, either 'certified'," \
                        " 'privileged' or 'web'. Defaults to 'certified'")
    parser.add_option("--version", dest="version", default="1.3",
                        help="FxOS version. Defaults to 1.3")
    parser.add_option("--all-permissions", dest="all_perm", default=False,
                        action="store_true",
                        help="If this is passed, all permissions will be" \
                             " given to the app, ignoring any permission in" \
                             " the details file")
    (options, args) = parser.parse_args()
    if (options.all_perm and len(args) not in [1,2]) or \
        (not options.all_perm and len(args) != 2):
        print "Please pass in the app_name and details_file"
        print "or just app_name if --all-permissions option is used"
        print "Run with --help for more information"
        sys.exit(1)

    app_name = args[0]
    details = None
    details_file = None
    if len(args) == 2:
        details_file = args[1]
    generate_app(app_name, details_file=details_file,
                 uninstall=options.uninstall,
                 install=options.install,
                 app_type=options.type,
                 version=options.version,
                 adb_path=options.adb_path,
                 app_path=options.app_path,
                 all_perm=options.all_perm)
    print "Done."


def generate_app(app_name, details_file=None, uninstall=False, install=False,
                 app_type="certified", version="1.3", adb_path=None,
                 app_path=None, all_perm=False):
    """
    Generates the app and optionally installs it.

    :param app_name: name of the app
    :param details_file: the path to the json file holding the permissions/details
    :param uninstall: Optional, if passed as True, we uninstall the app if it was
                    previously installed
    :param install: Optional, if passed as True, we will install the app
    :param app_type: Optional, type of app. Either "hosted", "certified" or 
                    "privilged". Default is "certified"
    :param version: Optional, the b2g version. Default is "1.3"
    :param adb_path: Optional, path to adb executable. By default, we assume
                    'adb' is on the path.
    :param app_path: Optional, if passed, the app's zip file will be
                     stored at the given location. By default, we will put
                     it in the current working dirctory as 'app.zip'
    :param all_perm: Optional, if passed, gives the app all permissions.
                     By default this is false. 
    """
    details = create_details(version, details_file, all_perm)
    manifest = create_manifest(app_name, details, app_type,
                               version)

    #TODO : ask for workingdir for temp files
    #Creating the application's zip file
    app_path = package_app(manifest, app_path)

    if uninstall:
        print "Uninstalling app"
        uninstall_app(app_name, adb_path)
    if install:
        print "Generating app"
        install_app(app_name, app_path, adb_path)


def create_details(version, details_file=None, all_perms=None):
    """
    You need to pass in either a details_file, or all_perms=True,
    or all_perms=True and a details_file
    """
    details = None
    if all_perms:
        perms = None
        all_perms_file = pkg_resources.resource_filename(__name__,
                                                os.path.sep.join(
                                                ["resources",
                                                 "%s" % version,
                                                 "complete_permissions.json"
                                                 ]))
        with open(all_perms_file, "r") as f:
            perms = json.load(f)
        if details_file:
            #User has provided us with a details_file
            with open(details_file, "r") as f:
                details = json.load(f)
            details["permissions"] = perms["permissions"]
        else:
            details = perms
    else:
        with open(details_file, "r") as f:
            details = json.load(f)
    return details


def create_manifest(app_name, details, app_type, version):
    manifest = None
    manifest_path = "%s/manifest.webapp" % version
    manifest_path = pkg_resources.resource_filename(__name__,
                                                    os.path.sep.join(
                                                    ["resources",
                                                    manifest_path]))
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    manifest["name"] = app_name
    app_type = app_type.lower()
    if app_type not in APP_TYPES:
        raise Exception("Need to pass in one of the following app types: %s" % 
                  APP_TYPES)
        sys.exit(1)
    manifest["type"] = app_type
    if "description" in details:
        manifest["description"] = details["description"]
    manifest["permissions"] = details["permissions"]

    # Check if user provided messages
    if "messages" in details:
        manifest["messages"] = details["messages"]
    else:
        launch_path = manifest["launch_path"]
        all_messages = None
        messages_path = "%s/messages.json" % (version)
        messages_path = pkg_resources.resource_filename(__name__,
                                                        os.path.sep.join(
                                                        ["resources",
                                                          messages_path]))

        with open(messages_path, "r") as f:
            all_messages = json.load(f)

        def add_messages(messages, manifest):
            for message in messages:
                manifest["messages"].append({message: launch_path})

        # Add general messages for the default case
        add_messages(all_messages["general"], manifest)

        for permission in manifest["permissions"]:
            if permission in all_messages:
                related_messages = all_messages[permission]
                # If we have a dictionary, then we should apply the messages if
                # we have the appropriate access level
                if type(related_messages) is dict:
                    level = manifest["permissions"][permission]["access"]
                    for key in related_messages:
                        # use "in" to allow us to use "read" key on both 
                        # "readwrite", "readonly" and "read".
                        if key in level:
                            messages = related_messages[key]
                            add_messages(messages, manifest)
                            break
                else:
                    add_messages(related_messages, manifest)
                
    if "datastores-access" in details:
        manifest["datastores-access"] = details["datastores-access"]
    if "datastores-owned" in details:
        manifest["datastores-owned"] = details["datastores-owned"]

    return manifest


def package_app(manifest, path):
    # create the manifest.webapp file
    manifest_path = os.path.sep.join([os.getcwd(), "manifest.webapp"])
    manifest_file = open(manifest_path, "w")
    manifest_file.write(json.dumps(manifest, 
                        indent=4, separators=(",", ": ")))
    manifest_file.close()

    index_html = pkg_resources.resource_filename(__name__,
                                                 os.path.sep.join(
                                                 ["resources",
                                                  "index.html"]))
    # create the app.zip
    app_path = path
    if not app_path:
        app_path = os.path.sep.join([os.getcwd(), "app.zip"])
    with ZipFile(app_path, "w") as zip_file:
        zip_file.write(index_html, "index.html")
        zip_file.write(manifest_path, "manifest.webapp")
    os.remove(manifest_path)

    return app_path


def uninstall_app(app_name, adb_path=None, script_timeout=5000):
    dm = None
    if adb_path:
        dm = mozdevice.DeviceManagerADB(adbPath=adb_path)
    else:
        dm = mozdevice.DeviceManagerADB()

    installed_app_name = app_name.lower()
    installed_app_name = installed_app_name.replace(" ", "-")
    ret = dm.forward("tcp:2828", "tcp:2828")
    if ret != 0:
        raise Exception("Can't use localhost:2828 for port forwarding." \
                    "Is something else using port 2828?")

    m = Marionette()
    m.start_session()
    uninstall_app = """
    var uninstallWithName = function(name) {
        let apps = window.wrappedJSObject.applications || window.wrappedJSObject.Applications;
        let installedApps = apps.installedApps;
        for (let manifestURL in installedApps) {
          let app = installedApps[manifestURL];
          let origin = null;
          let entryPoints = app.manifest.entry_points;
          if (entryPoints) {
            for (let ep in entryPoints) {
              let currentEntryPoint = entryPoints[ep];
              let appName = currentEntryPoint.name;
              if (name == appName.toLowerCase()) {
                window.wrappedJSObject.navigator.mozApps.mgmt.uninstall(app);
                return true;
              }
            }
          } else {
            let appName = app.manifest.name;
            if (name == appName.toLowerCase()) {
              window.wrappedJSObject.navigator.mozApps.mgmt.uninstall(app);
              return true;
            }
          }
        }
      };
    return uninstallWithName("%s");
    """
    m.set_script_timeout(script_timeout)
    m.execute_script(uninstall_app % app_name.lower())
    m.delete_session()


def install_app(app_name, app_path, adb_path=None, script_timeout=5000):
    dm = None
    if adb_path:
        dm = mozdevice.DeviceManagerADB(adbPath=adb_path)
    else:
        dm = mozdevice.DeviceManagerADB()

    #TODO: replace with app name
    installed_app_name = app_name.lower()
    installed_app_name = installed_app_name.replace(" ", "-")
    if dm.dirExists("/data/local/webapps/%s" % installed_app_name):
        raise Exception("%s is already installed" % app_name)
        sys.exit(1)
    app_zip = os.path.basename(app_path)
    dm.pushFile("%s" % app_path, "/data/local/%s" % app_zip)
    # forward the marionette port
    ret = dm.forward("tcp:2828", "tcp:2828")
    if ret != 0:
        raise Exception("Can't use localhost:2828 for port forwarding." \
                        "Is something else using port 2828?")

    # install the app
    install_js = pkg_resources.resource_filename(__name__,
                                                 os.path.sep.join([
                                                   'app_install.js']))
    f = open(install_js, "r")
    script = f.read()
    f.close()
    script = script.replace("YOURAPPID", installed_app_name)
    script = script.replace("YOURAPPZIP", app_zip)
    m = Marionette()
    m.start_session()
    m.set_context("chrome")
    m.set_script_timeout(script_timeout)
    m.execute_async_script(script)
    m.delete_session()


if __name__ == "__main__":
    cli()
