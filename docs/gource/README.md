## Gource: visualization of source code development


### Installation

Gource page: https://github.com/acaudwell/Gource

### Captions

Note: Captions have to be in ascending order and with unix timestamps, separated by pipe.

```
# !!careful to not overwrite existing file!!
# captions sorted from oldest to newest
# git log --oneline --reverse --format="%ct|%s" > gource_captions.txt
```

### Create the animation on screen

```
# run in git directory
gource --title "actinia development" -$RES --bloom-intensity 0.5 --camera-mode track \
       --hide filenames --seconds-per-day 0.05 \
       --caption-file gource_captions.txt -caption-size 24 --caption-colour FF0066 --caption-duration 4 ../..
```


### Create the animation as a MP4 film

```
gource --title "actinia development" -$RES --bloom-intensity 0.5 --camera-mode track \
       --hide filenames --seconds-per-day 0.05 \
       --caption-file gource_captions.txt -caption-size 24 --caption-colour FF0066 --caption-duration 6 --output-ppm-stream - | ffmpeg -y -b:v 10000K -r 60 \
       -f image2pipe -vcodec ppm -i - -vcodec libx264 \
       -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 $OUTPUT.mp4
```

### Create the animation as a WebM film:

```
gource --title "actinia development" -$RES --bloom-intensity 0.5 --camera-mode track --seconds-per-day 0.05 --stop-at-end --disable-progress --hide filenames -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libvpx -b:v 10000K $OUTPUT.webm
```
