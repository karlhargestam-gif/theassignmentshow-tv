#!/usr/bin/env python3
"""Build per-episode pages from the homepage episode cards.

The homepage article list is the catalog (titles, descriptions, YouTube URLs).
This script gives each episode its own URL, unique head metadata, TVEpisode and
VideoObject JSON-LD, breadcrumbs, and previous/next links. Verified video dates
and episode thumbnails come from .github/data/video-metadata.json. Unknown
dates stay absent: never substitute a site rebuild date or invent an air date.

Re-run after editing an episode card in index.html:

    python3 .github/scripts/build_episodes.py
    python3 .github/scripts/build_episodes.py --check
"""

from __future__ import annotations

import json
import re
import sys
from html import escape, unescape
from video_metadata import load_video_metadata


def html_text(value: str) -> str:
    """Escape markup but keep apostrophes, matching the copy already on the homepage."""
    return escape(value, quote=False).replace('"', "&quot;")
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOST = "www.theassignmentshow.tv"
ORIGIN = f"https://{HOST}"
SITEMAP_LASTMOD = "2026-10-27"
HERO_ALT = "The Ethiopian highlands, setting of The Assignment: Ethiopia documentary series"
HERO_IMAGE = f"{ORIGIN}/ethiopia-highlands-hero.jpg"
MARKER = "/* episode pages */"

EXTRA_CSS = f"""{MARKER} */
.episode h3 a{{color:inherit;text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.14em}}
.episode h3 a:hover,.episode h3 a:focus-visible{{color:var(--red)}}
.episode-actions{{display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;margin-top:auto;padding-top:1.1rem}}
.episode .episode-actions .btn{{margin-top:0}}
.skip{{position:absolute;left:1rem;top:0;transform:translateY(-120%);background:#fff;color:#111;padding:.6rem 1rem;z-index:30;font-weight:800;text-decoration:none}}
.skip:focus{{transform:none}}
.visually-hidden{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}
.subnav{{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:.4rem clamp(1.15rem,7vw,7rem);background:#050505;color:#fff}}
.subnav a{{color:#fff;text-decoration:none;font-size:.8125rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}}
.subnav a:hover,.subnav a:focus-visible{{color:#ff5a61}}
.subnav nav{{display:flex;gap:1.2rem;align-items:center}}
.subnav nav a{{display:inline-flex;align-items:center;min-height:48px}}
.subnav .brand{{font-size:1rem;font-weight:900;letter-spacing:-.04em;min-height:48px;display:inline-flex;align-items:center}}
.subnav .watch{{border:1px solid rgba(255,255,255,.65);padding:.62rem .9rem}}
.episode-page h1{{margin:0;max-width:22ch;font-size:clamp(2.4rem,6.2vw,4.6rem);line-height:1.02;letter-spacing:-.045em;font-weight:800;text-transform:none}}
.episode-page .section-inner{{max-width:760px}}
.episode-page .section-label,.episode-page .pager-kicker{{color:#ff5a61;font-size:.8125rem}}
.episode-page footer{{font-size:.8125rem}}
.crumbs{{margin:0 0 1.6rem}}
.crumbs ol{{display:flex;flex-wrap:wrap;align-items:center;gap:.15rem 0;list-style:none;margin:0;padding:0;font-size:.875rem}}
.crumbs li{{display:flex;align-items:center;min-height:48px}}
.crumbs li+li::before{{content:"/";margin:0 .55rem;color:var(--muted)}}
.crumbs a{{color:inherit;text-decoration:underline;text-underline-offset:.14em}}
.synopsis{{font-size:1.125rem;line-height:1.6;max-width:62ch;margin:1.15rem 0 0}}
.watch-row{{margin:1.6rem 0 0}}
.watch-row .btn{{min-height:48px}}
.pager{{display:flex;justify-content:space-between;gap:1rem;margin-top:2.4rem;border-top:1px solid var(--line);padding-top:.4rem}}
.pager a{{display:flex;flex-direction:column;justify-content:center;gap:.2rem;min-height:48px;padding:.85rem 0;text-decoration:none;max-width:46%}}
.pager a[rel="next"]{{margin-left:auto;text-align:right;align-items:flex-end}}
.pager a:hover .pager-title,.pager a:focus-visible .pager-title{{text-decoration:underline;text-underline-offset:.12em}}
.pager-title{{font-size:1.05rem;font-weight:700;letter-spacing:-.02em;line-height:1.25}}
@media (prefers-color-scheme: light){{
  .episode-page .section-label,.episode-page .pager-kicker{{color:var(--red-dark)}}
}}
@media(max-width:760px){{
  .subnav{{padding:.4rem 1.15rem}}
  .subnav nav a:not(.watch){{display:none}}
  .episode .episode-actions{{margin-top:1.3rem;padding-top:0}}
  .pager{{flex-direction:column}}
  .pager a,.pager a[rel="next"]{{max-width:none;margin-left:0;text-align:left;align-items:flex-start}}
}}
"""

