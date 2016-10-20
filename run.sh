#!/bin/bash

IFS="
"

for i in wget pdftotext
do
	if [ -z "$(which -- "$i")" ]
	then
		echo "Missing '$i'" >&2
		exit 255
	fi
done

__FILE__="$(realpath -- "$0")"
D="$(dirname -- "$__FILE__")"

# U="http://www.castello.es/web30/pages/contenido_web20.php?cod0=7&cod1=48&cod2=164&idcont=897"  # 2015
U="http://www.castello.es/web30/pages/contenido_web20.php?cod0=7&cod1=48&cod2=164&idcont=991"  # 2016

PDFS="$(wget -O - -qq "$U" | \
	tr ' ' '\n' | \
	grep -a '^href' | \
	cut -d '"' -f 2 | \
	grep -iaE 'http://www.castello.es/.*\.pdf$')"


[ -d "$D/data" ] || mkdir -p "$D/data"
find "$D/data" -type f -empty -exec rm {} \;
for PDF in $PDFS
do
	DEST="$D/data/$(basename -- "$PDF")"
	wget -c -qq -O "$DEST" "$PDF"

	TXT="${DEST/.pdf/.txt}"
	if [ ! -f "TXT" ]; then
		pdftotext "$DEST"
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
	fi
done

