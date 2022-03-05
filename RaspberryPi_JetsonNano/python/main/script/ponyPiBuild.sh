#!/bin/bash
echo "开始执行脚本 ..."
pwd
cd /home/solinzon/project/e-Paper || exit
git add .
git reset --hard HEAD
git checkout pony_pi
git branch -D tmp_build
git fetch --all
git checkout tmp_build
git pull
cd /home/solinzon/project/e-Paper/RaspberryPi_JetsonNano/python || exit
pwd
echo "开始执行 python3 main/pony_pi_main.py ..."
sudo python3 main/pony_pi_main.py
echo "执行完成  ..."
cd /home/solinzon/project/e-Paper || exit
pwd

