#!/bin/bash
# usage: bv2.sh out.png "camera" file1 file2 ...
out=$1; cam=$2; shift 2; i=0; imgs=()
for f in "$@"; do
  echo "color([0.95,0.25,0.12]) import(\"$(realpath $f)\");" > bw_$i.scad
  xvfb-run -a openscad -o bw_$i.png --imgsize=500,600 --camera=$cam --colorscheme=Starnight bw_$i.scad >/dev/null 2>&1
  imgs+=(bw_$i.png); i=$((i+1))
done
python3 - "$out" "${imgs[@]}" <<'PY'
import sys; from PIL import Image
out=sys.argv[1]; ims=[Image.open(p) for p in sys.argv[2:]]
W=Image.new('RGB',(500*len(ims),600),'white'); [W.paste(im,(i*500,0)) for i,im in enumerate(ims)]; W.save(out)
PY
