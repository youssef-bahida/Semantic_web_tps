
import streamlit as st
import pandas as pd
import zipfile
import io
from pathlib import Path

# Importer nos modules
from download_page import download_page
from meta_data_extract import extract_metadata
from content_extract import extract_content
from content_tokenization import (
    get_top_words,
    get_collocations
)
from xml_generator import generate_xml


# ==========================================
# CONFIGURATION DE L'APPLICATION
# ==========================================

st.set_page_config(
    page_title="TP2 - HTML vers XML",
    page_icon="📄",
    layout="wide"
)


# ==========================================
# STYLE ET TITRE
# ==========================================

st.title("📄 HTML → XML")
st.subheader("Extraction et analyse d'articles Web")

st.write(
    """
    Cette application permet de télécharger une page Web,
    d'extraire les informations d'un article, d'analyser
    son contenu linguistique et de générer un fichier XML.
    """
)

st.divider()


# ==========================================
# PARAMÈTRES
# ==========================================

st.header("1. Paramètres de l'analyse")

url = st.text_input(
    "Adresse URL de l'article",
    placeholder="https://example.com/article"
)

language = st.selectbox(
    "Langue de l'article",
    options=["fr", "en", "es", "de"],
    format_func=lambda x: {
        "fr": "Français",
        "en": "Anglais",
        "es": "Espagnol",
        "de": "Allemand"
    }[x]
)

manual_keywords = st.text_input(
    "Mots-clés supplémentaires (facultatif)",
    placeholder="intelligence, technologie, données"
)

st.caption(
    "Si le site ne fournit pas de mots-clés, "
    "vous pouvez les saisir ici."
)


# ==========================================
# LANCEMENT DE L'ANALYSE
# ==========================================

if st.button(
    "🚀 Analyser l'article",
    type="primary",
    use_container_width=True
):

    if not url.strip():

        st.error("Veuillez saisir une URL.")

    else:

        try:

            with st.spinner(
                "Téléchargement et traitement de l'article..."
            ):

                # ----------------------------------
                # ÉTAPE 1 : TÉLÉCHARGER LE HTML
                # ----------------------------------

                html = download_page(url.strip())

                # ----------------------------------
                # ÉTAPE 2 : EXTRAIRE LES MÉTADONNÉES
                # ----------------------------------

                metadata = extract_metadata(
                    html,
                    url.strip()
                )

                # ----------------------------------
                # ÉTAPE 3 : EXTRAIRE LE CONTENU
                # ----------------------------------

                content = extract_content(html)

                if not content:

                    raise ValueError(
                        "Impossible d'extraire le contenu de l'article."
                    )

                # ----------------------------------
                # ÉTAPE 4 : GÉRER LES MOTS-CLÉS
                # ----------------------------------

                additional_keywords = [
                    word.strip()
                    for word in manual_keywords.split(",")
                    if word.strip()
                ]

                # Ajouter les mots-clés manuels
                # sans répéter ceux déjà présents
                existing = {
                    word.casefold()
                    for word in metadata["keywords"]
                }

                for keyword in additional_keywords:

                    if keyword.casefold() not in existing:

                        metadata["keywords"].append(keyword)
                        existing.add(keyword.casefold())

                # ----------------------------------
                # ÉTAPE 5 : CALCULER LES FRÉQUENCES
                # ----------------------------------

                frequencies = get_top_words(
                    content,
                    language
                )

                # ----------------------------------
                # ÉTAPE 6 : CALCULER LES COLLOCATIFS
                # ----------------------------------

                collocations = get_collocations(
                    content,
                    metadata["keywords"],
                    language
                )

                # ----------------------------------
                # ÉTAPE 7 : GÉNÉRER LE XML
                # ----------------------------------

                xml_file = generate_xml(
                    metadata,
                    content,
                    frequencies,
                    collocations
                )

                # ----------------------------------
                # SAUVEGARDER LES RÉSULTATS
                # ----------------------------------

                st.session_state["metadata"] = metadata
                st.session_state["content"] = content
                st.session_state["frequencies"] = frequencies
                st.session_state["collocations"] = collocations
                st.session_state["xml"] = xml_file
                st.session_state["analysis_done"] = True

        except Exception as error:

            st.session_state["analysis_done"] = False

            st.error(
                f"Une erreur est survenue : {error}"
            )


# ==========================================
# AFFICHAGE DES RÉSULTATS
# ==========================================

