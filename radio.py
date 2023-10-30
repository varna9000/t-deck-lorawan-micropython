from machine import SPI, Pin
from lora import SX1262


def get_modem():

# These settings are for LoRa P2P
#     lora_cfg = {
#         "freq_khz": 869000,
#         "sf": 7,
#         "bw": "125",  # kHz
#         "coding_rate": 5,
#         "preamble_len": 8,
#         "output_power": 14,  # dBm
#         "syncword":  0x1424
#         "pa_ramp_us": 80
#      }

#These settings are for LoraWan
    lora_cfg = {
        "freq_khz": 868100,
        "sf": 7,
        "bw": "125",  # kHz
        "coding_rate": 8, # Works only with 4/8
        "preamble_len": 8,
        "output_power": 14,  # dBm
        "syncword":  0x3444 # This setting is important for LoraWan
     }

    # Set up correct spi pins for T-deck
    spi = SPI(1, baudrate=8000000, sck=Pin(40), mosi=Pin(41), miso=Pin(38))
    cs = Pin(9)

    return SX1262(spi, cs,
                 busy=Pin(13),  # Required
                 dio1=Pin(45),   # Optional, recommended
                 reset=Pin(17),  # Optional, recommended
                 dio3_tcxo_millivolts=3300,
                 lora_cfg=lora_cfg)
