
import streamlit as st
import pandas as pd
import zipfile
import io
from pathlib import Path

from download_page import download_html
from meta_data_extract import extract_metadata
from content_extract import extract_content
from content_tokenization import get_top_words, find_collocations
from xml_generator import generate_xml


# ==================================================
# CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="TP2 | HTML to XML",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    h1 {
        padding-bottom: 0;
    }
    div[data-testid="stMetric"] {
        background: rgba(128,128,128,0.08);
        padding: 10px;
        border-radius: 10px;
    }
    div.stButton > button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌐 HTML → XML")
st.caption("Web sémantique | Extraction, analyse textuelle et génération XML")


# ==================================================
# ÉTAT DE L'APPLICATION
# ==================================================

if "article_url" not in st.session_state:
    st.session_state.article_url = ""

if "results" not in st.session_state:
    st.session_state.results = None


def clear_url():
    st.session_state.article_url = ""


# ==================================================
# PARAMÈTRES
# ==================================================

with st.container(border=True):

    st.markdown("**⚙️ Configuration de l'analyse**")

    source_type = st.radio(
        "Source de l'article",
        ["🌍 URL", "📁 Fichier HTML"],
        horizontal=True,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([3, 1])

    uploaded_file = None
    url = ""

    with col1:
        if source_type == "🌍 URL":

            url = st.text_input(
                "Adresse de l'article",
                key="article_url",
                placeholder="https://example.com/article"
            )

        else:
            uploaded_file = st.file_uploader(
                "Importer une page HTML",
                type=["html", "htm"],
                help="Sélectionnez un fichier HTML depuis votre ordinateur."
            )

    with col2:
        st.markdown("<div style='height: 28px'></div>",
                    unsafe_allow_html=True)

        if source_type == "🌍 URL":
            st.button(
                "✖ Effacer URL",
                on_click=clear_url,
                use_container_width=True
            )

    col3, col4 = st.columns(2)

    with col3:
        language = st.selectbox(
            "Langue de l'article",
            ["fr", "en", "es", "de"],
            format_func=lambda x: {
                "fr": "🇫🇷 Français",
                "en": "🇬🇧 English",
                "es": "🇪🇸 Español",
                "de": "🇩🇪 Deutsch"
            }[x]
        )

    with col4:
        keywords_input = st.text_input(
            "Mots-clés (séparés par des virgules)",
            placeholder="intelligence artificielle, web..."
        )

    analyze = st.button(
        "🚀 Analyser l'article",
        type="primary",
        use_container_width=True
    )


# ==================================================
# TRAITEMENT
# ==================================================

if analyze:

    if source_type == "🌍 URL" and not url.strip():
        st.error("Veuillez saisir une adresse URL.")
        st.stop()

    if source_type == "📁 Fichier HTML" and uploaded_file is None:
        st.error("Veuillez importer un fichier HTML.")
        st.stop()

    try:
        with st.spinner("Analyse en cours..."):

            # 1. Récupération du HTML
            if source_type == "🌍 URL":
                html = download_html(url)
                source_url = url

            else:
                raw_html = uploaded_file.getvalue()

                try:
                    html = raw_html.decode("utf-8")
                except UnicodeDecodeError:
                    html = raw_html.decode("latin-1")

                source_url = uploaded_file.name

            # 2. Extraction des métadonnées
            metadata = extract_metadata(html, source_url)

            # 3. Extraction du contenu
            content = extract_content(html)

            if not content or len(content.strip()) < 30:
                st.error("Le contenu de l'article est insuffisant.")
                st.stop()

            # 4. Définition des mots-clés
            keywords = [
                word.strip()
                for word in keywords_input.split(",")
                if word.strip()
            ]

            if not keywords:
                keywords = metadata.get("keywords", [])

            if isinstance(keywords, str):
                keywords = [
                    word.strip()
                    for word in keywords.split(",")
                    if word.strip()
                ]

            # 5. Fréquences
            top_words = get_top_words(
                content,
                language,
                limit=10
            )

            # 6. Collocatifs
            collocations = find_collocations(
                content,
                keywords,
                language,
                window=5
            )

            # 7. Génération XML
            xml_content = generate_xml(
                metadata=metadata,
                content=content,
                top_words=top_words,
                collocations=collocations,
                url=source_url
            )

            # Normalisation du XML
            if isinstance(xml_content, bytes):
                xml_content = xml_content.decode("utf-8")

            # Sauvegarde
            st.session_state.results = {
                "metadata": metadata,
                "content": content,
                "top_words": top_words,
                "collocations": collocations,
                "xml": xml_content,
                "url": source_url,
                "keywords": keywords,
                "html": html
            }

        st.success("Analyse terminée avec succès !")

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")


# ==================================================
# AFFICHAGE COMPACT DES RÉSULTATS
# ==================================================

if st.session_state.results:

    result = st.session_state.results

    metadata = result["metadata"]
    content = result["content"]
    top_words = result["top_words"]
    collocations = result["collocations"]
    xml_content = result["xml"]

    st.divider()

    st.subheader("📊 Résumé de l'analyse")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Mots dans l'article", len(content.split()))

    with col2:
        st.metric("Mots-clés", len(result["keywords"]))

    with col3:
        st.metric("Mots fréquents", len(top_words))

    # Onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Métadonnées",
        "📝 Contenu",
        "📊 Fréquences",
        "🔎 Collocatifs",
        "💻 XML"
    ])

    # ----------------------------------------------
    # ONGLET 1 : MÉTADONNÉES
    # ----------------------------------------------

    with tab1:

        st.markdown("**Informations extraites**")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Titre**")
            st.write(metadata.get("title") or "Non disponible")

            st.write("**Auteur**")
            st.write(metadata.get("author") or "Non disponible")

            st.write("**Date**")
            st.write(metadata.get("date") or "Non disponible")

        with col2:
            st.write("**Description**")
            st.write(metadata.get("description") or "Non disponible")

            st.write("**URL / Source**")
            st.write(result["url"])

            st.write("**Mots-clés**")
            st.write(", ".join(result["keywords"]) or "Non disponibles")

    # ----------------------------------------------
    # ONGLET 2 : CONTENU
    # ----------------------------------------------

    with tab2:

        st.markdown("**Texte extrait de l'article**")

        st.caption(f"{len(content.split())} mots extraits")

        with st.container(height=350):
            st.write(content)

        st.download_button(
            "⬇️ Télécharger le texte",
            data=content,
            file_name="article.txt",
            mime="text/plain"
        )

    # ----------------------------------------------
    # ONGLET 3 : FRÉQUENCES
    # ----------------------------------------------

    with tab3:

        st.markdown("**Les 10 mots les plus fréquents**")

        if isinstance(top_words, dict):
            frequency_data = [
                {"Mot": word, "Fréquence": count}
                for word, count in top_words.items()
            ]
        else:
            frequency_data = [
                {"Mot": item[0], "Fréquence": item[1]}
                for item in top_words
            ]

        if frequency_data:

            df = pd.DataFrame(frequency_data)

            col1, col2 = st.columns([1, 1])

            with col1:
                st.dataframe(
                    df,
                    hide_index=True,
                    use_container_width=True
                )

            with col2:
                st.bar_chart(
                    df.set_index("Mot"),
                    horizontal=True
                )

        else:
            st.info("Aucune fréquence disponible.")

    # ----------------------------------------------
    # ONGLET 4 : COLLOCATIFS
    # ----------------------------------------------

    with tab4:

        st.markdown("**Collocatifs dans une fenêtre de 5 mots**")

        if not collocations:
            st.info("Aucun collocatif trouvé.")

        for keyword, values in collocations.items():

            with st.expander(f"🔑 {keyword}", expanded=True):

                rows = []

                for word, counts in values.items():

                    rows.append({
                        "Collocatif": word,
                        "Gauche": counts.get("left", 0),
                        "Droite": counts.get("right", 0),
                        "Total": counts.get("total", 0)
                    })

                if rows:
                    df = pd.DataFrame(rows)
                    df = df.sort_values(
                        "Total",
                        ascending=False
                    )

                    st.dataframe(
                        df,
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.caption("Aucun collocatif trouvé.")

    # ----------------------------------------------
    # ONGLET 5 : XML
    # ----------------------------------------------

    with tab5:

        st.markdown("**Fichier XML généré**")

        st.download_button(
            "⬇️ Télécharger article.xml",
            data=xml_content.encode("utf-8"),
            file_name="article_analyse.xml",
            mime="application/xml",
            type="primary",
            use_container_width=True
        )

        with st.expander("Afficher le code XML"):
            st.code(xml_content, language="xml")

    # ----------------------------------------------
    # TÉLÉCHARGEMENT ZIP
    # ----------------------------------------------

    st.divider()

    with st.container(border=True):

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("**📦 Télécharger le projet complet**")
            st.caption(
                "Archive contenant les scripts Python, "
                "les dépendances et le résultat XML."
            )

        project_dir = Path(__file__).resolve().parent
        zip_buffer = io.BytesIO()

        project_files = [
            "app.py",
            "download_page.py",
            "meta_data_extract.py",
            "content_extract.py",
            "content_tokenization.py",
            "xml_generator.py",
            "requirements.txt"
        ]

        with zipfile.ZipFile(
            zip_buffer,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zip_file:

            for filename in project_files:

                file_path = project_dir / filename

                if file_path.exists():
                    zip_file.write(file_path, filename)

            zip_file.writestr(
                "article_analyse.xml",
                xml_content
            )

            zip_file.writestr(
                "article_source.html",
                result["html"]
            )

        with col2:
            st.download_button(
                "⬇️ Télécharger ZIP",
                data=zip_buffer.getvalue(),
                file_name="TP2_HTML_XML.zip",
                mime="application/zip",
                use_container_width=True
            )


# ==================================================
# PIED DE PAGE
# ==================================================

st.divider()

st.caption(
    "TP2 – Web sémantique | Python • BeautifulSoup • "
    "Trafilatura • Streamlit • XML"
)

