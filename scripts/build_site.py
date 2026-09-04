#!/usr/bin/env python3
"""Generate the static multi-page Van Eck Photography website."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "assets/data/site-data.json").read_text(encoding="utf-8"))
WHATSAPP = "https://wa.me/27698007288?text=Hello%20Catelyn%2C%20I%27m%20interested%20in%20booking%20a%20photography%20session."

ROUTES = {
    "/": "Home",
    "/about/": "About",
    "/price-list/": "Price List & Wedding Packages",
    "/portfolio/": "Portfolio",
    "/contact/": "Contact",
}

PORTFOLIO_LINKS = [
    ("Wedding", "/wedding/"),
    ("Engagement", "/engagement/"),
    ("Couples", "/fashion/"),
    ("Families", "/casual/"),
    ("Graduations, Events & Other", "/families-copy/"),
]

PORTFOLIO_CARDS = [
    ("Weddings", "to have and to hold", "/wedding/"),
    ("Engagements", "yes to forever", "/engagement/"),
    ("Couples", "can't be without you", "/fashion/"),
    ("Families", "born to be together", "/casual/"),
    ("Kitchen teas, Events, Graduations & Other", "let's celebrate", "/families-copy/"),
]

GALLERY_TITLES = {
    "/wedding/": "Weddings",
    "/engagement/": "Engagements",
    "/fashion/": "Couples",
    "/casual/": "Families",
    "/families-copy/": "Events, Graduations & Other",
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def prefix(route: str) -> str:
    return "" if route == "/" else "../"


def href(route: str, destination: str) -> str:
    base = prefix(route)
    if destination == "/":
        return f"{base}index.html"
    return f"{base}{destination.strip('/')}/"


def asset(route: str, path: str) -> str:
    return prefix(route) + path


def header(route: str) -> str:
    main_links = []
    for destination, label in ROUTES.items():
        current = " is-current" if destination == route else ""
        if destination == "/portfolio/":
            dropdown = "".join(
                f'<a href="{href(route, item_route)}">{esc(label)}</a>'
                for label, item_route in PORTFOLIO_LINKS
            )
            main_links.append(
                f'<li class="nav-item has-dropdown{current}"><a href="{href(route, destination)}">{esc(label)}</a>'
                f'<div class="dropdown">{dropdown}</div></li>'
            )
        else:
            main_links.append(
                f'<li class="nav-item{current}"><a href="{href(route, destination)}">{esc(label)}</a></li>'
            )
    return f"""
    <header class="site-header">
      <a class="brand" href="{href(route, '/')}">
        <img src="{asset(route, 'assets/images/shared/logo.png')}" alt="Van Eck Photography">
      </a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-navigation">
        <span></span><span></span><span></span><span class="sr-only">Toggle navigation</span>
      </button>
      <nav id="site-navigation" aria-label="Primary navigation">
        <ul>{''.join(main_links)}</ul>
      </nav>
    </header>
    """


def whatsapp_button(label: str = "Contact me on WhatsApp") -> str:
    return f"""
      <a class="whatsapp-button" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">
        <img src="assets/icons/whatsapp.svg" alt="" aria-hidden="true">
        <span>{esc(label)}</span>
      </a>
    """


def routed_whatsapp_button(route: str, label: str = "Contact me on WhatsApp") -> str:
    return whatsapp_button(label).replace('src="assets/', f'src="{prefix(route)}assets/')


def footer(route: str) -> str:
    return f"""
    <footer class="site-footer">
      <p>© 2026 Van Eck Photography</p>
      <div class="social-links" aria-label="Social media">
        <a href="https://www.facebook.com/profile.php?id=61556693330722&amp;mibextid=LQQJ4d" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8.5V6.7c0-.8.5-1 1-1h2.8V2.1L15 2c-3.2 0-5 1.9-5 5.3v1.2H7v4h3V22h4v-9.5h3.2l.5-4H14Z"/></svg>
        </a>
        <a href="https://www.instagram.com/vaneck.photography" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.5 2h9A5.5 5.5 0 0 1 22 7.5v9a5.5 5.5 0 0 1-5.5 5.5h-9A5.5 5.5 0 0 1 2 16.5v-9A5.5 5.5 0 0 1 7.5 2Zm0 2A3.5 3.5 0 0 0 4 7.5v9A3.5 3.5 0 0 0 7.5 20h9a3.5 3.5 0 0 0 3.5-3.5v-9A3.5 3.5 0 0 0 16.5 4h-9ZM17 5.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/></svg>
        </a>
      </div>
    </footer>
    """


def shell(route: str, title: str, content: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{esc(description)}">
  <meta name="theme-color" content="#f3f2ee">
  <title>{esc(title)} | Van Eck Photography</title>
  <link rel="icon" type="image/png" href="{asset(route, 'assets/images/shared/logo.png')}">
  <link rel="stylesheet" href="{asset(route, 'assets/css/styles.css')}">
  <script src="{asset(route, 'assets/js/site.js')}" defer></script>
</head>
<body data-route="{esc(route)}">
  <a class="skip-link" href="#main-content">Skip to content</a>
  {header(route)}
  <main id="main-content">{content}</main>
  {footer(route)}
</body>
</html>
"""


