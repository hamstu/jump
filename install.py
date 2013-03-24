#!/usr/bin/env python

######################################################
#
# jump
# Makes your `cd`ing fast and fun.
#
# This script installs `jump` from:
#   https://github.com/hamstu/jump
#
# See the README for installation instructions
#
######################################################

import os
import sys
import subprocess

config = {
    "orig": os.getcwd(),
    "temp": os.path.join(os.getcwd(), ".jumpinstall"),
    "bash": "%s/.bash_profile" % os.path.expanduser("~"),
    "bin": "/usr/bin",

    "urwid": {
        "name": "urwid-1.1.1",
        "download": "http://excess.org/urwid/urwid-1.1.1.tar.gz"
    },
    "files": {
        "py": "https://raw.github.com/hamstu/jump/master/jump/jump.py",
        "sh": "https://raw.github.com/hamstu/jump/master/jump/jump.sh"
    }
}


def cleanup():
    os.chdir(config['orig'])
    os.system("rm -rf %s" % config['temp'])


def abort(msg):
    cleanup()
    print "\n----- INSTALL ABORTED ----- \n%s \n" % msg
    sys.exit()


def main(args):
    if "uninstall" in args:
        # TODO: Write uninstall routine
        print "Uninstall coming soon. In the meantime, you'll want to reverse the install instructions in the README."
        print "See https://github.com/hamstu/jump/"
        return

    else:
        # Install
        print "===== Installing jump... ===== "
        print

        # Make sure it is not already installed (or something else with the same name)
        proc = subprocess.Popen(["which jump.sh"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if out != "":
            print "It looks like you already have jump installed!"
            do = raw_input("Do you want to continue anyway? [y/n]")
            if not "y" in do:
                abort("Cancelled install.")

        # 0: Store everything in a temp folder
        ret = os.system("mkdir %s &> /dev/null" % config['temp'])
        if ret != 0:
            abort("Could not create temporary directory %s" % config['temp'])
        os.chdir(config['temp'])

        # 1: Check Dependencies
        print "1. Checking dependencies..."
        try:
            import urwid
            print "   urwid version %s found!" % urwid.__version__
        except ImportError:
            print
            print "The Python library `urwid` was not found."
            do = raw_input("Would you like to install it now? [y/n] ")

            if "y" in do:
                print
                print " ----- Fetching urwid..."
                print
                ret = os.system("curl -OL %s" % config['urwid']['download'])
                if (ret != 0):
                    abort("Could not download urwid")
                print

                print " ----- Expanding archive..."
                filename = os.path.basename(config['urwid']['download'])
                ret = os.system("tar xvfz %s" % filename)
                if (ret != 0):
                    abort("Could not untar %s" % filename)
                print

                print " ----- Running `python setup.py install`..."
                print
                print "Note: In order to install properly, you must grant this"
                print "command permission to write to Python's site-packages/ dir"
                print "by entering your password. If you're not comfortable doing"
                print "this, then you may want to install urwid manually."
                print
                os.chdir(config['urwid']['name'])
                ret = os.system("sudo python setup.py install")
                if (ret != 0):
                    abort("Could not install urwid %s" % filename)
                print
                print " ----- urwid install complete!"

            else:
                abort("urwid not installed...")

        # 2. Download the files from GitHub
        print "\n2. Downloading files..."
        for key in config['files']:
            ret = os.system("curl -s -OL %s" % config['files'][key])
            if (ret != 0):
                abort("Could not download %s" % config['files'][key])
            print "   %s [DONE]" % config['files'][key]

        # 3. chmod +x our files so they can run
        print "\n3. Setting executable permissions..."
        for key in config['files']:
            filename = os.path.basename(config['files'][key])
            ret = os.system("chmod +x %s" % filename)
            if (ret != 0):
                abort("Could not set permission on %s" % filename)
            print "   %s [DONE]" % filename

        # 4. Move our files to the /usr/bin folder
        print "\n4. Moving files into system PATH..."

        print "\n   NOTE: In order to find and run jump, the executables must be copied"
        print "   to a folder in your system's PATH. Press ENTER below for the default."
        print "   (This will require you to enter your password)"

        new = raw_input("\n   Where should they be installed? [%s] " % config['bin'])
        if new.strip() != "":
            config['bin'] = new.strip()

        for key in config['files']:
            filename = os.path.basename(config['files'][key])
            ret = os.system("sudo cp %s %s" % (filename, config['bin']))
            if (ret != 0):
                abort("   Could not move files to path '%s'" % config['bin'])
            print "   %s [INSTALLED]" % filename

        # 4.5 Check to make sure the path is in the environ
        system_path = os.environ['PATH'].split(":")
        addpath = False
        if not config['bin'] in system_path:
            print "\n   NOTE: Unable to locate %s in your system's $PATH" % config['bin']
            addpath = raw_input("   Would you like me to add it for you? [y/n] ")
            if "y" in addpath:
                addpath = True

        # 5. Add the alias to the .bash_profile
        print "\n5. Updating shell startup script..."
        new = raw_input("\n   Which file should we use? [%s] " % config['bash'])
        if new.strip() != "":
            config['bash'] = new.strip()

        # Create alias line to add to shell start file...
        lines_to_add = ["\n\n# JUMP: Begin"]
        lines_to_add.append("\nalias j='. jump.sh'")
        if addpath:
            lines_to_add.append("\nexport PATH=$PATH:%s" % config['bin'])
        lines_to_add.append("\n# JUMP: End")

        # Check for existing lines...
        found = False
        bashfile = open(config['bash'], "r")
        bashlines = bashfile.readlines()
        for line in bashlines:
            if line.find("alias j='") > -1:
                found = True

        # Add and write lines to file if present
        if not found:
            bashlines = bashlines + lines_to_add
            bashfile = open(config['bash'], "w")
            bashfile.writelines(bashlines)

        bashfile.close()

        print "\n\n===== Install Completed! ====="
        print "\nNow restart your terminal/shell and run the `j` command"

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        abort("Installation cancelled. Goodbye.")
    finally:
        cleanup()
