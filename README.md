# JsTestDriver / Android Emulator Initialization Script

Automates the initialization of JsTestDriver with an Android emulator,
capturing the emulator's web browser in the JsTestDriver server instance
and running the tests specified on the command line.

## Dependencies

- **Python**  
  (Tested with versions 2.7.2 and 3.2.2)  
  [http://www.python.org/](http://www.python.org/)
- **JsTestDriver**  
  (Tested with version 1.3.3c)  
  [http://code.google.com/p/js-test-driver/](http://code.google.com/p/js-test-driver/)
- **Android SDK**  
  [http://developer.android.com/sdk/index.html](http://developer.android.com/sdk/index.html)

## Usage

`jtd-android-init.py [Path to SDK] [AVD] [Delay] [Path to JTD] [JTD Port] [JTD Test] [JTD Args]...`

- **Path to SDK** : The path to your local Android SDK directory
- **AVD**         : The name of the Android Virtual Device to start
- **Delay**       : The number of seconds to wait for the Android browser to
  finish loading the JsTestDriver test page
- **Path to JTD** : The path to your JsTestDriver JAR file
- **JTD Port**    : The port on which to start the JsTestDriver server
- **JTD Test**    : The JsTestDriver tests to run
  (This should be a proper value for the JsTestDriver "[--tests](http://code.google.com/p/js-test-driver/wiki/CommandLineFlags#--tests)" option)
- **JTD Args**    : Additional arguments to pass to JsTestDriver when running tests

###Example

`jtd-android-init.py /usr/bin/android-sdk/ Android233 10 JsTestDriver.jar 9876 all --browser /usr/bin/Firefox/firefox.exe`

## Current Limitations

- Does not support capturing the browser of a USB-connected Android device.
- Does not support capturing multiple emulator instances.