def carousel(route: str, images: list[str], label: str) -> str:
    slides = []
    for index, image in enumerate(images):
        loading = "eager" if index < 3 else "lazy"
        slides.append(
            f'<figure class="carousel-slide"><img src="{asset(route, image)}" '
            f'alt="{esc(label)} — photograph {index + 1}" loading="{loading}" decoding="async"></figure>'
        )
    return f"""
      <div class="carousel" data-carousel aria-label="{esc(label)} photo gallery">
        <button class="carousel-arrow previous" type="button" aria-label="Previous photograph">‹</button>
        <div class="carousel-track">{''.join(slides)}</div>
        <button class="carousel-arrow next" type="button" aria-label="Next photograph">›</button>
        <p class="carousel-count"><span>1</span> / {len(images)}</p>
      </div>
    """


def home_page() -> str:
    route = "/"
    blocks = DATA[route]["blocks"]
    hero_image = blocks[0]["images"][0]
    feature_images = blocks[3]["images"]
    instagram_images = blocks[5]["images"]
    feature_data = [
        ("Weddings", "/wedding/"),
        ("Engagements", "/engagement/"),
        ("Events & Others", "/families-copy/"),
    ]
    instagram_links = [
        "https://www.instagram.com/p/DcjFoAiiD-M/",
        "https://www.instagram.com/reel/DbVXMoko0rT/",
        "https://www.instagram.com/p/Dazr33ICKT_/",
        "https://www.instagram.com/p/DapkYm5iA59/",
        "https://www.instagram.com/reel/DapTKKjI3cw/",
    ]
    features = "".join(
        f'<a class="feature-card" href="{href(route, destination)}">'
        f'<img src="{asset(route, image)}" alt="{esc(label)} photography" loading="lazy">'
        f'<span>{esc(label)}</span></a>'
        for (label, destination), image in zip(feature_data, feature_images)
    )
    instagram = "".join(
        f'<a href="{link}" target="_blank" rel="noopener noreferrer">'
        f'<img src="{asset(route, image)}" alt="Recent Van Eck Photography Instagram post" loading="lazy"></a>'
        for link, image in zip(instagram_links, instagram_images)
    )
    content = f"""
      <section class="home-hero">
        <img src="{asset(route, hero_image)}" alt="Van Eck Photography portfolio collage">
      </section>
      <section class="intro-section">
        <h1>Welcome to Van Eck Photography</h1>
        <p>Capturing your special moments brings me the greatest joy!</p>
      </section>
      <section class="featured-work">
        <h2>See My Work</h2>
        <div class="feature-grid">{features}</div>
        <a class="outline-button" href="{href(route, '/portfolio/')}">See More Galleries</a>
      </section>
      <section class="instagram-section">
        <p class="eyebrow">Follow me on Instagram</p>
        <div class="instagram-grid">{instagram}</div>
        <a class="instagram-handle" href="https://www.instagram.com/vaneck.photography" target="_blank" rel="noopener noreferrer">@vaneck.photography</a>
      </section>
      <section class="contact-cta">
        <h2>Let’s create something beautiful</h2>
        <p>Tell me about the moments you would love to preserve.</p>
        {routed_whatsapp_button(route)}
      </section>
    """
    return shell(route, "Home", content, "Warm, natural wedding, couples, family and event photography by Van Eck Photography.")


