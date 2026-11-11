#!/usr/bin/env python3
"""Build every generated asset of the profile from profile.toml and refresh README.md.

    pip install -r scripts/requirements.txt     # Python 3.11+
    python3 scripts/build.py                    # build assets + README blocks
    python3 scripts/build.py --check            # validate profile.toml only, write nothing

See scripts/README.md for how the pieces fit together.

Why SVGs drawn this way: GitHub shows README images through a sandboxed <img>, so an SVG can't
load fonts or other files. Every glyph is turned into a <path> and every image is inlined as a
data: URI. Output files are named <stem>.<content hash>.svg: GitHub's /raw/ redirect drops query
strings, so a new file name is the only way to make sure nobody sees a cached old image.
"""
import base64
import hashlib
import html
import pathlib
import re
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "profile.toml"
README = ROOT / "README.md"
GEN = ROOT / "assets" / "gen"
ICONS = ROOT / "assets" / "icons"
THUMBS = ROOT / "assets" / "thumbs"
CACHE = ROOT / ".cache"

GOOGLE_FONTS = "https://raw.githubusercontent.com/google/fonts/main/ofl/{}"
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@16.30.0/icons/{}.svg"
SKILLICONS = "https://skillicons.dev/icons?i={}"
SKILLS_ICONS = "https://raw.githubusercontent.com/syvixor/skills-icons/a4847b091ad40968b801819da854a053a1620d0d/icons/{}.svg"

# skillicons.dev tile geometry (256-unit square): corner radius, fill, logo box, gap between tiles
TILE_RX, TILE_FILL, LOGO_BOX, TILE_GAP = 60, "#242938", (38, 218), 44
SK_LOGO_BOX = (51, 206)  # where skills-icons draws its logo inside its own tile
ROW_H, LABEL_W, CARD_W = 48, 170, 268
# Icon variants: (tile px, transparent gap px on its right). Gaps live inside the image so icons sit
# flush in markup. Phones get smaller tiles and gaps: six must fit a 294px column (a 360px phone).
ICON_DESKTOP, ICON_PHONE = (48, 8), (46, 3)


# ================================================================ basics
def fetch(url):
    CACHE.mkdir(exist_ok=True)
    dest = CACHE / re.sub(r"[^A-Za-z0-9._-]", "_", url.split("://", 1)[1])
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "profile-builder"})
        try:
            dest.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        except (urllib.error.URLError, TimeoutError) as e:
            sys.exit(f"download failed: {url}\n  {e}\n  (check the id/name in profile.toml, or your connection)")
    return dest.read_bytes()


def data_uri(raw, mime):
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def esc(text):
    return html.escape(text, quote=True)


def svg_doc(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
            f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{esc(title)}">'
            f"<title>{esc(title)}</title>{body}</svg>")


def mix(a, b, t):
    """Linear blend of two hex colours, like Compose's lerp(a, b, t)."""
    ca = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


class Output:
    """Writes content-hashed files into assets/gen and removes the ones a build didn't produce."""

    def __init__(self):
        GEN.mkdir(parents=True, exist_ok=True)
        self.written = set()

    def save(self, stem, svg):
        name = f"{stem}.{hashlib.sha1(svg.encode()).hexdigest()[:8]}.svg"
        (GEN / name).write_text(svg)
        self.written.add(name)
        return f"assets/gen/{name}"

    def prune(self):
        for f in GEN.glob("*.svg"):
            if f.name not in self.written:
                f.unlink()


