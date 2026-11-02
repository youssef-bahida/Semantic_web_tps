
import xml.etree.ElementTree as ET
from xml.dom import minidom


def generate_xml(metadata, content, top_words, collocations, url):
    """
    Génère un document XML contenant :
    - Les métadonnées
    - Le contenu de l'article
    - Les 10 mots les plus fréquents
    - Les collocatifs des mots-clés
    """

    root = ET.Element("article")

    # ======================================
    # MÉTADONNÉES
    # ======================================

    meta = ET.SubElement(root, "metadata")

    ET.SubElement(meta, "title").text = str(
        metadata.get("title") or ""
    )

    ET.SubElement(meta, "url").text = str(url or "")

    ET.SubElement(meta, "description").text = str(
        metadata.get("description") or ""
    )

    ET.SubElement(meta, "author").text = str(
        metadata.get("author") or ""
    )

    ET.SubElement(meta, "publication_date").text = str(
        metadata.get("date") or ""
    )

    keywords_element = ET.SubElement(meta, "keywords")

    keywords = metadata.get("keywords", [])

    if isinstance(keywords, str):
        keywords = [
            word.strip()
            for word in keywords.split(",")
            if word.strip()
        ]

    for keyword in keywords:
        ET.SubElement(
            keywords_element,
            "keyword"
        ).text = str(keyword)

    # ======================================
    # CONTENU
    # ======================================

    content_element = ET.SubElement(root, "content")
    content_element.text = content

    # ======================================
    # FRÉQUENCES
    # ======================================

    frequencies = ET.SubElement(
        root,
        "word_frequencies"
    )

    if isinstance(top_words, dict):
        items = top_words.items()
    else:
        items = top_words

    for word, count in items:

        ET.SubElement(
            frequencies,
            "word",
            value=str(word),
            count=str(count)
        )

    # ======================================
    # COLLOCATIFS
    # ======================================

    collocations_element = ET.SubElement(
        root,
        "collocations"
    )

    for keyword, values in collocations.items():

        keyword_element = ET.SubElement(
            collocations_element,
            "keyword",
            value=str(keyword)
        )

        for word, counts in values.items():

            ET.SubElement(
                keyword_element,
                "collocate",
                value=str(word),
                left=str(counts.get("left", 0)),
                right=str(counts.get("right", 0)),
                total=str(counts.get("total", 0))
            )

    # ======================================
    # FORMATAGE XML
    # ======================================

    xml_bytes = ET.tostring(
        root,
        encoding="utf-8"
    )

    pretty_xml = minidom.parseString(
        xml_bytes
    ).toprettyxml(indent="    ", encoding="utf-8")

    return pretty_xml.decode("utf-8")

