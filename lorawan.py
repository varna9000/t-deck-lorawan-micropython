# LoraWan method for ABP join communications to TheThingsNetwork
# LoraWAN packet creation methond borrowed from
# https://github.com/lemariva/uPyLoRaWAN/blob/LoRaWAN/sx127x.py
# I've sligtly modified it to work for our case


from encryption_aes import AES
import radio
import machine
import ubinascii
import time
from random import randint


__DEBUG__ = True

ttn_config={
    'device_address': bytearray([0x00, 0x00, 0x00, 0x00]),
    'network_key': bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    'app_key': bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
}


frame_counter = 0
REG_DIO_MAPPING_1 = 0x40
fport = 1

# Frequency plans of TTN for Europe: https://www.thethingsnetwork.org/docs/lorawan/frequency-plans/
uplink_ch=[ 868100, 868300, 868500,
             867100, 867300, 867500,
             867700, 867900]

downlink_ch = 869525


def send_data(msg):

    global frame_counter

    # Send on different frequency channel
    shuffle_freq = uplink_ch[randint(0,7)]

    # I believe you'll need to send on one of the
    # first 3 frequencies before your device is activated
    # Later you can shuffle the messages on different freqs
    modem.configure({'freq_khz': shuffle_freq })

    print(f"Sending on {shuffle_freq} Khz")

    # prepare packet
    buf = lorawan_pkt(msg, len(msg))

    # Send msg
    modem.send(buf)

    # increase counter
    frame_counter+=1
    time.sleep(1)


def lorawan_pkt(data, data_length):

        # Data packet
        global frame_counter

        enc_data = bytearray(data_length)
        lora_pkt = bytearray(9) # was 64 in the original lib

        # Copy bytearray into bytearray for encryption
        enc_data[0:data_length] = data[0:data_length]

        # Encrypt data (enc_data is overwritten in this function)
        fc = frame_counter

        aes = AES(
            ttn_config['device_address'],
            ttn_config['app_key'],
            ttn_config['network_key'],
            fc
        )

        enc_data = aes.encrypt(enc_data)
        # Construct MAC Layer packet (PHYPayload)
        # MHDR (MAC Header) - 1 byte
        lora_pkt[0] = REG_DIO_MAPPING_1 # MType: unconfirmed data up, RFU / Major zeroed
        # MACPayload
        # FHDR (Frame Header): DevAddr (4 bytes) - short device address
        lora_pkt[1] = ttn_config['device_address'][3]
        lora_pkt[2] = ttn_config['device_address'][2]
        lora_pkt[3] = ttn_config['device_address'][1]
        lora_pkt[4] = ttn_config['device_address'][0]
        # FHDR (Frame Header): FCtrl (1 byte) - frame control
        lora_pkt[5] = 0x00
        # FHDR (Frame Header): FCnt (2 bytes) - frame counter
        lora_pkt[6] = frame_counter & 0x00FF
        lora_pkt[7] = (frame_counter >> 8) & 0x00FF
        # FPort - port field
        lora_pkt[8] = fport
        # Set length of LoRa packet
        lora_pkt_len = 9

        if __DEBUG__:
            print("PHYPayload", ubinascii.hexlify(lora_pkt))

        # load encrypted data into lora_pkt
        lora_pkt[lora_pkt_len : lora_pkt_len + data_length] = enc_data[0:data_length]

        if __DEBUG__:
            print("PHYPayload with FRMPayload", ubinascii.hexlify(lora_pkt))

        # Recalculate packet length
        lora_pkt_len += data_length

        # Calculate Message Integrity Code (MIC)
        # MIC is calculated over: MHDR | FHDR | FPort | FRMPayload
        mic = bytearray(4)
        mic = aes.calculate_mic(lora_pkt, lora_pkt_len, mic)

        # Load MIC in package
        lora_pkt[lora_pkt_len : lora_pkt_len + 4] = mic[0:4]

        # Recalculate packet length (add MIC length)
        lora_pkt_len += 4

        if __DEBUG__:
            print("PHYPayload with FRMPayload + MIC", ubinascii.hexlify(lora_pkt))

        return lora_pkt



modem = radio.get_modem()
# modem.calibrate()

for i in range(10):
    msg=b'counter:{}'.format(frame_counter)
    send_data(msg)
    time.sleep(10)
