#!/bin/bash
# usage: cmp.sh out.png "name:tx,ty,tz,rx,ry,rz,dist" ...   (coords in ORIGINAL 50 mm units)
out=$1; shift; S=6.1; files=()
for spec in "$@"; do n=${spec%%:*}; IFS=, read tx ty tz rx ry rz d <<< "${spec#*:}"
  cam=$(python3 -c "print(','.join(map(str,[$tx*$S,$ty*$S,$tz*$S,$rx,$ry,$rz,$d*$S])))")
  for f in b_scaled b2; do echo "color(\"Gainsboro\") import(\"$(pwd)/$f.stl\");" > w_$f.scad; xvfb-run -a openscad -o c_${n}_$f.png --imgsize=500,500 --camera=$cam --colorscheme=Tomorrow w_$f.scad >/dev/null 2>&1; done
  files+=("$n")
done
python3 - "$out" "${files[@]}" <<'PY'
import sys; from PIL import Image, ImageDraw
out=sys.argv[1]; names=sys.argv[2:]
W=Image.new('RGB',(300*len(names),620),'white'); d=ImageDraw.Draw(W)
for i,n in enumerate(names):
    for j,f in enumerate(['b_scaled','b2']):
        W.paste(Image.open(f'c_{n}_{f}.png').resize((300,300)),(i*300,20+j*300))
    d.text((i*300+5,2),n,fill='black')
d.text((5,22),'BEFORE',fill='red'); d.text((5,322),'AFTER',fill='red')
W.save(out)
PY
