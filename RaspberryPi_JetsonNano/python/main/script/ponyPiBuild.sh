#!/bin/bash
git add .
git reset --hard HEAD
git branch -D tmp_build
git fetch --all
git checkout -b tmp_build
git pull
echo "cur ...."
cd /home/solinzon/project/e-Paper/RaspberryPi_JetsonNano/python
pwd
sudo python3 main/pony_pi_main.py