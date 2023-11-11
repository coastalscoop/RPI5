#/bin/bash

sleep 20
export XAUTHORITY=/home/picam_blast/.Xauthority
export DISPLAY=:0
export S3CFG=/home/picam_blast/.s3cfg

PATH=/usr/local/bin:/usr/bin:/bin

/home/picam_blast/rpi5_multicam_testing/ScheduledCollection2 >"/home/picam_blast/rpi5_multicam_testing/logs/picoastalAll_"$(date +'%Y%m%d_%H%M')".log" 2>&1