# The marker line in EXTRA_CSS is f"{MARKER} */" which would be wrong.
# Keep the constant and the CSS comment identical. Fixed below if needed.

YOUTUBE_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 '
    '31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 '
    '2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z"/></svg>'
)

FONT_LINKS = """  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,ital,wght@6..96,500;6..96,600&family=Libre+Franklin:wght@400;500;600;700;800;900&display=swap" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,ital,wght@6..96,500;6..96,600&family=Libre+Franklin:wght@400;500;600;700;800;900&display=swap"></noscript>"""

FOOTER = """  <footer><div class="foot"><span>© 2026 The Assignment: Ethiopia</span><span>Landscape photography: <a href="https://www.clubmed.be/l/quand-partir-en-ethiopie" target="_blank" rel="noopener">Ethiopia</a></span></div></footer>"""


def plain_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", "", fragment)
    return " ".join(unescape(text).split())


def meta_description(plain: str) -> str:
    """Use the episode's own wording, keeping a verbatim prefix under 160 characters."""
    plain = " ".join(plain.split())
    if len(plain) <= 160:
        return plain
    parts = re.split(r"(?<=[.!?])\s+", plain)
    out = ""
    for part in parts:
        trial = (out + " " + part).strip()
        if len(trial) <= 160:
            out = trial
        else:
            break
    if len(out) >= 80:
        return out
    rest = plain[len(out):].strip()
    budget = 160 - (len(out) + (1 if out else 0))
    chunk = rest[:budget]
    if "," in chunk:
        chunk = chunk.rsplit(",", 1)[0]
    else:
        chunk = chunk.rsplit(" ", 1)[0]
    chunk = chunk.rstrip(",;: ")
    return (out + " " + chunk).strip()


def assert_safe_description(fragment: str) -> None:
    stripped = re.sub(r"</?strong>", "", fragment)
    if "<" in stripped or ">" in stripped:
        raise SystemExit(f"unexpected markup in an episode description: {fragment[:80]!r}")


def parse_episodes(html: str) -> list[dict]:
    articles = re.findall(r'<article class="episode">(.*?)</article>', html, flags=re.S)
    episodes = []
    for art in articles:
        number = int(re.search(r'class="episode-number">(\d+)', art).group(1))
        title_html = re.search(r"<h3>(.*?)</h3>", art, flags=re.S).group(1)
        title = plain_text(title_html)
        description_html = re.search(r"<p>(.*?)</p>", art, flags=re.S).group(1).strip()
        assert_safe_description(description_html)
        youtube = re.search(r"https://youtu\.be/[A-Za-z0-9_-]+", art).group(0)
        episodes.append(
            {
                "n": number,
                "title": title,
                "description_html": description_html,
                "plain": plain_text(description_html),
                "youtube": youtube,
            }
        )
    nums = [ep["n"] for ep in episodes]
    if nums != list(range(1, 14)):
        raise SystemExit(f"expected episodes 1..13 in order, found {nums}")
    titles = [ep["title"] for ep in episodes]
    if len(set(titles)) != len(titles):
        raise SystemExit("episode titles are not unique")
    videos = [ep["youtube"] for ep in episodes]
    if len(set(videos)) != len(videos):
        raise SystemExit("episode video URLs are not unique")
    return episodes


