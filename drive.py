# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 11:55:05 2019

@author: AI & ML
"""
import numpy as np
import socketio           #for integrating with game using server
import eventlet
from flask import Flask
from keras.models import load_model
import base64
from io import BytesIO  #working wiith images
from PIL import Image
import cv2

sio = socketio.Server()   #Handling with server

app = Flask(__name__) #'__main__'

speed_limit = 30

def img_preprocess(img):
  img = img[60:135,:,:]
  img = cv2.cvtColor(img,cv2.COLOR_RGB2YUV)
  img = cv2.GaussianBlur(img, (3,3),0)
  img = cv2.resize(img,(200,66))
  img = img/255
  
  return img



@sio.on('telemetry')                       #Sending signal to game

def telemetry(sid, data):
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))   #take image from game
    image = np.asarray(image)
    image = img_preprocess(image)       #preprocessing
    image = np.array([image])
    steering_angle = float(model.predict(image))    #predicting streering angle
    throttle = 1.0 - speed/speed_limit               #predicting throttle
    print('{} {} {}'.format(steering_angle, throttle,speed))
    send_control(steering_angle,throttle)                        #sending commands

@sio.on('connect')#message, disconnect     #to connect with game

def connect(sid, environ):
    print('connected')
    send_control(0,0)
    
def send_control(steering_angle,throttle):                #sending signal using telemetry
    sio.emit('steer',data={
            'steering_angle':steering_angle.__str__(),
            'throttle':throttle.__str__()
            })
    

if __name__=='__main__':
    model = load_model('model.h5')  #loading model from colab 
    app = socketio.Middleware(sio,app)   #for creating the tunnel between game and python
    eventlet.wsgi.server(eventlet.listen(('',4567)),app)    #port 
