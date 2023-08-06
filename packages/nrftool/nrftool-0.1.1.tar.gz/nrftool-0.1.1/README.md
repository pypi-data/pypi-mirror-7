nrftool
=======

A tool to flash and erase nRF devices

Dependencies
------------

* J-Link programmer or J-Link OB microcontroller (on-board)
* [Segger's JLink software](http://www.segger.com/jlink-software.html) (`V4.80`)

Supported devices
-----------------

Currently, only the nRF51822 chip is supported.

Usage
-----

To flash new firmware:

	$ nrftool flash FIRMWARE ADDRESS [--verbose]

To erase current firmware:

	$ nrftool erase [--verbose]

If `JLinkExe` can't be found in your `PATH`, it can be specified using `--jlinkexe` option:

	$ nrftool --jlinkexe path/to/your/JLinkExe erase
