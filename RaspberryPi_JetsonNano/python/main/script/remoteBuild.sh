#!/bin/bash
pwd
ip_pony_pi=$1
if [ -z "$ip_pony_pi" ]; then
  echo "ip_pony_pi = null , use defalut"
  ip_pony_pi="192.168.5.21"
fi
git branch -D tmp_build
git stash save "tmp_build"
git checkout -b tmp_build
git stash apply
git add .
git commit -m "tmp_build"
git push origin tmp_build:tmp_build -f
ssh "solinzon@$ip_pony_pi" < main/script/ponyPiBuild.sh
echo "result ： $?"
git checkout pony_pi
git stash pop
