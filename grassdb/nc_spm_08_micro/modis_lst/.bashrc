test -r ~/.alias && . ~/.alias
PS1='GRASS 7.8.dev (nc_spm_08_grass7):\w > '
grass_prompt() {
    MAPSET_PATH="`g.gisenv get=GISDBASE,LOCATION_NAME,MAPSET separator='/'`"
    LOCATION="$MAPSET_PATH"
    if test -f "$MAPSET_PATH/cell/MASK" && test -d "$MAPSET_PATH/grid3/RASTER3D_MASK" ; then
        echo [2D and 3D raster MASKs present]
    elif test -f "$MAPSET_PATH/cell/MASK" ; then
        echo [Raster MASK present]
    elif test -d "$MAPSET_PATH/grid3/RASTER3D_MASK" ; then
        echo [3D raster MASK present]
    fi
}
PROMPT_COMMAND=grass_prompt
alias l="ls -lart"

export PATH="/home/mneteler/software/grass78_git/dist.x86_64-pc-linux-gnu/bin:/home/mneteler/software/grass78_git/dist.x86_64-pc-linux-gnu/scripts:/home/mneteler/.grass7/addons/bin:/home/mneteler/.grass7/addons/scripts:/home/mneteler/.local/bin:/home/mneteler/bin:/usr/libexec/python2-sphinx:/usr/share/Modules/bin:/usr/lib64/ccache:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/home/mneteler/bin:/var/lib/snapd/snap/bin:/home/mneteler/bin:/var/lib/snapd/snap/bin"
export HOME="/home/mneteler"
