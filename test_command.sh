#!/bin/bash
set -e

# Run this script to test the endpoints and save responses to files
clear
mkdir -p test_response

# home 路由
curl -s https://ns-nano-ih4e.onrender.com/ > test_response/home.html

# test_db 路由
curl -s https://ns-nano-ih4e.onrender.com/test_db | jq . > test_response/test_db.json

# dissociate locations 路由
location_paths=(
  "0_-52_26/"
  "0_-52_26/-2_50_-6"
  "-2_50_-6/0_-52_26"
)
echo "[" > test_response/coords.json
for i in "${!location_paths[@]}"; do
  curl -s "https://ns-nano-ih4e.onrender.com/dissociate/locations/${location_paths[$i]}" | jq .
  if [ "$i" -lt "$((${#location_paths[@]}-1))" ]; then
    echo "," 
  fi
done >> test_response/coords.json
echo "]" >> test_response/coords.json

# dissociate terms 路由
term_paths=(
  "posterior_cingulate/"
  "anterior_cingulate/ventromedial_prefrontal"
  "ventromedial_prefrontal/posterior_cingulate"
)
echo "[" > test_response/terms.json
for i in "${!term_paths[@]}"; do
  curl -s "https://ns-nano-ih4e.onrender.com/dissociate/terms/${term_paths[$i]}" | jq .
  if [ "$i" -lt "$((${#term_paths[@]}-1))" ]; then
    echo ","
  fi
done >> test_response/terms.json
echo "]" >> test_response/terms.json

clear
echo "Successfully tested the dissociate endpoints!"
