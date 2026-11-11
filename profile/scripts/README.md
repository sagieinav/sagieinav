# How this profile is built

The profile README mixes hand-written text with generated art. Everything generated comes from
one config file and one script:

```
profile.toml            what the profile shows: fonts, colours, banner, skill rows, tools, projects, contacts
scripts/build.py        draws every asset into assets/gen/ and rewrites the README's gen blocks
scripts/clean_scene.py  one-off retouch of the banner art (posters and a mug removed)
assets/src/             source images: the pixel-art scene (raw + retouched), the SQL drawing
assets/thumbs/          2:1 project thumbnails (536x268) used by the cards
assets/icons/           local logos (LinkedIn)
assets/gen/             build output only, never edited by hand
```

## Workflow

```bash
pip install -r scripts/requirements.txt      # Python 3.11+
python3 scripts/build.py --check             # validate profile.toml, write nothing
python3 scripts/build.py                     # draw assets + refresh README blocks
```

Then commit `README.md`, `profile.toml` and `assets/` together.

- **Generated blocks.** Text between `<!-- gen:NAME -->` and `<!-- /gen:NAME -->` in `README.md` is
  overwritten on every build (`banner`, `skills`, `studying`, `projects`, `contact`). Everything
  else in the README is hand-written and never touched.
- **File names carry a content hash** (`card-monotask-dark.be107180.svg`). GitHub's `/raw/`
  redirect drops query strings, so `?v=2` can't bust caches; a new name can. The build deletes
  files it no longer produces.
- **MonoTask fonts** (Gloock, Google Sans Flex, Harabara) are read from `app_fonts` in
  `profile.toml` (the MonoTask repo), never copied here. Harabara is demo-licensed.

## Common changes

| Change | Where |
|---|---|
| Add a skill icon | add it under `[tools]`, then list its key in a `[[skill_rows]]` (max 6 per row) |
| A logo crowds its tile | add `scale = 0.8` to that tool |
| Tool without a skillicons icon | `icon = "sk:<name>"` (github.com/syvixor/skills-icons) or a `draw:` function in `build.py` |
| New project card | `[[projects]]` + a 2:1 thumbnail in `assets/thumbs/` |
| Tag colour | add the tag to a `[tag_categories.*]` list (unlisted tags are neutral grey) |
| Banner text or size | `[banner]` |
| Fonts | `[fonts.*]` (`google:` paths or `app:` files, with variable-font `axes`) |

## Why things look the way they do

- GitHub serves README images as sandboxed `<img>`: SVGs can't load fonts or files, so text is
  drawn as paths and images are inlined as `data:` URIs.
- GitHub strips CSS, `<nobr>` and table border control. Responsive layout uses `<picture>` with
  `media` queries (theme + viewport width), which GitHub keeps: wider labels and smaller icons
  under 768px keep every skill row on its own line on phones.
- Every image has real alt text; skill names also appear in alt/title, and the intro repeats the
  key facts as plain text for scrapers that ignore images.
