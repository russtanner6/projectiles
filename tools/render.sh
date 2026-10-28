#!/usr/bin/env bash
# Render an OpenSCAD design to a binary STL plus preview PNGs, then check it.
# Usage: tools/render.sh designs/mk1/mk1_dart.scad [extra openscad args, e.g. -D '$fn=40']
# Needs: openscad, xvfb-run (for PNGs), python3 with trimesh.
set -euo pipefail

scad="$1"; shift
dir="$(dirname "$scad")"
name="$(basename "$scad" .scad)"
stl="$dir/$name.stl"
mkdir -p "$dir/previews"

openscad -o "$stl" "$@" "$scad"
python3 "$(dirname "$0")/check_stl.py" "$stl" --binary
python3 "$(dirname "$0")/overhangs.py" "$stl"

wrapper="$(mktemp --suffix=.scad)"
echo "color(\"SteelBlue\") import(\"$(realpath "$stl")\");" > "$wrapper"
center_z=$(python3 -c "import trimesh;m=trimesh.load('$stl');print(round(m.bounds[1][2]/2,1))")
# side view (slightly from above) and view from below (tail)
xvfb-run -a openscad -o "$dir/previews/${name}_side.png" --imgsize=900,1100 \
  --camera=0,0,$center_z,70,0,25,300 --colorscheme=Tomorrow "$wrapper" 2>/dev/null
xvfb-run -a openscad -o "$dir/previews/${name}_tail.png" --imgsize=900,900 \
  --camera=0,0,$center_z,230,0,25,300 --colorscheme=Tomorrow "$wrapper" 2>/dev/null
# true lengthwise cross-sections (between and through the fin planes)
python3 "$(dirname "$0")/section.py" "$stl" "$dir/previews/${name}_section.png"
rm -f "$wrapper"
echo "previews in $dir/previews/"
