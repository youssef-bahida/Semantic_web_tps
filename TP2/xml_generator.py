
from xml.etree import ElementTree as ET
from xml.dom import minidom


def generate_xml(metadata, content, frequencies, collocations):
    """
    Génère un fichier XML à partir des résultats de l'analyse.

    Paramètres :
        metadata     : informations de l'article
        content      : contenu principal
        frequencies  : 10 mots les plus fréquents
        collocations : résultats des collocatifs

    Retour :
        Document XML encodé en UTF-8.
    """

    # Élément racine
    root = ET.Element("article")

    # =====================================
    # 1. MÉTADONNÉES
    # =====================================

    metadata_element = ET.SubElement(
        root,
        "metadata"
    )

    fields = [
        "title",
        "link",
        "description",
        "author",
        "date"
    ]

    for field in fields:

        element = ET.SubElement(
            metadata_element,
            field
        )

        element.text = metadata.get(field, "") or ""

    # =====================================
    # 2. MOTS-CLÉS
    # =====================================

    keywords_element = ET.SubElement(
        metadata_element,
        "keywords"
    )

    for keyword in metadata.get("keywords", []):

        element = ET.SubElement(
            keywords_element,
            "keyword"
        )

        element.text = keyword

    # =====================================
    # 3. CONTENU DE L'ARTICLE
    # =====================================

    content_element = ET.SubElement(
        root,
        "content"
    )

    content_element.text = content

    # =====================================
    # 4. FRÉQUENCES DES MOTS
    # =====================================

    frequencies_element = ET.SubElement(
        root,
        "frequencies"
    )

    for word, count in frequencies:

        ET.SubElement(
            frequencies_element,
            "word",
            {
                "value": word,
                "count": str(count)
            }
        )

    # =====================================
    # 5. COLLOCATIFS
    # =====================================

    collocations_element = ET.SubElement(
        root,
        "collocations"
    )

    for keyword, data in collocations.items():

        keyword_element = ET.SubElement(
            collocations_element,
            "keyword",
            name=keyword
        )

        # Trois directions
        for direction in [
            "left",
            "right",
            "total"
        ]:

            direction_element = ET.SubElement(
                keyword_element,
                direction
            )

            # Ajouter les collocatifs
            for word, count in data[direction].most_common():

                ET.SubElement(
                    direction_element,
                    "word",
                    {
                        "value": word,
                        "count": str(count)
                    }
                )

    # =====================================
    # 6. FORMATER LE XML
    # =====================================

    xml_bytes = ET.tostring(
        root,
        encoding="utf-8"
    )

    # Rendre le document lisible
    pretty_xml = minidom.parseString(
        xml_bytes
    ).toprettyxml(
        indent="    ",
        encoding="UTF-8"
    )

    return pretty_xml

