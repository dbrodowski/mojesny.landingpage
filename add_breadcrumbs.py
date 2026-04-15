#!/usr/bin/env python3
"""
Masowe dodawanie breadcrumbs (JSON-LD + wizualnych) do plików HTML.
Uruchom w folderze z plikami HTML:  python3 add_breadcrumbs.py
"""

import os
import re
import json
import glob

BASE_URL = "https://mojesny.app/"

# Mapowanie polskich liter na nazwy plików sny-litera-*
POLISH_LETTER_MAP = {
    'ć': 'c-pl', 'ł': 'l-pl',
    'ś': 's-pl', 'ź': 'z-kreska-pl', 'ż': 'z-pl',
}

# Litery polskie bez własnej strony — mapuj na zwykłą literę
POLISH_FALLBACK = {
    'ą': 'a', 'ę': 'e', 'ń': 'n', 'ó': 'o',
}




def extract_title(content):
    m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    return m.group(1).strip() if m else None


def get_display_title(title):
    """'Sen o aborcji – co oznacza? Znaczenie snu | MojeSny' → 'Sen o aborcji'"""
    # Remove everything after | first
    t = title.split('|')[0].strip()
    # Then remove everything after – (em dash)
    t = t.split('–')[0].strip()
    # Also try regular dash
    t = t.split(' - ')[0].strip()
    return t


def get_letter_info(title):
    """
    Z tytułu 'Sen o ćwiczeniach ...' zwraca (letter_file_slug, display_letter).
    np. ('c-pl', 'Ć') albo ('a', 'A')
    """
    m = re.match(r'Sen o\s+(\S)', title, re.IGNORECASE)
    if not m:
        return None, None
    char = m.group(1).lower()
    if char in POLISH_LETTER_MAP:
        return POLISH_LETTER_MAP[char], char.upper()
    elif char in POLISH_FALLBACK:
        slug = POLISH_FALLBACK[char]
        return slug, slug.upper()
    else:
        return char, char.upper()


def get_letter_info_from_filename(filename):
    """
    Z 'sny-litera-c-pl.html' zwraca ('c-pl', 'Ć')
    Z 'sny-litera-a.html' zwraca ('a', 'A')
    """
    slug = filename.replace('sny-litera-', '').replace('.html', '')
    # Only the letters that have their own -pl page get Polish display
    slug_to_display = {
        'c-pl': 'Ć', 'l-pl': 'Ł', 's-pl': 'Ś',
        'z-pl': 'Ż', 'z-kreska-pl': 'Ź',
    }
    if slug in slug_to_display:
        return slug, slug_to_display[slug]
    else:
        return slug, slug.upper()


def build_jsonld(items):
    """items: list of (name, url|None). Buduje BreadcrumbList JSON-LD."""
    list_items = []
    for i, (name, url) in enumerate(items, 1):
        entry = {
            "@type": "ListItem",
            "position": i,
            "name": name,
        }
        if url:
            entry["item"] = url
        list_items.append(entry)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": list_items
    }


def build_visual_nav(items):
    """Buduje widoczny HTML breadcrumbs. Ostatni element bez linku."""
    parts = []
    for i, (name, url) in enumerate(items):
        if url and i < len(items) - 1:
            parts.append(f'<a href="{url}">{name}</a>')
        else:
            parts.append(f'<span>{name}</span>')
    sep = ' <span class="breadcrumb-sep">&gt;</span> '
    inner = sep.join(parts)
    return (
        '    <nav class="breadcrumbs" aria-label="Breadcrumb">\n'
        '        <div class="container">\n'
        f'            {inner}\n'
        '        </div>\n'
        '    </nav>'
    )


def process_file(filepath):
    filename = os.path.basename(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pomiń jeśli już ma breadcrumbs
    if 'BreadcrumbList' in content:
        return f"SKIP (already has breadcrumbs): {filename}"

    title = extract_title(content)
    if not title:
        return f"SKIP (no title): {filename}"

    display_title = get_display_title(title)
    insert_visual = True

    # --- Określ strukturę breadcrumbs ---
    if filename == 'index.html':
        items = [("Strona Główna", BASE_URL)]
        insert_visual = False

    elif filename == 'ksiega-snow.html':
        items = [
            ("Strona Główna", BASE_URL),
            ("Księga Snów", None),
        ]

    elif filename.startswith('sny-litera-'):
        slug, display_letter = get_letter_info_from_filename(filename)
        items = [
            ("Strona Główna", BASE_URL),
            ("Księga Snów", BASE_URL + "ksiega-snow.html"),
            (f"Litera {display_letter}", None),
        ]

    elif filename.startswith('sen-o-'):
        slug, display_letter = get_letter_info(title)
        if not slug:
            return f"SKIP (can't extract letter): {filename}"
        items = [
            ("Strona Główna", BASE_URL),
            ("Księga Snów", BASE_URL + "ksiega-snow.html"),
            (f"Litera {display_letter}", BASE_URL + f"sny-litera-{slug}.html"),
            (display_title, None),
        ]

    elif filename in ('prywatnosc.html', 'regulamin.html'):
        items = [
            ("Strona Główna", BASE_URL),
            (display_title, None),
        ]

    else:
        return f"SKIP (unknown type): {filename}"

    # --- Buduj HTML do wstawienia ---
    jsonld = build_jsonld(items)
    jsonld_str = json.dumps(jsonld, ensure_ascii=False, indent=2)
    # Indent JSON inside script tag
    jsonld_indented = '\n'.join('    ' + line if line.strip() else line for line in jsonld_str.split('\n'))
    jsonld_block = f'    <script type="application/ld+json">\n{jsonld_indented}\n    </script>'

    if insert_visual:
        visual_block = build_visual_nav(items)
        insert_block = f'\n{jsonld_block}\n\n{visual_block}\n'
    else:
        insert_block = f'\n{jsonld_block}\n'

    # Wstaw zaraz po </header>
    content = content.replace('</header>', f'</header>{insert_block}', 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return f"OK: {filename}"


def main():
    files = sorted(glob.glob("*.html"))
    print(f"Found {len(files)} HTML files\n")

    ok = 0
    skip = 0
    for filepath in files:
        result = process_file(filepath)
        print(result)
        if result.startswith("OK"):
            ok += 1
        else:
            skip += 1

    print(f"\nDone! Updated: {ok}, Skipped: {skip}")


if __name__ == '__main__':
    main()
