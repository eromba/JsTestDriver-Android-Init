#!/usr/bin/python
#
# JsTestDriver / Android Emulator Initialization Script
#
# Automates the initialization of JsTestDriver with an Android emulator,
# capturing the emulator's web browser in the JsTestDriver server instance
# and running the tests specified on the command line.
#
# Project Homepage: https://github.com/eromba/JsTestDriver-Android-Init
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


if not len(sys.argv) >= 7:
  print("Usage: jtd-android-init.py [Path to SDK] [AVD] [Delay] [Path to JTD] [JTD Port] [JTD Test] [JTD Args]...")
  exit(1)

SDK_PATH = sys.argv[1]
AVD_NAME = sys.argv[2]
DELAY = sys.argv[3]
JTD_PATH = sys.argv[4]
JTD_PORT = sys.argv[5]
JTD_TEST = sys.argv[6]
ADB_PATH = os.path.abspath( os.path.join(SDK_PATH, "platform-tools/adb") )
EMULATOR_PATH = os.path.abspath( os.path.join(SDK_PATH, "tools/emulator") )


#
# Start the JsTestDriver server
#


try:
  print("Detecting JsTestDriver server on port " + JTD_PORT + "...")
  f = openUrl("http://localhost:" + JTD_PORT)

  # If the server is not running, an exception will be thrown before this code is executed
  print("Server detected")
  print("\nPlease stop the JsTestDriver server to flush any existing captured browsers")
  sys.exit(1)

except (urlError):
  print("Server not detected\nStarting JsTestDriver server...")
  jtdProc = subprocess.Popen(["java", "-jar", JTD_PATH, "--port", JTD_PORT])
  print("JsTestDriver started")


#
# Launch the given Android emulator if it is not already running
#


print("\nDetecting Android emulator...")

adbProc = subprocess.Popen([ADB_PATH, "devices"], stdout=subprocess.PIPE)

# subprocess.communicate() returns a list of stdout and stderror as byte strings
output = adbProc.communicate()[0].decode("utf-8")

if output.find("emulator") == -1:
  print("Emulator not detected\nStarting emulator...")
  subprocess.call([EMULATOR_PATH, "-avd", AVD_NAME], stdout=subprocess.PIPE)
  print("Emulator started")

else:
  print("Emulator detected\n")

  # Kill any existing Android browser instances
  # This is necessary to prevent old JsTestDriver pages from being recaptured.
  print("Killing any existing Android browser instances...")
  psProc = subprocess.Popen([ADB_PATH, "shell", "ps"], stdout=subprocess.PIPE)
  output = psProc.communicate()[0].decode("utf-8")
  killed = False
  for line in output.splitlines():
    if line.find("browser") != -1:
      pid = line.split()[1]
      subprocess.call([ADB_PATH, "shell", "kill", pid], stdout=subprocess.PIPE)
      killed = True
      print("Browser instance " + pid + " killed")
  if not killed:
    print("No browser instances detected")


#
# Unlock the Android emulator's screen
#


# There is no way to detect whether the screen is locked from the command line,
# but if it is, we can unlock it by sending the keyevent corresponding to the
# Menu button once the emulator is initialized. This command may timeout if
# the emulator takes too long to load, so we retry until it succeeds.
print("\nUnlocking Android device...")
while 1:
  unlockProc = subprocess.Popen([ADB_PATH, "wait-for-device", "shell", "input", "keyevent", "82"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  result = unlockProc.communicate()[0].decode("utf-8")
  if result.find("Killed") == -1:
    print("Device unlocked\n")
    break


#
# Load the JsTestDriver test page in the emulator
# NOTE: The emulator uses http://10.0.2.2 to refer to the host machine
#


subprocess.call([ADB_PATH, "shell", "am", "start", "-a",\
  "android.intent.action.VIEW", "-d", "http://10.0.2.2:" + JTD_PORT + "/capture"],\
  stdout=subprocess.PIPE)

# Wait until the Android browser is captured
# We check the server's status page every second until it reports that there
# is at least 1 captured Android browser.
print("Capturing Android browser...")
while not AndroidBrowserIsCaptured():
  time.sleep(1)
print("Browser captured")

# We must wait for the JavaScript on the JsTestDriver page to initialize.
print("Waiting " + DELAY + " seconds for the browser to finish loading...")
time.sleep(float(DELAY))

print("\nInitialization complete")


#
# Run JsTestDriver tests
#


print("\nRunning tests:\n")

# Invoke JsTestDriver with the last arguments given on the command-line
testArgs = ["java", "-jar", JTD_PATH, "--tests", JTD_TEST] + sys.argv[7:]

testProc = subprocess.Popen(testArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
testResults = testProc.communicate()[0].decode("utf-8")
print(testResults)

# Kill the JsTestDriver server
jtdProc.kill()

