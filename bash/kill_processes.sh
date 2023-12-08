#!/bin/bash

killall -w -e -q chrome
killall -w -e -q chromedriver
killall -w -e -q Xvfb
killall -w -e -q rg
echo "All specified processes have been terminated."