if st.session_state.get("analysis_done", False):

    metadata = st.session_state["metadata"]
    content = st.session_state["content"]
    frequencies = st.session_state["frequencies"]
    collocations = st.session_state["collocations"]
    xml_file = st.session_state["xml"]

    st.divider()

    st.success("Analyse terminée avec succès !")

    # ======================================
    # 1. MÉTADONNÉES
    # ======================================

    st.header("2. Informations de l'article")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Titre :**")
        st.write(metadata["title"] or "Non disponible")

        st.write("**Auteur :**")
        st.write(metadata["author"] or "Non disponible")

        st.write("**Date de publication :**")
        st.write(metadata["date"] or "Non disponible")

    with col2:

        st.write("**Lien :**")
        st.write(metadata["link"])

        st.write("**Description :**")
        st.write(metadata["description"] or "Non disponible")

        st.write("**Mots-clés :**")
        st.write(
            ", ".join(metadata["keywords"]) or "Aucun"
        )

    # ======================================
    # 2. CONTENU
    # ======================================

    st.divider()

    st.header("3. Contenu extrait")

    st.text_area(
        "Texte de l'article",
        value=content,
        height=250,
        disabled=True
    )

    # ======================================
    # 3. FRÉQUENCES
    # ======================================

    st.divider()

    st.header("4. Les 10 mots les plus fréquents")

    if frequencies:

        frequency_df = pd.DataFrame(
            frequencies,
            columns=["Mot", "Fréquence"]
        )

        col1, col2 = st.columns(
            [1, 2]
        )

        with col1:

            st.dataframe(
                frequency_df,
                use_container_width=True,
                hide_index=True
            )

        with col2:

            st.bar_chart(
                frequency_df.set_index("Mot")
            )

    else:

        st.warning(
            "Aucun mot significatif n'a été détecté."
        )

    # ======================================
    # 4. COLLOCATIFS
    # ======================================

    st.divider()

    st.header("5. Analyse des collocatifs")

    if not collocations:

        st.info(
            "Aucun mot-clé disponible pour rechercher les collocatifs."
        )

    else:

        for keyword, data in collocations.items():

            with st.expander(
                f"Mot-clé : {keyword}",
                expanded=True
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.markdown("**À gauche**")

                    df_left = pd.DataFrame(
                        data["left"].most_common(),
                        columns=["Mot", "Occurrences"]
                    )

                    st.dataframe(
                        df_left,
                        use_container_width=True,
                        hide_index=True
                    )

                with col2:

                    st.markdown("**À droite**")

                    df_right = pd.DataFrame(
                        data["right"].most_common(),
                        columns=["Mot", "Occurrences"]
                    )

                    st.dataframe(
                        df_right,
                        use_container_width=True,
                        hide_index=True
                    )

                with col3:

                    st.markdown("**Total**")

                    df_total = pd.DataFrame(
                        data["total"].most_common(),
                        columns=["Mot", "Occurrences"]
                    )

                    st.dataframe(
                        df_total,
                        use_container_width=True,
                        hide_index=True
                    )

    # ======================================
    # 5. AFFICHER LE XML
    # ======================================

    st.divider()

    st.header("6. Document XML généré")

    st.code(
        xml_file.decode("utf-8"),
        language="xml"
    )

    st.download_button(
        label="📥 Télécharger article.xml",
        data=xml_file,
        file_name="article.xml",
        mime="application/xml",
        use_container_width=True
    )

    # ======================================
    # 6. CRÉER UNE ARCHIVE ZIP
    # ======================================

    st.divider()

    st.header("7. Exporter le projet complet")

    zip_buffer = io.BytesIO()

    project_directory = Path(__file__).resolve().parent

    project_files = [
        "download_page.py",
        "meta_data_extract.py",
        "content_extract.py",
        "content_tokenization.py",
        "xml_generator.py",
        "web_gui.py",
        "requirements.txt"
    ]

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as archive:

        # Ajouter le XML
        archive.writestr(
            "resultats/article.xml",
            xml_file
        )

        # Ajouter tous les fichiers Python
        for filename in project_files:

            file_path = project_directory / filename

            if file_path.exists():

                archive.write(
                    file_path,
                    arcname=filename
                )

    st.download_button(
        label="📦 Télécharger le projet complet (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="TP2_HTML_XML.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True
    )

    st.success(
        "Votre projet est prêt à être téléchargé."
    )


# ==========================================
# PIED DE PAGE
# ==========================================

st.divider()

st.caption(
    "TP2 - Web sémantique | Conversion HTML vers XML"
)

