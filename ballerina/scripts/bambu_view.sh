#!/bin/bash
# usage: bambu_view.sh out.png file1.stl [file2.stl ...]   -> side-by-side, Bambu-like flat orange shading
out=$1; shift; i=0; imgs=()
for f in "$@"; do
  echo "color([0.95,0.25,0.12]) import(\"$(realpath $f)\");" > bv_$i.scad
  # behind, slightly to her right, eye at hip height (matches Russ's screenshot)
  xvfb-run -a openscad -o bv_$i.png --imgsize=600,720 --camera=6,10,140,90,0,205,260 --colorscheme=Starnight bv_$i.scad >/dev/null 2>&1
  imgs+=(bv_$i.png); i=$((i+1))
done
python3 - "$out" "${imgs[@]}" <<'PY'
import sys; from PIL import Image
out=sys.argv[1]; ims=[Image.open(p) for p in sys.argv[2:]]
W=Image.new('RGB',(600*len(ims),720),'white'); [W.paste(im,(i*600,0)) for i,im in enumerate(ims)]; W.save(out)
PY