# ================================================================ fonts
class Font:
    def __init__(self, raw, weight=400, axes=None, space_scale=1.0, fake_bold=0.0):
        CACHE.mkdir(exist_ok=True)
        key = hashlib.sha1(raw).hexdigest()[:12]
        path = CACHE / f"font-{key}.ttf"
        if not path.exists():
            path.write_bytes(raw)
        font = TTFont(path)
        if "fvar" in font:
            have = {a.axisTag for a in font["fvar"].axes}
            pins = {k: v for k, v in {"wght": weight, **(axes or {})}.items() if k in have}
            font = instancer.instantiateVariableFont(font, pins)
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.hmtx = font["hmtx"]
        self.upm = font["head"].unitsPerEm
        os2 = font["OS/2"] if "OS/2" in font else None
        self.cap = (getattr(os2, "sCapHeight", 0) or 0.7 * self.upm) / self.upm
        self.space_scale = space_scale  # < 1 tightens word gaps
        self.fake_bold = fake_bold      # Android-style synthetic bold amount (tags only)

    def _glyph(self, ch):
        return self.cmap.get(ord(ch), ".notdef")

    def _advance(self, name, ch):
        adv = self.hmtx[name][0]
        return adv * self.space_scale if ch == " " else adv

    def width(self, text, size):
        return sum(self._advance(self._glyph(c), c) for c in text) * size / self.upm

    def path(self, text, x, baseline, size, fill, extra=""):
        scale = size / self.upm
        pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        advance = 0
        for ch in text:
            name = self._glyph(ch)
            self.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x + advance * scale, baseline)))
            advance += self._advance(name, ch)
        return f'<path fill="{fill}" {extra}d="{pen.getCommands()}"/>'


def load_fonts(cfg):
    app_dir = pathlib.Path(cfg["app_fonts"]).expanduser()
    fonts = {}
    for role, spec in cfg["fonts"].items():
        kind, _, rel = spec["file"].partition(":")
        if kind == "app":
            path = app_dir / rel
            if not path.exists():
                sys.exit(f"font '{role}': {path} not found (set app_fonts in profile.toml)")
            raw = path.read_bytes()
        else:
            raw = fetch(GOOGLE_FONTS.format(urllib.parse.quote(rel)))
        fonts[role] = Font(raw, spec.get("weight", 400), spec.get("axes"),
                           spec.get("space_scale", 1.0), spec.get("fake_bold", 0.0))
    return fonts


def wrap(text, font, size, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if font.width(trial, size) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line]


# ================================================================ icons
def icon_uri(spec, color):
    """'si:<slug>' (one-colour Simple Icon, drawn in `color`) or 'file:<name>' from assets/icons."""
    kind, _, value = spec.partition(":")
    if kind == "si":
        svg = fetch(SIMPLE_ICONS.format(value)).decode().replace("<svg ", f'<svg fill="{color}" ', 1)
        return data_uri(svg.encode(), "image/svg+xml")
    return data_uri((ICONS / value).read_bytes(), "image/svg+xml")


def mono_icon(spec, fg, bg):
    """Icon in a tag's text colour. LinkedIn's file is two-tone: its white 'in' takes the fill colour."""
    if spec == "file:linkedin.svg":
        svg = (ICONS / "linkedin.svg").read_text().replace("#0076b2", fg).replace("#fff", bg)
        return data_uri(svg.encode(), "image/svg+xml")
    return icon_uri(spec, fg)


def draw_sql(scale=1.0):
    """SQL: the outline drawing in assets/src/sql.png, recoloured (drum blue, lettering white).
    The lettering is shrunk to 70% (anchored bottom-left, against the drum) and the result is
    centred on its real ink bounds, so the drum sits near the middle of the tile."""
    from PIL import Image
    import io
    import numpy as np
    src = np.asarray(Image.open(ROOT / "assets/src/sql.png").convert("RGBA")).astype(np.float32)
    ink = (src[..., 3] / 255) * (1 - src[..., :3].mean(axis=-1) / 255)   # black lines -> opaque
    letters = np.zeros(ink.shape, bool); letters[350:, 240:] = True

    def layer(mask, rgb):
        out = np.zeros(src.shape, np.uint8)
        out[...] = rgb + [0]
        out[..., 3] = np.where(mask, ink, 0) * 255
        return Image.fromarray(out, "RGBA")

    drum = layer(~letters, [0x5A, 0xAE, 0xFF])
    text = layer(letters, [0xFF, 0xFF, 0xFF]).crop((240, 350, 512, 512))
    tb = text.getbbox()
    text = text.crop(tb)
    k_text = 0.7
    text = text.resize((round(text.width * k_text), round(text.height * k_text)), Image.LANCZOS)
    canvas = drum.copy()
    canvas.alpha_composite(text, (240 + tb[0], 350 + tb[3] - text.height))  # keep left + baseline
    canvas = canvas.crop(canvas.getbbox())
    buf = io.BytesIO()
    canvas.save(buf, "PNG", optimize=True)
    box = (LOGO_BOX[1] - LOGO_BOX[0]) * scale
    k = box / max(canvas.size)
    w, h = canvas.width * k, canvas.height * k
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="none">'
            f'<rect width="256" height="256" rx="{TILE_RX}" fill="{TILE_FILL}"/>'
            f'<image x="{128 - w / 2:.2f}" y="{128 - h / 2:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'href="{data_uri(buf.getvalue(), "image/png")}"/></svg>')


