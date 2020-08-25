test -r ~/.alias && . ~/.alias
PS1='GRASS 7.8.4dev (nc_spm_08_micro):\w > '
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
export HOME="/home/abettge"
export PATH="/home/abettge/repos/grass78/dist.x86_64-pc-linux-gnu/bin:/home/abettge/repos/grass78/dist.x86_64-pc-linux-gnu/scripts:/home/abettge/.grass7/addons/bin:/home/abettge/.grass7/addons/scripts:/home/abettge/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/abettge/.local/bin"
