#!/bin/bash
# usage: views.sh out.png file.stl cx cy cz dist az1 az2 ...   (flat orange, horizontal views)
out=$1; f=$2; cx=$3; cy=$4; cz=$5; d=$6; shift 6; imgs=()
echo "color([0.95,0.25,0.12]) import(\"$(realpath $f)\");" > vw.scad
for a in "$@"; do
  xvfb-run -a openscad -o vw_$a.png --imgsize=500,600 --camera=$cx,$cy,$cz,80,0,$a,$d --colorscheme=Starnight vw.scad >/dev/null 2>&1
  imgs+=(vw_$a.png)
done
python3 - "$out" "${imgs[@]}" <<'PY'
import sys; from PIL import Image
out=sys.argv[1]; ims=[Image.open(p) for p in sys.argv[2:]]
W=Image.new('RGB',(500*len(ims),600),'white'); [W.paste(im,(i*500,0)) for i,im in enumerate(ims)]; W.save(out)
PY