DRAWN = {"sql": draw_sql}


def tile(icon_id, scale=1.0):
    """One 256-unit tile in skillicons' exact shape, as SVG markup. scale < 1 shrinks the logo
    inside the tile (for logos drawn edge to edge)."""
    if icon_id.startswith("draw:"):
        return DRAWN[icon_id[5:]](scale)
    if not icon_id.startswith("sk:"):
        return fetch(SKILLICONS.format(icon_id)).decode()
    svg = fetch(SKILLS_ICONS.format(icon_id[3:])).decode()
    svg = re.sub(r"<style>.*?</style>", "", svg, flags=re.S)
    inner = svg[svg.index(">") + 1:svg.rindex("</svg>")]
    inner = re.sub(r"<rect[^>]*/>", "", inner, count=1)   # drop skills-icons' own tile background
    k = (LOGO_BOX[1] - LOGO_BOX[0]) / (SK_LOGO_BOX[1] - SK_LOGO_BOX[0]) * scale  # fit skillicons' box
    shift = 128 - 128 * k
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="none">'
            f'<rect width="256" height="256" rx="{TILE_RX}" fill="{TILE_FILL}"/>'
            f'<g transform="translate({shift:.2f} {shift:.2f}) scale({k:.4f})">{inner}</g></svg>')


# ================================================================ tags (MonoTask TaskTag.kt)
def tag_color(label, cfg):
    """A tag's text colour: its category's colour, else the neutral one."""
    key = label.lower()
    for category in cfg.get("tag_categories", {}).values():
        if key in (t.lower() for t in category["tags"]):
            return category["color"]
    return cfg["tag_neutral"]


def tag_style(label, theme_name, cfg, color=None):
    """(fill, border, border_opacity, text, text_opacity) from one text colour.
    Light follows TaskTag.kt (tinted fill, border = lerp(Black, content, 0.85) at 20%, text at 85%);
    MonoTask has no dark tags, so dark uses a deep tint for the fill and a lightened text colour."""
    c = color or tag_color(label, cfg)
    if theme_name == "light":
        fg = mix(c, "#000000", 0.12)
        return mix("#FFFFFF", c, 0.12), mix("#000000", fg, 0.85), 0.2, fg, 0.85
    light_fg = mix(c, "#FFFFFF", 0.55)
    return mix(cfg["theme"]["dark"]["card"], c, 0.28), light_fg, 0.35, light_fg, 1.0


def tag(label, x, y, size, theme_name, cfg, font, icon=None, color=None, shape="pill"):
    """Draw a tag at (x, y); returns (svg, w, h). Geometry scales from MonoTask's 14sp tag."""
    k = size / 14
    text = label.lower()
    bg, border, border_op, fg, fg_op = tag_style(label, theme_name, cfg, color)
    pad, bw = 8 * k, 1.5 * k
    h = size * 1.05 + 4 * k + 2 * bw
    icon_w, gap = (size, 4 * k) if icon else (0, 0)
    w = pad * 2 + icon_w + gap + font.width(text, size)
    rx = (h - bw) / 2 if shape == "pill" else 6 * k
    parts = [f'<rect x="{x + bw / 2:.2f}" y="{y + bw / 2:.2f}" width="{w - bw:.2f}" height="{h - bw:.2f}" '
             f'rx="{rx:.2f}" fill="{bg}" stroke="{border}" stroke-opacity="{border_op}" stroke-width="{bw:.2f}"/>']
    tx = x + pad
    if icon:
        parts.append(f'<image x="{tx:.2f}" y="{y + (h - icon_w) / 2:.2f}" width="{icon_w:.2f}" '
                     f'height="{icon_w:.2f}" href="{mono_icon(icon, fg, bg)}"/>')
        tx += icon_w + gap
    # Android's fake bold: stroke width = size * lerp(1/24 at 9px, 1/32 at 36px)
    t = min(max((size - 9) / 27, 0), 1)
    stroke = size * (1 / 24 + (1 / 32 - 1 / 24) * t) * font.fake_bold
    parts.append(font.path(text, tx, y + h / 2 + font.cap * size / 2, size, fg,
                           f'fill-opacity="{fg_op}" stroke="{fg}" stroke-opacity="{fg_op}" '
                           f'stroke-width="{stroke:.2f}" stroke-linejoin="round" '))
    return "".join(parts), w, h


