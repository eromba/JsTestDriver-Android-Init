#!/usr/bin/python
#
# JsTestDriver / Android Emulator Initialization Script
#
# Automates the initialization of JsTestDriver with an Android emulator,
# capturing the emulator's web browser in the JsTestDriver server instance.
#
# === Dependencies ===
#
#  - Python
#      Tested with versions 2.7.2 and 3.2.2
#      http://www.python.org/
#  - JsTestDriver
#      Tested with version 1.3.3c
#      http://code.google.com/p/js-test-driver/
#  - Android SDK
#      http://developer.android.com/sdk/index.html
#
# === Usage ===
#
#   jtd-android-init.py [Path to JTD] [Port] [Path to SDK] [AVD] [Delay]
#
#  - Path to JTD : The path to your JsTestDriver JAR file
#  - Port        : The port on which to start the JsTestDriver server
#  - Path to SDK : The path to your local Android SDK directory
#  - AVD         : The name of the Android Virtual Device to start
#  - Delay       : The number of seconds to wait for the Android browser to
#                  finish loading the JsTestDriver test page
#
# === Current Limitations ===
#
#  - Does not support capturing the browser of a USB-connected Android device.
#  - Does not support capturing multiple emulator instances.
#


import os
import sys
import subprocess
import time

try:
  import urllib.request
  urlError = urllib.error.URLError
except ImportError:
  import urllib2
  urlError = urllib2.URLError


#
# FUNCTION DEFINITIONS
#

#
# Wrapper around urlopen() for compatibility with Python 2.x
#

def openUrl(url):
  try:
    return urllib.request.urlopen(url)
  except NameError:
    return urllib2.urlopen(url)

#
# Determine if JsTestDriver has captured an Android browser
#

def AndroidBrowserIsCaptured():
  try:
    f = openUrl("http://localhost:" + JTD_PORT)
    output = f.read().decode("utf-8")
    if output.find("Android") == -1:
      return False
    else:
      return True
  except (urlError):
    return False

#
# END OF FUNCTION DEFINITIONS
#


#
# Map command-line arguments to variables
#


if len(sys.argv) != 6:
  print("Usage: jtd-android-init.py [Path to JTD] [Port] [Path to SDK] [AVD] [Delay]")
  exit(1)

JTD_PATH = sys.argv[1]
JTD_PORT = sys.argv[2]
SDK_PATH = sys.argv[3]
AVD_NAME = sys.argv[4]
DELAY = sys.argv[5]

ADB_PATH = os.path.abspath( os.path.join(SDK_PATH, "platform-tools/adb") )
EMULATOR_PATH = os.path.abspath( os.path.join(SDK_PATH, "tools/emulator") )


#
# Start the JsTestDriver server in a new window if it is not already running
#


try:
  print("Detecting JsTestDriver server on port " + JTD_PORT + "...")
  f = openUrl("http://localhost:" + JTD_PORT)
  print("JsTestDriver server already running\n")
  newServerInstance = False
except (urlError):
  print("JsTestDriver not detected\nStarting JsTestDriver server...\n")
  newServerInstance = True
  if os.name == 'nt':
    subprocess.Popen(["cmd", "/c", "start", "java", "-jar", JTD_PATH, "--port", JTD_PORT])
  else:
    subprocess.Popen(["xterm", "-e", "java", "-jar", JTD_PATH, "--port", JTD_PORT])


#
# Launch the given Android emulator if it is not already running
#


print("Detecting Android emulator...")

adbProc = subprocess.Popen([ADB_PATH, "devices"], stdout=subprocess.PIPE)

# subprocess.communicate() returns a list of stdout and stderror as byte strings
output = adbProc.communicate()[0].decode("utf-8")

if output.find("emulator") == -1:

  print("Android emulator not detected")

  # If we are starting a new emulator instance but have an existing server instance,
  # we must restart the server in order to flush any previously-captured browsers.
  if not newServerInstance:
    print("\nPlease close JsTestDriver to flush any existing captured browsers.")
    sys.exit(1)

  print("Starting emulator...\n")
  newEmulatorInstance = True
  emulatorProc = subprocess.Popen([EMULATOR_PATH, "-avd", AVD_NAME])

else:

  print("Emulator already running\n")

  # If the emulator's browser is NOT already captured, we treat this as a new
  # emulator instance.
  print
  if AndroidBrowserIsCaptured():
    print("Android browser already captured")
    newEmulatorInstance = False
  else:
    print("Android browser not yet captured")
    newEmulatorInstance = True

  # If we are starting a new server instance but have an existing emulator
  # instance, we open a blank page in the emulator's browser. This will cause a
  # hard-refresh when we open http://10.0.2.2:.../capture later on, which in
  # turn will cause the new server instance to re-capture the browser.
  if newServerInstance:
    subprocess.call([ADB_PATH, "shell", "am", "start", "-a",\
      "android.intent.action.VIEW", "-d", "about:blank"], stdout=subprocess.PIPE)

  # Press the "Home" button to return to the home screen
  # This prevents the browser's menu from appearing when we try to unlock
  # the screen by pressing the Menu button.
  subprocess.call([ADB_PATH, "shell", "input", "keyevent", "3"])

# Unlock the Android emulator's screen
# Unfortunately, there is no way to detect whether the screen is locked from
# the command line. In any event, we unlock the screen by sending the
# keyevent corresponding to the Menu button once the emulator is initialized.
subprocess.call([ADB_PATH, "wait-for-device", "shell", "input", "keyevent", "82"])


#
# Load the JsTestDriver test page in the emulator
# NOTE: The emulator uses http://10.0.2.2 to refer to the host machine
#


subprocess.call([ADB_PATH, "shell", "am", "start", "-a",\
  "android.intent.action.VIEW", "-d", "http://10.0.2.2:" + JTD_PORT + "/capture"],\
  stdout=subprocess.PIPE)

# Wait until the Android browser is captured (if necessary)
# We check the server's status page every second until it reports that there
# is at least 1 captured Android browser.
if newEmulatorInstance:
  print("Capturing browser...")
  while not AndroidBrowserIsCaptured():
    time.sleep(1)
  print("Browser captured!")

# If the browser is newly-captured, we must wait for the JavaScript on the
# JsTestDriver page to initialize.
if newServerInstance or newEmulatorInstance:
  print("Waiting " + DELAY + " seconds for the browser to finish loading...")
  time.sleep(float(DELAY))

print("\nReady for testing!")

