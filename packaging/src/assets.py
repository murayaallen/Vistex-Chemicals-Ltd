"""Prepare embedded assets for the Swift Toilet Blocks carton artwork."""
import base64, json, pathlib
import qrcode
from qrcode.image.svg import SvgPathImage

HERE = pathlib.Path(__file__).parent
OUT = HERE / "assets.json"

# Real, scannable QR -> the company site. The previous artwork's QR was an
# AI-drawn pattern that does not decode.
QR_TARGET = "https://vistexchemicals.co.ke"  # shorter = fewer modules = bigger, more scannable cells
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=0)
qr.add_data(QR_TARGET)
qr.make(fit=True)
svg = qr.make_image(image_factory=SvgPathImage, attrib={"class": "qr"})
qr_svg = svg.to_string().decode("utf8")
(HERE / "qr.svg").write_text(qr_svg, encoding="utf8")

def b64(p):
    return base64.b64encode(pathlib.Path(p).read_bytes()).decode("ascii")

assets = {
    "qr_svg": qr_svg,
    "font_outfit": b64(HERE / "fonts/outfit-2.woff2"),
    "font_outfit_ext": b64(HERE / "fonts/outfit-1.woff2"),
    "font_jakarta": b64(HERE / "fonts/jakarta-4.woff2"),
    "vistex": b64(r"D:\Projects\Vistex\images\logo\vistex-logo-color-on-white.png"),
    "vistex_white": b64(r"D:\Projects\Vistex\images\logo\vistex-logo-white-on-blue.png"),
}
OUT.write_text(json.dumps(assets), encoding="utf8")
print("qr modules:", qr.modules_count, "| target:", QR_TARGET)
print("assets.json", OUT.stat().st_size // 1024, "KB")