def patch_article(art: str, ep: dict) -> str:
    n = ep["n"]
    title = html_text(ep["title"])
    art = re.sub(
        r"<h3>(?:<a[^>]*>)?(.*?)(?:</a>)?</h3>",
        f'<h3><a href="/episode-{n}/">{title}</a></h3>',
        art,
        count=1,
        flags=re.S,
    )
    view = f'<a class="btn" href="/episode-{n}/">View episode {n}</a>'
    if f">View episode {n}<" not in art:
        art = art.replace(
            f'<a class="btn" href="{ep["youtube"]}"',
            f'<div class="episode-actions">{view}<a class="btn" href="{ep["youtube"]}"',
            1,
        )
        close = art.rfind("</a>")
        if close == -1:
            raise SystemExit(f"episode {n} is missing its YouTube link")
        art = art[: close + 4] + "</div>" + art[close + 4 :]
    return art


def patch_cards(html: str, episodes: list[dict]) -> str:
    by_number = {ep["n"]: ep for ep in episodes}

    def repl(match: re.Match) -> str:
        inner = match.group(1)
        number = int(re.search(r'class="episode-number">(\d+)', inner).group(1))
        return '<article class="episode">' + patch_article(inner, by_number[number]) + "</article>"

    patched, count = re.subn(
        r'<article class="episode">(.*?)</article>', repl, html, flags=re.S
    )
    if count != 13:
        raise SystemExit(f"patched {count} episode cards, expected 13")
    return patched


def episode_schema_array(episodes: list[dict]) -> str:
    lines = []
    for ep in episodes:
        obj = {
            "@type": "TVEpisode",
            "@id": f"{ORIGIN}/episode-{ep['n']}/#episode",
            "episodeNumber": ep["n"],
            "name": ep["title"],
            "description": ep["plain"],
            "url": f"{ORIGIN}/episode-{ep['n']}/",
        }
        lines.append("      " + json.dumps(obj, ensure_ascii=False, separators=(", ", ": ")))
    return "[\n" + ",\n".join(lines) + "\n    ]"


def patch_jsonld(html: str, episodes: list[dict]) -> str:
    key = '"episode":'
    start = html.find(key)
    if start == -1:
        raise SystemExit("homepage JSON-LD is missing the TVSeries episode list")
    bracket = html.find("[", start)
    depth = 0
    end = None
    for i in range(bracket, len(html)):
        if html[i] == "[":
            depth += 1
        elif html[i] == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise SystemExit("could not find the end of the TVSeries episode list")
    return html[:bracket] + episode_schema_array(episodes) + html[end + 1 :]


def patch_alt(html: str) -> str:
    html = html.replace(
        '<picture class="hero-media" aria-hidden="true">',
        '<picture class="hero-media">',
        1,
    )
    html = html.replace(
        '<img src="/ethiopia-highlands-hero.jpg" alt=""',
        f'<img src="/ethiopia-highlands-hero.jpg" alt="{html_text(HERO_ALT)}"',
        1,
    )
    if f'alt="{HERO_ALT}"' not in html:
        raise SystemExit("homepage hero image is missing its alt text")
    return html


def stylesheet(html: str, existing_css: str) -> tuple[str, str]:
    """Keep homepage CSS inline so the first paint does not wait on a second request."""
    link = '<link rel="stylesheet" href="/site.css" />'
    match = re.search(r"<style>(.*?)</style>", html, flags=re.S)
    if match:
        base_source = match.group(1).strip("\n")
        html = html[: match.start()] + "@@STYLE@@" + html[match.end() :]
    elif link in html:
        base_source = existing_css
        html = html.replace(link, "@@STYLE@@", 1)
    else:
        raise SystemExit("homepage has neither a style block nor a site.css link")
    if MARKER in base_source:
        base = base_source.split(MARKER)[0].rstrip() + "\n"
    else:
        base = base_source.rstrip() + "\n"
    extra = EXTRA_CSS.replace(f"{MARKER} */", MARKER, 1)
    css = base + "\n" + extra
    if not css.endswith("\n"):
        css += "\n"
    html = html.replace("@@STYLE@@", "<style>\n" + css + "</style>", 1)
    return html, css


def page_url(n: int) -> str:
    return f"{ORIGIN}/episode-{n}/"


