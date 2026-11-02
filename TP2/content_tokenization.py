
import re
from collections import Counter, defaultdict

import stopwordsiso
from wordfreq import zipf_frequency


# ==========================================
# 1. TOKENIZATION
# ==========================================

def tokenize(text):
    """
    Découpe un texte en mots.
    Conserve les accents et les apostrophes.
    """

    return re.findall(
        r"[^\W\d_]+(?:['’][^\W\d_]+)*",
        text.lower(),
        flags=re.UNICODE
    )


# ==========================================
# 2. FILTERING
# ==========================================

def filter_words(words, language):
    """
    Supprime les mots vides et les mots
    qui ne semblent pas appartenir à la langue choisie.
    """

    stop_words = stopwordsiso.stopwords(language)

    filtered = []

    for word in words:

        if word in stop_words:
            continue

        # Éliminer les mots trop courts
        if len(word) < 2:
            continue

        # Vérifier que le mot existe suffisamment
        # dans la langue sélectionnée
        if zipf_frequency(word, language) < 2:
            continue

        filtered.append(word)

    return filtered


# ==========================================
# 3. TOP 10 WORD FREQUENCIES
# ==========================================

def get_top_words(text, language="fr", limit=10):
    """
    Retourne les mots les plus fréquents.
    Résultat : dictionnaire {mot: fréquence}.
    """

    words = tokenize(text)

    filtered = filter_words(words, language)

    frequencies = Counter(filtered)

    return dict(frequencies.most_common(limit))


# ==========================================
# 4. KEYWORD COLLOCATIONS
# ==========================================

def find_collocations(text, keywords, language="fr", window=5):
    """
    Recherche les collocatifs autour de chaque mot-clé.

    window = 5 :
    - 5 mots à gauche
    - 5 mots à droite

    Résultat :
    {
        "mot-clé": {
            "collocatif": {
                "left": 2,
                "right": 3,
                "total": 5
            }
        }
    }
    """

    words = tokenize(text)

    # Filtrer les mots non pertinents
    stop_words = stopwordsiso.stopwords(language)

    results = {}

    for keyword in keywords:

        keyword = keyword.strip().lower()

        keyword_tokens = tokenize(keyword)

        if len(keyword_tokens) != 1:
            continue

        target = keyword_tokens[0]

        if target not in words:
            results[keyword] = {}
            continue

        collocations = defaultdict(
            lambda: {
                "left": 0,
                "right": 0,
                "total": 0
            }
        )

        # Parcourir le texte
        for index, word in enumerate(words):

            if word != target:
                continue

            # Fenêtre à gauche
            left_start = max(0, index - window)

            for position in range(left_start, index):

                collocate = words[position]

                if collocate == target or collocate in stop_words:
                    continue

                if len(collocate) < 2:
                    continue

                collocations[collocate]["left"] += 1
                collocations[collocate]["total"] += 1

            # Fenêtre à droite
            right_end = min(len(words), index + window + 1)

            for position in range(index + 1, right_end):

                collocate = words[position]

                if collocate == target or collocate in stop_words:
                    continue

                if len(collocate) < 2:
                    continue

                collocations[collocate]["right"] += 1
                collocations[collocate]["total"] += 1

        # Trier par fréquence totale
        sorted_collocations = dict(
            sorted(
                collocations.items(),
                key=lambda item: item[1]["total"],
                reverse=True
            )
        )

        results[keyword] = sorted_collocations

    return results

