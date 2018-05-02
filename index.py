import os
import datetime
import sys
import json
import subprocess
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from gpiozero import LED, MotionSensor # Import GPIO library: https://gpiozero.readthedocs.io/en/stable/
from time import sleep
from losantmqtt import Device # Import Losant library: https://github.com/Losant/losant-mqtt-python

led_gpio = 23
pir_gpio = 20

led = LED(led_gpio)
pir = MotionSensor(pir_gpio, pull_up=False)
# Construct Losant device
device = Device("5ada7f66e304ec0006542ace", "43207a25-c78c-4b87-9349-1578dbd80686", "633f190871e9909a262bd31f2570b184c01abbd158af2a30deae104d2faadcfb")

fromaddr = "thisisforwow87@gmail.com"
toaddr = "thisisforwow87@gmail.com"

msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "PIR Active w/ Image"
body = "Image captured"

def on_command(device, command):
    print(command["name"] + " command received.")

    # Listen for the gpioControl. This name configured in Losant
    if command["name"] == "toggle":
        # toggle the LED
        led.toggle()

def sendDeviceState():
    print("Sending Device State")
    device.send_state({"pir": True})
    # read the absolute path
    script_dir = os.path.dirname(__file__)
    # call the .sh to capture the image
    os.system('fswebcam image.jpg')
    #get the date and time, set the date and time as a filename.
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    # create the real path
    rel_path = currentdate +".jpg"
    #  join the absolute path and created file name
    abs_file_path = os.path.join(script_dir, rel_path)
    print abs_file_path
    msg.attach(MIMEText(body, 'plain'))
    filename = "image.jpg"
    attachment = open("/home/pi/Desktop/Images/image.jpg","rb")
    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= %s" % filename)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, 'ISMELLASITCOM123')
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
                    

# Listen for commands.
device.add_event_observer("command", on_command)

print("Listening for device commands")

pir.when_motion = sendDeviceState #Sends device state when PIR goes active

    
# Connect to Losant and leave the connection open
device.connect(blocking=True)