# ================================================================ builders (each returns README markdown)
def picture(dark, light, alt, attrs=""):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{dark}">'
            f'<img{attrs} alt="{esc(alt)}" src="{light}"></picture>')


def build_banner(cfg, fonts, out):
    b = cfg["banner"]
    w, h = b["width"], b["height"]
    cx, cy, cw, ch = b["crop"]
    from PIL import Image  # only the banner needs Pillow
    import io
    scene = Image.open(ROOT / b["scene"]).convert("RGB").crop((cx, cy, cx + cw, cy + ch))
    iw = round(h * cw / ch)
    scene = scene.resize((iw * 2, h * 2), Image.LANCZOS)  # 2x for sharp screens
    buf = io.BytesIO()
    scene.save(buf, "JPEG", quality=88)
    img = data_uri(buf.getvalue(), "image/jpeg")
    files = {}
    for theme_name, t in cfg["theme"].items():
        tx = iw + 36
        room = w - tx - 26
        name_size, title_size = b["name_size"], b["title_size"]  # shrunk below only if they don't fit
        while fonts["display"].width(b["name"], name_size) > room:
            name_size -= 1
        while fonts["body"].width(b["title"], title_size) > room:
            title_size -= 1
        body = (f'<defs><clipPath id="card"><rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16"/></clipPath>'
                f'<linearGradient id="fade"><stop offset="0" stop-color="{t["card"]}" stop-opacity="0"/>'
                f'<stop offset="1" stop-color="{t["card"]}"/></linearGradient></defs>'
                f'<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="{t["card"]}"/>'
                f'<image width="{iw}" height="{h}" href="{img}"/>'
                f'<rect x="{iw - 60}" width="60" height="{h}" fill="url(#fade)"/></g>'
                f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{t["line"]}"/>'
                + fonts["display"].path(b["name"], tx, h * 0.47, name_size, t["text"])
                + f'<rect x="{tx + 2}" y="{h * 0.47 + 16:.0f}" width="44" height="5" rx="2.5" fill="{t["accent"]}"/>'
                + fonts["body"].path(b["title"], tx, h * 0.47 + 66, title_size, t["muted"]))
        files[theme_name] = out.save(f"banner-{theme_name}", svg_doc(w, h, body, f'{b["name"]}: {b["title"]}'))
    return picture(files["dark"], files["light"], b["alt"], ' width="100%"')


# On phones a label must fill its line, or the first icons would sit beside it and the rest wrap
# below. GitHub strips <nobr>, so instead narrow screens get a wider label (same text, transparent
# space on the right) through <picture> media queries. (max viewport, label width) pairs:
LABEL_TIERS = [(430, 330), (767, 560)]