def json_ld(ep: dict, episodes: list[dict]) -> str:
    n = ep["n"]
    url = page_url(n)
    video_id = ep["youtube"].rsplit("/", 1)[-1]
    metadata = ep["video_metadata"]
    graph = [
        {
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": f"{ep['title']} — Episode {n} | The Assignment: Ethiopia",
            "description": ep["plain"],
            "inLanguage": "en",
            "isPartOf": {"@id": f"{ORIGIN}/#website"},
            "breadcrumb": {"@id": f"{url}#breadcrumb"},
            "mainEntity": {"@id": f"{url}#episode"},
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{url}#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "The Assignment: Ethiopia",
                    "item": f"{ORIGIN}/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Episodes",
                    "item": f"{ORIGIN}/#episodes",
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": f"Episode {n}: {ep['title']}",
                    "item": url,
                },
            ],
        },
        {
            "@type": "TVSeries",
            "@id": f"{ORIGIN}/#series",
            "name": "The Assignment: Ethiopia",
            "url": f"{ORIGIN}/",
        },
        {
            "@type": "TVEpisode",
            "@id": f"{url}#episode",
            "name": ep["title"],
            "episodeNumber": n,
            "description": ep["plain"],
            "url": url,
            "inLanguage": "en",
            "image": HERO_IMAGE,
            "partOfSeries": {"@id": f"{ORIGIN}/#series"},
            "video": {"@id": f"{url}#video"},
        },
        {
            "@type": "VideoObject",
            "@id": f"{url}#video",
            "name": ep["title"],
            "description": ep["plain"],
            "thumbnailUrl": metadata["thumbnailUrl"],
            **({"uploadDate": metadata["uploadDate"]} if metadata["status"] == "verified" else {}),
            "url": ep["youtube"],
            "embedUrl": f"https://www.youtube.com/embed/{video_id}",
            "inLanguage": "en",
        },
    ]
    # Publication of this exact YouTube video is separate from a TV air date.
    del episodes
    payload = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_episode(ep: dict, episodes: list[dict]) -> str:
    n = ep["n"]
    url = page_url(n)
    title = f"{ep['title']} — Episode {n} | The Assignment: Ethiopia"
    description = meta_description(ep["plain"])
    prev_ep = episodes[n - 2] if n > 1 else None
    next_ep = episodes[n] if n < len(episodes) else None

    def head_link(rel: str, other: dict | None) -> str:
        if not other:
            return ""
        return f'  <link rel="{rel}" href="{page_url(other["n"])}" />\n'

    def pager_link(rel: str, label: str, other: dict | None) -> str:
        if not other:
            return ""
        return (
            f'        <a rel="{rel}" href="/episode-{other["n"]}/">'
            f'<span class="pager-kicker">{html_text(label)}</span>'
            f'<span class="pager-title">{html_text(other["title"])}</span></a>\n'
        )

    e_title = html_text(title)
    e_desc = html_text(description)
    e_h1 = html_text(ep["title"])
    crumb = html_text(f"Episode {n}: {ep['title']}")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="color-scheme" content="light dark" />
  <meta name="theme-color" content="#0b0b0b" media="(prefers-color-scheme: dark)" />
  <meta name="theme-color" content="#f5f4f0" media="(prefers-color-scheme: light)" />
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <title>{e_title}</title>
  <meta name="description" content="{e_desc}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
  <link rel="canonical" href="{url}" />
  <link rel="alternate" hreflang="en" href="{url}" />
  <link rel="alternate" hreflang="x-default" href="{url}" />
{head_link("prev", prev_ep)}{head_link("next", next_ep)}  <meta property="og:type" content="video.episode" />
  <meta property="og:site_name" content="The Assignment" />
  <meta property="og:locale" content="en_US" />
  <meta property="og:title" content="{e_title}" />
  <meta property="og:description" content="{e_desc}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{HERO_IMAGE}" />
  <meta property="og:image:secure_url" content="{HERO_IMAGE}" />
  <meta property="og:image:type" content="image/jpeg" />
  <meta property="og:image:width" content="2200" />
  <meta property="og:image:height" content="1469" />
  <meta property="og:image:alt" content="{html_text(HERO_ALT)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{e_title}" />
  <meta name="twitter:description" content="{e_desc}" />
  <meta name="twitter:image" content="{HERO_IMAGE}" />
  <meta name="twitter:image:alt" content="{html_text(HERO_ALT)}" />
{FONT_LINKS}
  <link rel="stylesheet" href="/site.css" />
  <script type="application/ld+json">
{json_ld(ep, episodes)}
  </script>
