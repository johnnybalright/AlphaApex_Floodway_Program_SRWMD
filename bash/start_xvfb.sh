#!/bin/bash

export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x16 &
sleep 1
echo "Xvfb has been started."
