#!/bin/sh

#######
# gource animation script
# https://github.com/acaudwell/Gource
#
# Copyright (c) 2021 Markus Neteler and mundialis GmbH & Co. KG
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#######


#
# installation
# dnf install gource
#
# preparation of logs:
#
# !!careful to not overwrite existing file!!
# captions sorted from oldest to newest
# git log --oneline --reverse --format="%ct|%s" > gource_captions.txt

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
       --caption-file gource.captions.txt -caption-size 24 --caption-colour FF0066 --caption-duration 4 ../..

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

