# Full build: html -> vector pdf -> stamp vector Swift logo -> verify -> preview
$ErrorActionPreference = 'Stop'
$S = "C:\Users\ACCOUNTS\AppData\Local\Temp\claude\d--Projects-Vistex\7ce5ea09-1dfb-4acd-91c5-126113df775f\scratchpad"
$P = "$S\pack"
$PY = "$S\venv\Scripts\python.exe"
& $PY "$P\build.py"
Push-Location $P
node render.js carton.html       "$P\_art.pdf"
node render.js carton-proof.html "$P\_proof.pdf"
Pop-Location
& $PY "$P\stamp.py" "$P\_art.pdf"   "$P\artwork.pdf"
& $PY "$P\stamp.py" "$P\_proof.pdf" "$P\proof.pdf"
& $PY "$P\verify.py" "$P\artwork.pdf" "$P\proof.pdf"
& $PY -c @"
import pymupdf
from PIL import Image
for n in ('proof','artwork'):
    d = pymupdf.open(rf'$P\{n}.pdf')
    pix = d[0].get_pixmap(dpi=165)
    Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(rf'$P\{n}.png')
"@
