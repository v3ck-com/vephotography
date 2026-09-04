# Van Eck Photography

A self-contained static version of the Van Eck Photography website, prepared for GitHub Pages.

## Local preview

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Rebuild

The downloaded site content is stored in `assets/data/site-data.json`. To regenerate the ten static pages after changing the shared templates, run:

```sh
python3 scripts/build_site.py
```

Forms from the original site are intentionally omitted. Contact actions open WhatsApp for `+27 69 800 7288`.

The original crawl inventory is retained in `scripts/source-data.json`; `scripts/download_assets.py` can use it to reacquire the media if the local asset folder ever needs rebuilding.

Before a public release, `scripts/strip_image_metadata.py` removes EXIF, XMP, IPTC, Photoshop, and comment metadata without recompressing the photographs.
