
import requests
from urllib.parse import urlparse


def download_page(url):
    """
    Télécharge une page HTML depuis une URL.

    Paramètre :
        url : adresse de la page Web

    Retour :
        Le code HTML de la page sous forme de texte.
    """

    # Vérifier que l'URL est valide
    parsed_url = urlparse(url)

    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise ValueError("URL invalide. Utilisez une adresse HTTP ou HTTPS.")

    # Simuler un navigateur Web
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        )
    }

    try:
        # Envoyer une requête au serveur
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        # Vérifier le statut HTTP
        response.raise_for_status()

        # Vérifier le type de contenu
        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type.lower():
            raise ValueError("La ressource téléchargée n'est pas une page HTML.")

        # Détecter l'encodage
        response.encoding = response.apparent_encoding

        # Retourner le HTML
        return response.text

    except requests.exceptions.Timeout:
        raise Exception("Le téléchargement a dépassé le délai autorisé.")

    except requests.exceptions.ConnectionError:
        raise Exception("Impossible de se connecter au site Web.")

    except requests.exceptions.HTTPError as error:
        raise Exception(f"Erreur HTTP : {error}")

    except requests.exceptions.RequestException as error:
        raise Exception(f"Erreur de téléchargement : {error}")

