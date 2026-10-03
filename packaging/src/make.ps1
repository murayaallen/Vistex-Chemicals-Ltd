# Full build: html -> vector pdf -> stamp vector Swift logo -> verify -> previews
$ErrorActionPreference = 'Stop'
$S = "C:\Users\ACCOUNTS\AppData\Local\Temp\claude\d--Projects-Vistex\7ce5ea09-1dfb-4acd-91c5-126113df775f\scratchpad"
$P = "$S\pack"
$PY = "$S\venv\Scripts\python.exe"
& $PY "$P\build.py"
$m = Get-Content "$P\meta.json" -Raw | ConvertFrom-Json
Push-Location $P
node render.js card-front.html "$P\_front.pdf" $m.PAGE_W  $m.PAGE_H
node render.js card-back.html  "$P\_back.pdf"  $m.PAGE_W  $m.PAGE_H
node render.js card-proof.html "$P\_proof.pdf" $m.PROOF_W $m.PROOF_H
Pop-Location
& $PY "$P\stamp.py" "$P\_front.pdf" "$P\front.pdf"
& $PY "$P\stamp.py" "$P\_proof.pdf" "$P\proof.pdf"
Copy-Item "$P\_back.pdf" "$P\back.pdf" -Force
& $PY "$P\verify.py" "$P\front.pdf" "$P\back.pdf" "$P\proof.pdf"
& $PY -c @"
import pymupdf
from PIL import Image
for n,dpi in (('proof',150),('front',300),('back',300)):
    d = pymupdf.open(rf'$P\{n}.pdf')
    pix = d[0].get_pixmap(dpi=dpi)
    Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(rf'$P\{n}.png')
"@
