from machine import Pin, I2S
import math
import struct



i2s = I2S(0,
          sck=Pin(7),
          ws=Pin(5),
          sd=Pin(6),
          mode=I2S.TX,
          bits=16,
          format=I2S.MONO,
          rate=22050,
          ibuf=40000) # create I2S object


TONE_FREQUENCY_IN_HZ = 440
SAMPLE_SIZE_IN_BITS = 16
SAMPLE_RATE_IN_HZ = 22_050



def make_tone(rate, bits, frequency):
    # create a buffer containing the pure tone samples
    samples_per_cycle = rate // frequency
    sample_size_in_bytes = bits // 8
    samples = bytearray(samples_per_cycle * sample_size_in_bytes)
    volume_reduction_factor = 8 # volume!
    range = pow(2, bits) // 2 // volume_reduction_factor

    if bits == 16:
        format = "<h"
    else:  # assume 32 bits
        format = "<l"

    for i in range(samples_per_cycle):
        sample = range + int((range - 1) * math.sin(2 * math.pi * i / samples_per_cycle))
        struct.pack_into(format, samples, i * sample_size_in_bytes, sample)

    return samples

def click():
    click = make_tone(SAMPLE_RATE_IN_HZ, SAMPLE_SIZE_IN_BITS, TONE_FREQUENCY_IN_HZ)
    tone=bytearray()

    for i in range(50):
        tone=tone+click

    i2s.write(tone)
