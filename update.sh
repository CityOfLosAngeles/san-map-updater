#!/bin/bash
set -e 

source /home/ubuntu/.bashrc
python /home/ubuntu/san-map-updater/map_creator.py

echo "Done Updating"
