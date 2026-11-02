
import trafilatura
from bs4 import BeautifulSoup


def extract_content(html):
    """
    Extrait le contenu principal d'un article HTML.

    Paramètre :
        html : code source HTML

    Retour :
        Texte principal de l'article.
    """

    # Première méthode : utiliser Trafilatura
    content = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        include_links=False,
        favor_precision=True
    )

    # Deuxième méthode : BeautifulSoup si Trafilatura échoue
    if not content:

        soup = BeautifulSoup(html, "html.parser")

        # Supprimer les éléments inutiles
        unwanted_tags = [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
            "noscript"
        ]

        for tag in soup(unwanted_tags):
            tag.decompose()

        # Rechercher le contenu de l'article
        article = soup.find("article")

        if article:
            content = article.get_text(
                separator=" ",
                strip=True
            )

        else:
            main = soup.find("main")

            if main:
                content = main.get_text(
                    separator=" ",
                    strip=True
                )

            else:
                content = soup.body.get_text(
                    separator=" ",
                    strip=True
                ) if soup.body else soup.get_text(
                    separator=" ",
                    strip=True
                )

    return content.strip() if content else ""

