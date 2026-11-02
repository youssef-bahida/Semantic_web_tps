
import re

from collections import Counter
from stopwordsiso import stopwords
from wordfreq import zipf_frequency


def tokenize(text):
    """
    Découpe un texte en mots.

    - Convertit en minuscules.
    - Élimine les nombres.
    - Ignore les caractères spéciaux.
    - Conserve les accents et les apostrophes internes.
    """

    return re.findall(
        r"[^\W\d_]+(?:['’][^\W\d_]+)?",
        text.lower(),
        flags=re.UNICODE
    )


def get_top_words(content, language="fr"):
    """
    Calcule les 10 mots les plus fréquents.

    Élimine :
    - Les mots vides (stopwords).
    - Les mots trop peu fréquents dans la langue choisie.
    """

    words = tokenize(content)

    # Récupérer les mots vides de la langue
    stop_words = stopwords(language)

    useful_words = []

    for word in words:

        # Ignorer les mots vides
        if word in stop_words:
            continue

        # Filtrer les mots peu plausibles dans la langue
        if zipf_frequency(word, language) < 2:
            continue

        useful_words.append(word)

    # Calculer les fréquences
    frequencies = Counter(useful_words)

    # Retourner les 10 premiers
    return frequencies.most_common(10)


def get_collocations(content, keywords, language="fr"):
    """
    Recherche les collocatifs des mots-clés.

    Distance :
        5 mots à gauche.
        5 mots à droite.

    Retourne pour chaque mot-clé :
        left  : collocatifs à gauche.
        right : collocatifs à droite.
        total : total des occurrences.
    """

    words = tokenize(content)

    stop_words = stopwords(language)

    results = {}

    for keyword in keywords:

        # Découper le mot-clé
        keyword_words = tokenize(keyword)

        if not keyword_words:
            continue

        keyword_size = len(keyword_words)

        left_counter = Counter()
        right_counter = Counter()

        # Parcourir le texte
        for i in range(
            len(words) - keyword_size + 1
        ):

            # Vérifier la présence du mot-clé
            if words[i:i + keyword_size] == keyword_words:

                # Cinq mots avant le mot-clé
                left_words = words[
                    max(0, i - 5):i
                ]

                # Cinq mots après le mot-clé
                right_words = words[
                    i + keyword_size:
                    i + keyword_size + 5
                ]

                # Comptabiliser les collocatifs à gauche
                for word in left_words:

                    if (
                        word not in stop_words
                        and zipf_frequency(word, language) >= 2
                    ):
                        left_counter[word] += 1

                # Comptabiliser les collocatifs à droite
                for word in right_words:

                    if (
                        word not in stop_words
                        and zipf_frequency(word, language) >= 2
                    ):
                        right_counter[word] += 1

        # Additionner les occurrences gauche et droite
        total_counter = left_counter + right_counter

        results[keyword] = {
            "left": left_counter,
            "right": right_counter,
            "total": total_counter
        }

    return results