def build_rows(cfg, fonts, out, block):
    """Label image + one linked image per icon (alt = tool name, link = tool site)."""
    lines = []
    for row in [r for r in cfg["skill_rows"] if r["block"] == block]:
        slug = re.sub(r"[^a-z0-9]+", "-", row["label"].lower()).strip("-")
        files = {}  # (theme, width) -> path
        for theme_name, t in cfg["theme"].items():
            body = (f'<rect x="0" y="14" width="4" height="20" rx="2" fill="{t["accent"]}"/>'
                    + fonts["label"].path(row["label"], 14, 30, 16, t["text"]))
            for width in [LABEL_W] + [w for _, w in LABEL_TIERS]:
                files[theme_name, width] = out.save(f"label-{slug}-{theme_name}-{width}",
                                                    svg_doc(width, ROW_H, body, row["label"]))
        sources = []
        for max_vw, width in LABEL_TIERS:
            q = f"(max-width: {max_vw}px)"
            sources.append(f'<source media="(prefers-color-scheme: dark) and {q}" srcset="{files["dark", width]}">')
            sources.append(f'<source media="{q}" srcset="{files["light", width]}">')
        sources.append(f'<source media="(prefers-color-scheme: dark)" srcset="{files["dark", LABEL_W]}">')
        label = (f'<picture>{"".join(sources)}<img alt="{esc(row["label"])}:" '
                 f'src="{files["light", LABEL_W]}"></picture>')
        links = []
        for key in row["icons"]:
            tool = cfg["tools"][key]
            tile_uri = data_uri(tile(tool["icon"], tool.get("scale", 1.0)).encode(), "image/svg+xml")
            src = {}
            for name, (size, gap) in {"desktop": ICON_DESKTOP, "phone": ICON_PHONE}.items():
                w, y = size + gap, (ROW_H - size) / 2
                svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{ROW_H}" viewBox="0 0 {w} {ROW_H}" '
                       f'role="img" aria-label="{esc(tool["name"])}"><title>{esc(tool["name"])}</title>'
                       f'<image y="{y}" width="{size}" height="{size}" href="{tile_uri}"/></svg>')
                src[name] = out.save(f"icon-{key}-{name}", svg)
            phone_q = f"(max-width: {LABEL_TIERS[-1][0]}px)"
            links.append(f'<a href="{tool["url"]}"><picture><source media="{phone_q}" srcset="{src["phone"]}">'
                         f'<img src="{src["desktop"]}" alt="{esc(tool["name"])}" title="{esc(tool["name"])}"></picture></a>')
        lines.append(label + " " + "".join(links))
    return "<br>\n".join(lines)


def card_parts(p, theme_name, t, cfg, fonts):
    """Title, wrapped pitch and flowing tags for one card; returns (svg parts, content height)."""
    w, th, pad = CARD_W, CARD_W / 2, 14
    y = th + pad + 17
    parts = [fonts["title"].path(p["title"], pad, y, 17.5, t["text"])]
    for line in wrap(p["pitch"], fonts["body"], 12.5, w - 2 * pad):
        y += 18.5
        parts.append(fonts["body"].path(line, pad, y, 12.5, t["muted"]))
    y += 11
    x, row_h = pad, 0
    for label in p["tags"]:  # flow layout: wrap to a new line when the row is full
        svg, tw, tag_h = tag(label, 0, 0, 11, theme_name, cfg, fonts["tag"])
        if x + tw > w - pad and x > pad:
            x, y = pad, y + row_h + 5
        parts.append(f'<g transform="translate({x:.2f} {y:.2f})">{svg}</g>')
        x += tw + 5
        row_h = tag_h
    return parts, y + row_h + pad


def build_projects(cfg, fonts, out):
    """Thumbnail cards, all the same height so a row lines up; 268px wide, so 3 fit per desktop
    row and they wrap to one per row on phones."""
    w, th = CARD_W, CARD_W / 2
    files = {}  # (slug, theme) -> path
    for theme_name, t in cfg["theme"].items():
        laid_out = [(p, *card_parts(p, theme_name, t, cfg, fonts)) for p in cfg["projects"]]
        h = max(height for *_, height in laid_out)
        for p, parts, _ in laid_out:
            img = data_uri((THUMBS / p["thumb"]).read_bytes(), "image/jpeg")
            body = (f'<defs><clipPath id="c"><rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12"/></clipPath></defs>'
                    f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{t["card"]}"/>'
                    f'<image width="{w}" height="{th}" preserveAspectRatio="xMidYMid slice" href="{img}"/>'
                    f'<rect y="{th}" width="{w}" height="1" fill="{t["line"]}"/></g>'
                    f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{t["line"]}"/>'
                    + "".join(parts))
            files[p["slug"], theme_name] = out.save(f'card-{p["slug"]}-{theme_name}', svg_doc(w, h, body, card_alt(p)))
    width = f' width="{CARD_W}"'
    links = [f'<a href="{p["url"]}">{picture(files[p["slug"], "dark"], files[p["slug"], "light"], card_alt(p), width)}</a>'
             for p in cfg["projects"]]
    return "&nbsp; ".join(links)  # &nbsp; widens the gap; the plain space still lets cards wrap


