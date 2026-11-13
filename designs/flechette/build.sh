#!/usr/bin/env bash
# Build every flechette part in both rod sizes and run the checks.
# Output: 8mm/*.stl and 12.7mm/*.stl.   Usage: ./build.sh [extra openscad args]
set -uo pipefail
cd "$(dirname "$0")"
T=../../tools
for size in 8 12.7 12; do
  out="${size}mm"; mkdir -p "$out"
  for part in nose_ogive nose_trocar nose_spike tail_fins tail_basket tail_basket_spin; do
    openscad -q -o "$out/$part.stl" -D rod_d=$size -D "part=\"$part\"" "$@" flechette_parts.scad
  done
  openscad -q -o "$out/socket_fit_gauge.stl" -D rod_d=$size "$@" socket_fit_gauge.scad
  openscad -q -o "$out/sabot_petal.stl" -D rod_d=$size -D 'part="petal"' "$@" sabot.scad
  openscad -q -o "$out/sabot_all.stl" -D rod_d=$size -D 'part="all"' "$@" sabot.scad
  for f in "$out"/*.stl; do
    echo "== $f"
    mw=38.0; [[ $f == *sabot* ]] && mw=39.6
    python3 $T/check_stl.py "$f" --binary --max-width $mw
    [[ $f == *sabot_all* ]] && continue
    python3 $T/overhangs.py "$f" || echo "(overhang report above)"
    python3 $T/islands.py "$f" || echo "(island report above)"
  done
done
# XL tails (2 mm wider fins and basket) + the XL petal they need
for size in 8 12.7 12; do
  out="xl/${size}mm"; mkdir -p "$out"
  for part in tail_fins tail_basket_spin; do
    openscad -q -o "$out/${part}_xl.stl" -D rod_d=$size -D tail_xl=true -D "part=\"$part\"" "$@" flechette_parts.scad
  done
  openscad -q -o "$out/sabot_petal_xl.stl" -D rod_d=$size -D tail_xl=true -D 'part="petal"' "$@" sabot.scad
  openscad -q -o "$out/sabot_all_xl.stl" -D rod_d=$size -D tail_xl=true -D 'part="all"' "$@" sabot.scad
done
