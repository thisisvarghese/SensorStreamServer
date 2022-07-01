#!/usr/bin/env python

import asyncio
import websockets
import socket
from base64 import b64decode
import wave
import json

import time
import os

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventData

CONNECTION_STR = 'Endpoint=sb://sensorhub.servicebus.windows.net/;SharedAccessKeyName=SendToEventHub;SharedAccessKey=+CJiJAnpZMhkfzM05RdW5XjGUOfE+rDIgKR8l/oxnCU=;EntityPath=edgedeviceevents'
EVENTHUB_NAME = 'edgedeviceevents'




def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


hostname = socket.gethostname()
IPAddr = get_ip()
print("Your Computer Name is: " + hostname)
print("Your Computer IP Address is: " + IPAddr)
print(
    "* Enter {0}:5000 in the app.\n* Press the 'Set IP Address' button.\n* Select the sensors to stream.\n* Update the 'update interval' by entering a value in ms.".format(IPAddr))


async def echo(websocket, path):
    

    
    

    
    async for message in websocket:
        if path == '/accelerometer':
            data = await websocket.recv()
            print(data)
            f = open("accelerometer.txt", "a")
            f.write(data+"\n")

        if path == '/gyroscope':
            data = await websocket.recv()
            print(data)
            f = open("gyroscope.txt", "a")
            f.write(data+"\n")

        if path == '/magnetometer':
            data = await websocket.recv()
            print(data)
            f = open("magnetometer.txt", "a")
            f.write(data+"\n")

        if path == '/orientation':
            data = await websocket.recv()
            print(data)
            f = open("orientation.txt", "a")
            f.write(data+"\n")

        if path == '/stepcounter':
            data = await websocket.recv()
            print(data)
            f = open("stepcounter.txt", "a")
            f.write(data+"\n")

        if path == '/thermometer':
            data = await websocket.recv()
            print(data)
            f = open("thermometer.txt", "a")
            f.write(data+"\n")

        if path == '/lightsensor':
            print("connected")
            data = await websocket.recv()
            print(data)
            f = open("lightsensor.txt", "a")
            f.write(data+"\n")
            
            producer = EventHubProducerClient.from_connection_string(
            conn_str="Endpoint=sb://sensorhub.servicebus.windows.net/;SharedAccessKeyName=SendToEventHub;SharedAccessKey=+CJiJAnpZMhkfzM05RdW5XjGUOfE+rDIgKR8l/oxnCU=;EntityPath=edgedeviceevents",
            eventhub_name="edgedeviceevents")
        
            to_send_message_cnt = 1
            event_data_batch = await producer.create_batch()
            for i in range(to_send_message_cnt):
                event_data = EventData(data)
                try:
                    event_data_batch.add(event_data)
                    print("event added in batch")
                except ValueError:
                    await producer.send_batch(event_data_batch)
                    event_data_batch = await producer.create_batch()
                    event_data_batch.add(event_data)
                    print("Event Sent to EH")
            if len(event_data_batch) > 0:
                await producer.send_batch(event_data_batch)
                print("Event Sent to EH if len>0")



        if path == '/proximity':
            data = await websocket.recv()
            print(data)
            f = open("proximity.txt", "a")
            f.write(data+"\n")

        if path == '/geolocation':
            data = await websocket.recv()
            print(data)
            f = open("geolocation.txt", "a")
            f.write(data+"\n")

        if path == '/camera':
            try:
                print("Device connected to camera endpoint")
                data = await websocket.recv()
                print("Image received for parsing")
                parsed_response = json.loads(data)
                fh = open(str(parsed_response['Timestamp']) + ".png", "wb")
                fh.write(b64decode(parsed_response['Base64Data']))
                print("Wrote image with timestamp " +str(parsed_response['Timestamp']))
            except Exception:
                print('Connection closed due to error')
                await websocket.close()

        if path == '/audio':
            print("Device connected to audio endpoint")
            data = await websocket.recv()
            print(data)
            decoded_data = b64decode(data, ' /')
            with open('temp.pcm', 'ab') as pcm:
                pcm.write(decoded_data)
            with open('temp.pcm', 'rb') as pcm:
                pcmdata = pcm.read()
            with wave.open('audio.wav', 'wb') as wav:
                #(nchannels, sampwidth, framerate, nframes, comptype, compname)
                #wav.setparams((1, 16, 32000, 32, 'NONE', 'NONE'))
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(48000)
                wav.setcomptype('NONE', 'NONE')
                wav.writeframesraw(pcmdata)
            print("Wrote to audio.wav")


asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 5000, max_size=1_000_000_000))
asyncio.get_event_loop().run_forever()
