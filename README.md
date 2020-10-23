# RTMS

<img style='display: "block"' src="https://user-images.githubusercontent.com/61390950/97031491-10a61000-1569-11eb-90ac-4984ca69e0cc.png" alt="alt text" width="60%" height="270px">

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![Open Source Love png1](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![saythanks](https://img.shields.io/badge/say-thanks-ff69b4.svg)](https://saythanks.io/to/moshvilla@yandex.com)

## What's that? 
A temperature monitoring system based on raspberry pi, max31865 module, and pt100 temperature sensor

## How to use
1. clone the repo

2. Create creadintials for sending mails through gmail smtp
first, enable 2fa in your google account. 
second, create custom app password here 
https://myaccount.google.com/apppasswords
then, put username and password in config.ini

3. install requirements
```
pip install -r requirements.txt
```
3. start the app
```
python3 app.py
```
4. open the app in the browser


## Known technologies used in this project:
### Backend
Python - flask
### Frontend
JS - bootstrap - Jquery - Plotly.js

