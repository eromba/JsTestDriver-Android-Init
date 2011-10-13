# JsTestDriver / Android Emulator Initialization Script

Automates the initialization of JsTestDriver with an Android emulator,
capturing the emulator's web browser in the JsTestDriver server instance.

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

To initialize JsTestDriver and the Android emulator:  
`jtd-android-init.py [Path to JTD] [Port] [Path to SDK] [AVD] [Delay]`

To initialize only JsTestDriver:  
`jtd-android-init.py [Path to JTD] [Port]`

- **Path to JTD** : The path to your JsTestDriver JAR file
- **Port** : The port on which to start the JsTestDriver server
- **Path to SDK** : The path to your local Android SDK directory
- **AVD** : The name of the Android Virtual Device to start
- **Delay** : The number of seconds to wait for the Android browser to
  finish loading the JsTestDriver test page

## Current Limitations

- Does not support capturing the browser of a USB-connected Android device.
- Does not support capturing multiple emulator instances.