def card_alt(p):
    return f'{p["title"]}: {p["pitch"]} Built with {", ".join(p["tags"])}.'


def build_contacts(cfg, fonts, out):
    links = []
    for c in cfg["contacts"]:
        files = {}
        for theme_name in cfg["theme"]:
            body, w, h = tag(c["label"], 1, 1, 16, theme_name, cfg, fonts["tag"], icon=c["icon"],
                             color=c["color"], shape="button")
            files[theme_name] = out.save(f'contact-{c["slug"]}-{theme_name}', svg_doc(w + 2, h + 2, body, c["alt"]))
        links.append(f'<a href="{c["url"]}">{picture(files["dark"], files["light"], c["alt"])}</a>')
    return " ".join(links)


# ================================================================ README
def fill_readme(blocks):
    text = README.read_text()
    for name, markdown in blocks.items():
        start, end = f"<!-- gen:{name} -->", f"<!-- /gen:{name} -->"
        pattern = re.compile(re.escape(start) + ".*?" + re.escape(end), re.S)
        if not pattern.search(text):
            print(f"README: no {start} block, skipped")
            continue
        text = pattern.sub(lambda m: f"{start}\n{markdown}\n{end}", text, count=1)
    README.write_text(text)


# ================================================================ validation
MAX_ROW_ICONS = 6  # the most that fit one line on a 360px phone (see ICON_PHONE)


def validate(cfg):
    """Catch config mistakes before drawing anything, with messages that say where to look."""
    errors = []
    tools = cfg.get("tools", {})
    for key, tool in tools.items():
        for field in ("name", "url", "icon"):
            if field not in tool:
                errors.append(f"[tools.{key}] is missing '{field}'")
        icon = tool.get("icon", "")
        if icon.startswith("draw:") and icon[5:] not in DRAWN:
            errors.append(f"[tools.{key}] icon '{icon}': no drawer named '{icon[5:]}' in build.py (DRAWN)")
    used = set()
    for row in cfg.get("skill_rows", []):
        where = f"skill row '{row.get('label')}'"
        if row.get("block") not in ("skills", "studying"):
            errors.append(f"{where}: block must be 'skills' or 'studying'")
        if len(row.get("icons", [])) > MAX_ROW_ICONS:
            errors.append(f"{where}: {len(row['icons'])} icons, max {MAX_ROW_ICONS} (it would wrap on phones)")
        for key in row.get("icons", []):
            used.add(key)
            if key not in tools:
                errors.append(f"{where}: '{key}' is not defined under [tools]")
    for key in sorted(set(tools) - used):
        print(f"note: [tools.{key}] is defined but not used in any row")
    for p in cfg.get("projects", []):
        if not (THUMBS / p.get("thumb", "")).is_file():
            errors.append(f"project '{p.get('slug')}': thumbnail assets/thumbs/{p.get('thumb')} not found")
    for c in cfg.get("contacts", []):
        kind, _, value = c.get("icon", "").partition(":")
        if kind == "file" and not (ICONS / value).is_file():
            errors.append(f"contact '{c.get('slug')}': assets/icons/{value} not found")
    b = cfg.get("banner", {})
    if b and not (ROOT / b.get("scene", "")).is_file():
        errors.append(f"banner: scene {b.get('scene')} not found")
    for key in ("name_size", "title_size", "alt"):
        if b and key not in b:
            errors.append(f"[banner] is missing '{key}'")
    if errors:
        sys.exit("profile.toml has problems:\n  - " + "\n  - ".join(errors))


def main():
    cfg = tomllib.loads(CONFIG.read_text())
    validate(cfg)
    if "--check" in sys.argv:
        print("profile.toml looks good")
        return
    fonts = load_fonts(cfg)
    out = Output()
    blocks = {
        "banner": build_banner(cfg, fonts, out),
        "skills": build_rows(cfg, fonts, out, "skills"),
        "studying": build_rows(cfg, fonts, out, "studying"),
        "projects": build_projects(cfg, fonts, out),
        "contact": build_contacts(cfg, fonts, out),
    }
    out.prune()
    fill_readme(blocks)
    print(f"built {len(out.written)} files in assets/gen, README blocks: {', '.join(blocks)}")


if __name__ == "__main__":
    main()
