
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import trafilatura
import json


def get_meta(soup, *names):
    """
    Recherche une métadonnée dans les balises meta.
    Accepte les attributs name et property.
    """

    for name in names:

        tag = soup.find(
            "meta",
            attrs={"name": name}
        )

        if not tag:
            tag = soup.find(
                "meta",
                attrs={"property": name}
            )

        if tag and tag.get("content"):
            return tag["content"].strip()

    return ""


def extract_jsonld(soup):
    """
    Recherche les informations d'un article
    dans les données structurées JSON-LD.
    """

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:
            data = json.loads(script.string or script.get_text())

            objects = data if isinstance(data, list) else [data]

            for obj in objects:

                if not isinstance(obj, dict):
                    continue

                # Gérer les objets de type @graph
                candidates = [obj]
                if isinstance(obj.get("@graph"), list):
                    candidates.extend(obj["@graph"])

                for item in candidates:

                    if not isinstance(item, dict):
                        continue

                    item_type = item.get("@type", [])

                    if isinstance(item_type, str):
                        item_type = [item_type]

                    if any(
                        t in ["Article", "NewsArticle", "BlogPosting"]
                        for t in item_type
                    ):
                        return item

        except (json.JSONDecodeError, TypeError):
            continue

    return {}


def extract_metadata(html, url):
    """
    Extrait les métadonnées d'un article HTML.

    Retourne un dictionnaire contenant :
    title, link, description, keywords,
    author et date.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Métadonnées JSON-LD
    structured_data = extract_jsonld(soup)

    # Métadonnées Trafilatura
    article_data = trafilatura.extract_metadata(
        html,
        default_url=url
    )

    # Titre
    title = (
        get_meta(soup, "og:title", "twitter:title")
        or (article_data.title if article_data else "")
        or structured_data.get("headline", "")
        or (soup.title.get_text(strip=True) if soup.title else "")
    )

    if not title:
        heading = soup.find("h1")
        title = heading.get_text(" ", strip=True) if heading else ""

    # Description
    description = (
        get_meta(
            soup,
            "description",
            "og:description",
            "twitter:description"
        )
        or (article_data.description if article_data else "")
        or structured_data.get("description", "")
    )

    # Auteur
    author = (
        get_meta(soup, "author", "article:author")
        or (article_data.author if article_data else "")
    )

    if not author:
        author_data = structured_data.get("author", "")

        if isinstance(author_data, dict):
            author = author_data.get("name", "")

        elif isinstance(author_data, list):
            names = [
                a.get("name", "")
                for a in author_data
                if isinstance(a, dict)
            ]
            author = ", ".join(n for n in names if n)

        elif isinstance(author_data, str):
            author = author_data

    # Date de publication
    date = (
        get_meta(
            soup,
            "article:published_time",
            "datePublished",
            "date",
            "pubdate"
        )
        or (article_data.date if article_data else "")
        or structured_data.get("datePublished", "")
    )

    # Mots-clés
    keywords_text = (
        get_meta(
            soup,
            "keywords",
            "news_keywords"
        )
        or (article_data.tags[0] if article_data and article_data.tags else "")
    )

    if not keywords_text:
        keywords_data = structured_data.get("keywords", "")

        if isinstance(keywords_data, list):
            keywords_text = ",".join(str(k) for k in keywords_data)
        else:
            keywords_text = str(keywords_data)

    keywords = [
        keyword.strip()
        for keyword in keywords_text.split(",")
        if keyword.strip()
    ]

    # Lien canonique
    canonical = soup.find(
        "link",
        rel="canonical"
    )

    if canonical and canonical.get("href"):
        page_link = urljoin(url, canonical["href"])
    else:
        page_link = url

    return {
        "title": title,
        "link": page_link,
        "description": description,
        "keywords": keywords,
        "author": author,
        "date": date
    }