</head>
<body class="episode-page">
  <a class="skip" href="#main">Skip to content</a>
  <header class="subnav">
    <a class="brand" href="/">The Assignment: Ethiopia</a>
    <nav aria-label="Page navigation">
      <a href="/#story">Story</a>
      <a href="/#cast">Cast</a>
      <a href="/#connections">Connect</a>
      <a class="watch" href="/#episodes">All episodes</a>
    </nav>
  </header>
  <main id="main">
    <article class="section">
      <div class="section-inner">
        <nav class="crumbs" aria-label="Breadcrumb">
          <ol>
            <li><a href="/">The Assignment: Ethiopia</a></li>
            <li><a href="/#episodes">Episodes</a></li>
            <li aria-current="page">{crumb}</li>
          </ol>
        </nav>
        <p class="section-label">Episode {n:02d}</p>
        <h1>{e_h1}</h1>
        <p class="synopsis">{ep["description_html"]}</p>
        <p class="watch-row"><a class="btn btn-red" href="{ep["youtube"]}" target="_blank" rel="noopener">{YOUTUBE_ICON}Watch on YouTube<span class="visually-hidden"> (opens in a new tab)</span></a></p>
        <nav class="pager" aria-label="More episodes">
{pager_link("prev", "Previous episode", prev_ep)}{pager_link("next", "Next episode", next_ep)}        </nav>
      </div>
    </article>
  </main>
{FOOTER}
</body>
</html>
"""


def render_sitemap(episodes: list[dict]) -> str:
    urls = [f"{ORIGIN}/"] + [page_url(ep["n"]) for ep in episodes]
    body = []
    for i, loc in enumerate(urls):
        priority = "1.0" if i == 0 else "0.8"
        body.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n"
            "    <changefreq>monthly</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(body)
        + "\n</urlset>\n"
    )


def transform(html: str, existing_css: str) -> tuple[str, str, dict[int, str], str]:
    episodes = parse_episodes(html)
    metadata = load_video_metadata(ROOT)
    catalog_ids = {ep["youtube"].rsplit("/", 1)[-1] for ep in episodes}
    if set(metadata) != catalog_ids:
        raise SystemExit("video metadata must match the exact homepage video IDs")
    for ep in episodes:
        entry = metadata[ep["youtube"].rsplit("/", 1)[-1]]
        if entry["episode"] != ep["n"]:
            raise SystemExit(f"video metadata does not match episode {ep['n']}")
        ep["video_metadata"] = entry
    metas = [meta_description(ep["plain"]) for ep in episodes]
    if len(set(metas)) != len(metas):
        raise SystemExit("episode meta descriptions are not unique")
    html = patch_cards(html, episodes)
    html = patch_jsonld(html, episodes)
    html = patch_alt(html)
    html, css = stylesheet(html, existing_css)
    pages = {ep["n"]: render_episode(ep, episodes) for ep in episodes}
    for ep in episodes:
        if ep["youtube"] not in pages[ep["n"]]:
            raise SystemExit(f"episode {ep['n']} page dropped its video URL")
        if ep["plain"] not in pages[ep["n"]] and ep["description_html"] not in pages[ep["n"]]:
            raise SystemExit(f"episode {ep['n']} page dropped its description")
    return html, css, pages, render_sitemap(episodes)


def expected_files(html: str, existing_css: str) -> dict[str, str]:
    html2, css, pages, sitemap = transform(html, existing_css)
    files = {
        "index.html": html2,
        "site.css": css,
        "sitemap.xml": sitemap,
    }
    for number, page in pages.items():
        files[f"episode-{number}/index.html"] = page
    return files


def main() -> None:
    check = "--check" in sys.argv
    index_path = ROOT / "index.html"
    css_path = ROOT / "site.css"
    html = index_path.read_text(encoding="utf-8")
    existing_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    files = expected_files(html, existing_css)
    if check:
        stale = []
        for rel, content in files.items():
            path = ROOT / rel
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current != content:
                stale.append(rel)
        if stale:
            print("episode build is out of date: " + ", ".join(stale), file=sys.stderr)
            sys.exit(1)
        print(f"Checked {len(files)} generated file(s) against the homepage catalog.")
        return
    for rel, content in files.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Wrote {len(files)} file(s), including 13 episode pages.")


if __name__ == "__main__":
    main()
