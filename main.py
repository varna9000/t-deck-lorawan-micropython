import machine
import st7789
import font16 as font
import utime
import vga2_8x16 as font
import radio
import sound
import time


#utime.sleep(2)
history_buf=[]
cmd_buf=bytearray()

print("Keyboard ready ..\n")
MAX_WIDTH = 318
MAX_HEIGHT = 238
RSSI=0

#clean input line 40 spaces
clean_input = '{: <40}'.format("")

bat = machine.ADC(machine.Pin(4))
bat.width(machine.ADC.WIDTH_12BIT)
bat.atten(machine.ADC.ATTN_11DB)

bat_time_update=time.ticks_add(time.ticks_ms(), 1000)

spi = machine.SPI(1, baudrate=8000000, sck=machine.Pin(40), mosi=machine.Pin(41), miso=machine.Pin(38))

DC = machine.Pin(11, machine.Pin.OUT)
CS = machine.Pin(12, machine.Pin.OUT)
BL = machine.Pin(42, machine.Pin.OUT)

tft = st7789.ST7789(spi,
                    240,
                    320,
                    dc=DC,
                    cs=CS,
                    backlight=BL,
                    rotation=1)


kbd_pwr = machine.Pin(10, machine.Pin.OUT)
kbd_int = machine.Pin(46, machine.Pin.IN)
i2c = machine.SoftI2C(scl=machine.Pin(8), sda=machine.Pin(18), freq=400000, timeout=50000)


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('ssid', 'password')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


def get_key():
    ch = i2c.readfrom(0x55, 1)
    #if ch != 0:
    return ch


def split_rows(input_string, row_delimiter='\r', chunk_size=40):
    rows = input_string.split(row_delimiter)

    for row in rows:
        for i in range(0, len(row), chunk_size):
            chunk = row[i:i+chunk_size]
            history_buf.append(chunk)

    if len(history_buf) > 11:
        del history_buf[0:len(history_buf)-11]

    # print(f"{history_buf=}")


def chat_history(buf):
    split_rows(buf.decode())

    for txt in history_buf:

        if txt[0:3] == 'me>':
            tft.text(font, txt[0:3], 0, (history_buf.index(txt)+1)*16, st7789.GREEN, st7789.BLACK)
            tft.text(font, txt[3:], 24, (history_buf.index(txt)+1)*16, st7789.WHITE, st7789.BLACK)
        elif txt[0:4] == 'oth>':
            tft.text(font, txt[0:4], 0, (history_buf.index(txt)+1)*16, st7789.RED, st7789.BLACK)
            tft.text(font, txt[4:], 24, (history_buf.index(txt)+1)*16, st7789.WHITE, st7789.BLACK)
        else:
            tft.text(font, txt, 0, (history_buf.index(txt)+1)*16, st7789.WHITE, st7789.BLACK)


def cmd_line(cmd_buf):
    for rows in cmd_buf:
        tft.text(font, cmd_buf.decode(), 0, 222, st7789.WHITE, st7789.BLACK)


def draw_navbar(bat, rssi=0):
    # draw navbar
    for i in range(0,318,8):
        tft.text(font, 223, i, 0, st7789.BLUE, st7789.BLUE)
    tft.text(font, f"bat:{bat}V", 0, 0, st7789.WHITE, st7789.BLUE)
    tft.text(font, f"rssi:{rssi}", 90, 0, st7789.WHITE, st7789.BLUE)


def update_bat():
    global bat_time_update
    global RSSI
    if time.ticks_diff(bat_time_update, time.ticks_ms()) < 0:
        battery_voltage=((bat.read_u16() * 3.3) / 65535)/ (100/200)
        #update every minute
        bat_time_update = time.ticks_add(time.ticks_ms(), 60000)
        draw_navbar(round(battery_voltage,2), RSSI)

#enable keyboard
kbd_pwr.on()
utime.sleep(.5)


#Initit LoRa
modem=radio.get_modem()

#enable screen
tft.init()
tft.on


#draw red delimiter line
for i in range(0,318,8):
    tft.text(font, 223, i, 206, st7789.BLUE, st7789.BLACK)

modem.calibrate()

while True:

    update_bat()

    a = get_key()

    if a != b'\x00':
        # handle backspace
        if a == b'\x08':
            #delete last char including backspace byte
            cmd_buf=cmd_buf[:-1]
            tft.text(font, clean_input, 0, 222, st7789.BLACK, st7789.BLACK)
            tft.text(font, cmd_buf.decode(), 0 , 222, st7789.BLACK, st7789.BLACK)
        else:
            cmd_buf +=a

        if a == b'\r':
            print("Sending...")
            chat_history(b'me> '+ cmd_buf)
            tft.text(font, clean_input, 0, 222, st7789.BLACK, st7789.BLACK)
            modem.send(cmd_buf[:-1])
            cmd_buf=b''

        cmd_line(cmd_buf)

    rx = modem.recv(300)
    if rx:
        print(f"Received: {rx}")
        sound.click()
        chat_history(b'oth> '+ rx)
        RSSI = rx.rssi
        tft.text(font, clean_input, 0, 222, st7789.BLACK, st7789.BLACK)

kbd_pwr.off()
