#!/bin/bash

IFS="
"

__FILE__="$(realpath -- "$0")"
D="$(dirname -- "$__FILE__")"

for TXT in $(find "$D/data" -type f -name '*.txt')
do
	for i in \
		'pelayo'                \
		'f.elix\s+breva'        \
		'lepanto'               \
		'jorge\s+juan'          \
		'barrachina'            \
		'v.zquez\s+mella'       \
		'arquitecto\s+ros'      \
		'rep.blica\s+argentina' \
		'sidro\s+vilar+oig'     \
		'pintor\s+camar.n'      \
		'figueroles'            \
		'gran\s+v.a'
	do
		cat "$TXT" | tr '\n' ' ' | (grep -qiE "$i" "$TXT" && echo "$i": "$TXT")
	done
done

