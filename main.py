import network
import time
import machine
import gc
import network
import ssl
import time
import ubinascii
from umqtt.simple import MQTTClient
from random import random
from machine import UART
import ntptime
from machine import Pin, SoftI2C
import ssd1306
import urandom


i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)







MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())

SSID = b'xxxx-xxxx-xxx'
WIFI_PASSWORD = b'xxxxxxxx'
THING_NAME = b'TEST'
MQTT_BROKER = b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.amazonaws.com'

MQTT_CLIENT_KEY = "private.pem.key"
MQTT_CLIENT_CERT  = "certificate.pem.crt"
MQTT_BROKER_CA = "AmazonRootCA1.pem"


def read_pem(file):
    with open(file, "r") as input:
        text = input.read().strip()
        split_text = text.split("\n")
        base64_text = "".join(split_text[1:-1])
        return ubinascii.a2b_base64(base64_text)


def connect_internet():
    try:
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(SSID, WIFI_PASSWORD)

        for i in range(0, 10):
            if not sta_if.isconnected():
                time.sleep(1)
        print("Connected to Wi-Fi")
    except Exception as e:
        print('There was an issue connecting to WIFI')
        print(e)






def on_mqtt_msg(topic, msg):

    topic_str = topic.decode()
    msg_str = msg.decode()
    oled.fill_rect(0, 20, oled_width, 20, 0)
    print(f"RX: {topic_str}\n\t{msg_str}")
    oled.text(msg_str, 0, 20)



connect_internet()
print (time.localtime())
for i in range (3):
    try:
        ntptime.settime()
        time.sleep(5)
        print (time.localtime())
    except OSError:
        print('OSError')
        pass

key = read_pem(MQTT_CLIENT_KEY)
cert = read_pem(MQTT_CLIENT_CERT)
ca = read_pem(MQTT_BROKER_CA)


mqtt_client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    keepalive=60,
    ssl=True,
    ssl_params={
        "key": key,
        "cert": cert,
        "server_hostname": MQTT_BROKER,
        "cert_reqs": ssl.CERT_REQUIRED,
        "cadata": ca,
    },
)

def mqtt_publish(client, topic=THING_NAME, message=''):
    print("Publishing message...")
    client.publish(topic, message)
    print(message)

print(f"Connecting to MQTT broker")

mqtt_client.set_callback(on_mqtt_msg)
mqtt_client.connect()
mqtt_client.subscribe(THING_NAME)


def random_get():
    return urandom.randint(0, 100)


print("Connection established, awaiting messages")
while True:

    mqtt_client.check_msg()
    message_random = b'{"random":%s}' % random_get()
    mqtt_publish(client=mqtt_client,message=message_random)
    oled.text('Veri Bekleniyor', 0, 0)
    oled.show()
    time.sleep(5)