def about_page() -> str:
    route = "/about/"
    page = DATA[route]
    portrait = page["blocks"][0]["images"][0]
    paragraphs = page["paragraphs"][:4]
    copy_html = "".join(f"<p>{esc(text)}</p>" for text in paragraphs)
    slider = next(block for block in page["blocks"] if "block-photo-slider" in block["className"])
    content = f"""
      <section class="about-intro">
        <img src="{asset(route, portrait)}" alt="Catelyn and Johan Van Eck" class="about-portrait">
        <div class="about-copy"><h1>Hello! I’m Catelyn.</h1>{copy_html}</div>
      </section>
      <section class="about-gallery">{carousel(route, slider['images'], 'Life behind the scenes')}</section>
      <section class="contact-cta compact"><h2>Ready to connect?</h2>{routed_whatsapp_button(route)}</section>
    """
    return shell(route, "About", content, "Meet Catelyn, the photographer behind Van Eck Photography.")


def price_page() -> str:
    route = "/price-list/"
    image = DATA[route]["blocks"][2]["images"][0]
    content = f"""
      <section class="page-heading price-heading"><h1>Price List &amp; Wedding Packages</h1><h2>2026 Price list</h2></section>
      <section class="price-sheet"><img src="{asset(route, image)}" alt="Van Eck Photography 2026 price list"></section>
      <section class="contact-cta compact"><h2>Have a question?</h2>{routed_whatsapp_button(route)}</section>
    """
    return shell(route, "Price List", content, "Van Eck Photography session prices and wedding packages for 2026.")


def portfolio_page() -> str:
    route = "/portfolio/"
    images = DATA[route]["blocks"][1]["images"]
    cards = []
    for index, ((title, subtitle, destination), image) in enumerate(zip(PORTFOLIO_CARDS, images)):
        cards.append(f"""
          <a class="portfolio-card {'reverse' if index % 2 else ''}" href="{href(route, destination)}">
            <img src="{asset(route, image)}" alt="{esc(title)} photography" loading="{'eager' if index == 0 else 'lazy'}">
            <span class="portfolio-card-copy"><strong>{esc(title)}</strong><small>{esc(subtitle)}</small><i>View gallery</i></span>
          </a>
        """)
    content = f"""
      <section class="portfolio-intro">
        <p>The most important part when I take your photos is that you are comfortable and 100% yourself.</p>
        <p>If being in front of the camera is not your second nature — don’t worry. It’s part of my role to guide you all the way!</p>
      </section>
      <section class="portfolio-list">{''.join(cards)}</section>
    """
    return shell(route, "Portfolio", content, "Explore wedding, engagement, couples, family, graduation and event photography.")


def gallery_page(route: str) -> str:
    page = DATA[route]
    gallery_blocks = [block for block in page["blocks"] if "block-photo-slider" in block["className"]]
    albums: list[tuple[str, str]] = []
    headings = page["headings"]
    for index, heading in enumerate(headings):
        if heading["tag"] == "H3":
            location = ""
            for following in headings[index + 1:]:
                if following["tag"] == "H3":
                    break
                if following["tag"] == "H5" and "/" not in following["text"]:
                    location = following["text"]
                    break
            albums.append((heading["text"], location))
    sections = []
    for block, (title, location) in zip(gallery_blocks, albums):
        sections.append(f"""
          <section class="album-section">
            <div class="album-heading"><h2>{esc(title)}</h2>{f'<p>{esc(location)}</p>' if location else ''}</div>
            {carousel(route, block['images'], title)}
          </section>
        """)
    page_title = GALLERY_TITLES[route]
    content = f'<section class="page-heading gallery-heading"><h1>{esc(page_title)}</h1></section>{"".join(sections)}'
    return shell(route, page_title, content, f"{page_title} photography portfolio by Van Eck Photography.")


def contact_page() -> str:
    route = "/contact/"
    paragraphs = DATA[route]["paragraphs"][:2]
    content = f"""
      <section class="contact-page">
        <div class="contact-copy">
          <h1>Let’s Connect</h1>
          <p>{esc(paragraphs[0])}</p>
          <p>{esc(paragraphs[1])}</p>
          {routed_whatsapp_button(route, 'Message me on WhatsApp')}
          <p class="phone-number">+27 69 800 7288</p>
        </div>
      </section>
    """
    return shell(route, "Contact", content, "Contact Van Eck Photography on WhatsApp to discuss your photography session.")


def write_page(route: str, content: str) -> None:
    destination = ROOT / ("index.html" if route == "/" else route.strip("/") + "/index.html")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def main() -> None:
    write_page("/", home_page())
    write_page("/about/", about_page())
    write_page("/price-list/", price_page())
    write_page("/portfolio/", portfolio_page())
    write_page("/contact/", contact_page())
    for route in GALLERY_TITLES:
        write_page(route, gallery_page(route))
    print("Generated 10 static pages")


if __name__ == "__main__":
    main()
