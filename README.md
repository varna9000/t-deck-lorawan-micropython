# Micropython examples for running Liligo's T-deck

You'll need firmware which supports the display. I used the one from [Russ Huges' repo](https://github.com/russhughes/st7789_mpy/tree/master/firmware/GENERIC_S3_SPIRAM_OCT)

Many of the examples I've ported from the C code provided in Lilygo [T-deck repo](https://github.com/Xinyuan-LilyGO/T-Deck). LoRa radio examples work with the *new native LoRa drivers*. In the current case it's sx1262 chip driver.

The example files are used as follows:

- encryption_aes.py: imported and used in the example for loraWan communication. Could be used for encrypting p2p messages as well. Lib borrowed from [uPyLoRaWAN repo](https://github.com/lemariva/uPyLoRaWAN/tree/LoRaWAN)

- font16.py and vga2_8x16.py - compiled font files

- lorawan.py:

LoRawan functions (packet constructor and send function) for issuing ABP mode join. According to The Things Network, ABP mode is not recommended, but it's much easier to implement, hence I went for it. OTAA joins are not implemented (yet). Currently only sending data is implemented, I'll be working on RX in the next few weeks. The frequencies are set for Europe, so you should modify them in case you are not in Europe.

This file is a working example. If run, it will send 10 consequent messages to TTN network. Make sure you setup the device in the TTN console as ABP activated end device and put in the file the credentials: device address, network key and application key. Please read the code comments if you don't see the message in the TTN console. The first device join need to be on one of the three frequencies TTN requires.

- radio.py: initiation of  LoRa radio. The file contains configurations for both LoRa p2p and lorawan. Change them according to the task you are doing. File is used as init of the drivers by main.py and lorawan.py

- main.py: simple TUI interface for LoRa p2p messaging. Make sure you activate p2p configuration in radio.py before running this file.

- trackball.py: micropython port of the C example from Lilygo's repo.
