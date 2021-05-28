#!/bin/sh

# Markus Neteler, 2021

# https://github.com/acaudwell/Gource
#
# installation
# dnf install gource
#
# prepare logs:
## http://code.google.com/p/gource/wiki/SVN
# git log --oneline > actinia-log.txt

#
# $ git log --pretty=format:user:%aN%n%at --reverse --raw --encoding=UTF-8 --no-renames --after={1.years.ago} > git.log
# $ gource -s .001 -f 1920x1080 --auto-skip-seconds .001 --multi-sampling --stop-at-end --hide mouse,progress,files,tree,filenames,dirnames --file-idle-time 15 --max-files 0 --output-framerate 30 --output-ppm-stream - --seconds-per-day 1 git.log
##
# gource --hide dirnames,filenames --seconds-per-day 0.1 --auto-skip-seconds 1 -1280x720 -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 gource.mp4

# !!careful to not overwrite existing file!!
# re-order from oldest to newest
# git log --oneline  --format="%ct|%s" | tac > gource.captions.txt

##############
#RES="1100x900"
#RES="1800x1100"
RES="1280x720"

OUTPUT=actinia_gource_contribs

##################
# switches:
## http://code.google.com/p/gource/wiki/Controls

## viz only, you can mouse-navigate
#gource --title "GRASS GIS 6.4.3" -$RES --bloom-intensity 0.5 --camera-mode track --hide filenames --seconds-per-day 0.05 --stop-at-end --disable-progress my-project-log.xml

# run in git directory
gource --title "actinia development" -$RES --bloom-intensity 0.5 --camera-mode track \
       --hide filenames --seconds-per-day 0.05 \
       --caption-file gource.captions.txt -caption-size 24 --caption-colour FF0066 --caption-duration 4 .

# film creation below, we stop for now
exit 0

# make MP4 film
## ?? --stop-at-end --disable-progress
#
# IMPORTANT: annotations = caption has to be in ascending order and unix time with pipe!
#  convert example: date "+%s" -d "Aug 04, 2019"
#
gource --title "actinia development" -$RES --bloom-intensity 0.5 --camera-mode track \
       --hide filenames --seconds-per-day 0.05 \
       --caption-file gource.captions.txt -caption-size 24 --caption-colour FF0066 --caption-duration 6 --output-ppm-stream - | ffmpeg -y -b:v 10000K -r 60 \
       -f image2pipe -vcodec ppm -i - -vcodec libx264 \
       -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 $OUTPUT.mp4

# make WebM film:
#gource --title "actinia development" -$RES --bloom-intensity 0.5 --camera-mode track --seconds-per-day 0.05 --stop-at-end --disable-progress --hide filenames -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libvpx -b:v 10000K $OUTPUT.webm

# play the thing:
echo "vlc $OUTPUT.mp4"
#vlc $OUTPUT.webm

