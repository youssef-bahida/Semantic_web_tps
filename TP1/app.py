
import re
import io
import csv
from collections import Counter

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# --------------------------------------------------
# Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Text Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container {
        max-width: 1400px;
        padding-top: 1.4rem;
        padding-bottom: 1rem;
    }
    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.15);
    }
    div[data-testid="stTabs"] button {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Embedded example text (no external file required)
# --------------------------------------------------

EXAMPLE_TEXT = """
The Semantic Web is an extension of the World Wide Web that gives
data a well-defined meaning, making it easier for computers and
people to work together. Traditional web pages are mainly designed
for humans to read, while the Semantic Web aims to describe
information in a structured way so that software can interpret
relationships between concepts. Technologies such as RDF, RDFS,
OWL, and SPARQL help represent, organize, and query linked data.

Imagine a university that publishes information about students,
courses, teachers, research projects, and laboratories. If these
resources are described only in separate documents, it may be
difficult to discover how they are connected. A semantic model can
identify each resource and describe relationships such as a student
enrolling in a course, a teacher supervising a project, or a
laboratory belonging to a department. These explicit relationships
help applications retrieve relevant information more accurately.

Linked Data encourages publishers to use identifiers for resources,
provide useful descriptions, and connect related datasets. When
different organizations follow compatible principles, their data
can be combined to answer questions that no single dataset could
answer alone. For example, a researcher might connect university
publications with author profiles, funding information, and
scientific datasets. The result is a richer view of a research topic
and its surrounding context.

Text analysis can also benefit from structured knowledge. A text
analyzer may count words, identify frequent vocabulary, and explore
collocations, which are words that appear near a target word. If
the target word is data, nearby terms such as linked, semantic,
structured, or query can reveal the themes of a document. Frequency
statistics provide a useful overview, while collocation analysis
helps show how words are used in context. These methods do not fully
understand meaning, but they can support linguistic exploration
and information discovery.

Semantic technologies are useful in digital libraries, e-government,
healthcare information systems, scientific research, and knowledge
graphs. However, building reliable semantic applications requires
careful attention to data quality, shared vocabularies, privacy,
and interoperability. Different systems may use different terms
for the same concept, and poorly maintained datasets can create
misleading connections. Clear metadata and consistent identifiers
make integration more dependable.

Artificial intelligence can complement Semantic Web technologies.
Machine learning can identify patterns in large collections of
documents, while knowledge graphs represent entities and their
relationships explicitly. Combining statistical methods with
structured knowledge can improve search, recommendation, and
question-answering systems. For example, a search engine may use
word frequencies to identify important terms and a knowledge graph
to understand how people, places, organizations, and topics are
related.

The goal is not simply to publish more information, but to make
information easier to discover, connect, and reuse. When data is
described consistently and relationships are made explicit, both
people and software can navigate complex information more
effectively. The Semantic Web therefore offers a foundation for
more interoperable applications, while text analysis provides
practical techniques for exploring the language and structure
of documents.

Another important aspect of text analysis is vocabulary
distribution. Some words appear frequently, while others occur
only once. Studying these differences can help readers understand
the diversity of a text and identify its central themes. Researchers
can compare documents, examine terminology, and investigate how
the use of words changes across different contexts.

Collocations provide another perspective on language. Words that
regularly appear near one another may indicate meaningful
expressions, recurring topics, or relationships within a document.
For example, the words semantic and web often appear together
when a text discusses linked data and machine-readable knowledge.
The size of the context window affects which neighboring words are
counted, so researchers should choose a suitable window for their
analysis and interpret results carefully.

A useful text analyzer combines clear statistics with interactive
visualizations. Bar charts make frequent words easier to compare,
while distribution charts show how vocabulary is spread across
frequency groups. Tables allow users to inspect individual values,
and downloadable files make results easier to reuse in reports or
other applications. These features help transform an ordinary
text document into a source of information that can be explored
systematically.
"""


# --------------------------------------------------
# Text analysis functions
# --------------------------------------------------

def tokenize(text):
    """Extract words and normalize them to lowercase."""
    return re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)


def analyze_frequencies(words):
    """Count the occurrences of each word."""
    return Counter(words)


def analyze_collocations(words, target, window_size):
    """Count words appearing before and after a target word."""
    left = Counter()
    right = Counter()

    positions = [
        i for i, word in enumerate(words)
        if word == target
    ]

    for i in positions:
        start = max(0, i - window_size)
        end = min(len(words), i + window_size + 1)

        left.update(words[start:i])
        right.update(words[i + 1:end])

    return left, right, len(positions)


def make_frequency_text(frequencies):
    """Generate a downloadable TXT report."""
    output = io.StringIO()
    output.write("WORD FREQUENCIES\n")
    output.write("================\n\n")

    for word, count in frequencies.most_common():
        output.write(f"{word}: {count}\n")

    return output.getvalue()


def make_frequency_csv(frequencies):
    """Generate a properly escaped CSV report."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Word", "Frequency"])

    for word, count in frequencies.most_common():
        writer.writerow([word, count])

    return output.getvalue()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📊 Text Analyzer")

st.caption(
    "Explore word frequencies, vocabulary and collocations "
    "through interactive visualizations."
)


# --------------------------------------------------
# Text input
# --------------------------------------------------

st.subheader("📝 Your text")

source = st.radio(
    "Choose your text source",
    ["Use example text", "Upload a .txt file"],
    horizontal=True,
)

uploaded_file = None

if source == "Use example text":

    st.success(
        "The example text is built into this application. "
        "No external file is required."
    )

    # Display the text as a readable TXT-style preview.
    with st.expander("📄 View example.txt", expanded=True):
        st.text_area(
            "Example text",
            value=EXAMPLE_TEXT.strip(),
            height=260,
            disabled=True,
            label_visibility="collapsed",
        )

    # Download the embedded example as a real .txt file.
    st.download_button(
        label="⬇️ Download example.txt",
        data=EXAMPLE_TEXT.strip() + "\n",
        file_name="example.txt",
        mime="text/plain",
    )

    text = EXAMPLE_TEXT

else:
    uploaded_file = st.file_uploader(
        "Choose a text file",
        type=["txt"],
    )

    text = ""

    if uploaded_file is not None:
        try:
            text = uploaded_file.getvalue().decode("utf-8-sig")
        except UnicodeDecodeError:
            st.error(
                "Unable to read this file as UTF-8. "
                "Please upload a UTF-8 encoded text file."
            )


if not text.strip():
    st.info("Load a text file to start the analysis.")
    st.stop()


# --------------------------------------------------
# Compute statistics
# --------------------------------------------------

words = tokenize(text)
frequencies = analyze_frequencies(words)

if not words:
    st.warning("No words were detected in this text.")
    st.stop()

total_words = len(words)
vocabulary_size = len(frequencies)

unique_once = sum(
    1 for count in frequencies.values()
    if count == 1
)

top_words = frequencies.most_common(20)


# --------------------------------------------------
# Summary metrics
# --------------------------------------------------

st.divider()
st.subheader("📌 Overview")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total words", f"{total_words:,}")
m2.metric("Unique words", f"{vocabulary_size:,}")
m3.metric("Words appearing once", f"{unique_once:,}")
m4.metric(
    "Vocabulary ratio",
    f"{vocabulary_size / total_words * 100:.1f}%",
)


# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab_overview, tab_collocations, tab_data = st.tabs([
    "📈 Frequency overview",
    "🔗 Collocations",
    "📋 Data & export",
])


# --------------------------------------------------
# Tab 1: Frequency overview
# --------------------------------------------------

with tab_overview:

    left_panel, right_panel = st.columns([3, 2], gap="large")

    with left_panel:
        st.subheader("Most frequent words")

        max_words = st.slider(
            "Words to display",
            min_value=1,
            max_value=min(30, vocabulary_size),
            value=min(15, vocabulary_size),
        )

        selected_words = frequencies.most_common(max_words)

        chart_data = {
            "Word": [item[0] for item in selected_words],
            "Frequency": [item[1] for item in selected_words],
        }

        fig = px.bar(
            chart_data,
            x="Frequency",
            y="Word",
            orientation="h",
            text="Frequency",
            template="plotly_white",
            color="Frequency",
            color_continuous_scale="Blues",
        )

        fig.update_layout(
            height=max(350, max_words * 27),
            margin=dict(l=10, r=15, t=20, b=10),
            yaxis=dict(autorange="reversed", title=None),
            xaxis_title="Number of occurrences",
            coloraxis_showscale=False,
        )

        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    with right_panel:
        st.subheader("Vocabulary distribution")

        distribution = Counter(frequencies.values())

        distribution_data = [
            {
                "Occurrences per word": str(count),
                "Number of words": amount,
            }
            for count, amount in sorted(distribution.items())
        ]

        fig_dist = px.pie(
            distribution_data,
            names="Occurrences per word",
            values="Number of words",
            hole=0.55,
            template="plotly_white",
        )

        fig_dist.update_layout(
            height=350,
            margin=dict(l=5, r=5, t=20, b=10),
            legend_title_text="Word frequency",
        )

        fig_dist.update_traces(
            textposition="inside",
            textinfo="percent",
        )

        st.plotly_chart(fig_dist, use_container_width=True)

        st.caption(
            "Each slice represents how many different words occur "
            "a given number of times."
        )


# --------------------------------------------------
# Tab 2: Collocations
# --------------------------------------------------

with tab_collocations:

    st.subheader("Explore words around a target")

    all_words = sorted(frequencies.keys())

    settings_col, result_col = st.columns([1, 2], gap="large")

    with settings_col:

        target = st.selectbox(
            "Target word",
            options=all_words,
            index=0,
        )

        window_size = st.slider(
            "Window size",
            min_value=1,
            max_value=10,
            value=2,
            help=(
                "Number of words examined before and after "
                "each occurrence of the target."
            ),
        )

        top_collocations = st.slider(
            "Collocations to display",
            min_value=5,
            max_value=20,
            value=10,
        )

    left_counts, right_counts, occurrences = analyze_collocations(
        words,
        target,
        window_size,
    )

    with result_col:

        st.metric("Target word occurrences", occurrences)

        if occurrences == 0:
            st.info("The selected word was not found.")

        else:
            left_top = left_counts.most_common(top_collocations)
            right_top = right_counts.most_common(top_collocations)

            combined_words = list(dict.fromkeys(
                [word for word, _ in left_top]
                + [word for word, _ in right_top]
            ))

            comparison = [
                {
                    "Word": word,
                    "Left of target": left_counts.get(word, 0),
                    "Right of target": right_counts.get(word, 0),
                }
                for word in combined_words
            ]

            fig_collocations = go.Figure()

            fig_collocations.add_trace(go.Bar(
                name="Left",
                x=[row["Left of target"] for row in comparison],
                y=[row["Word"] for row in comparison],
                orientation="h",
            ))

            fig_collocations.add_trace(go.Bar(
                name="Right",
                x=[row["Right of target"] for row in comparison],
                y=[row["Word"] for row in comparison],
                orientation="h",
            ))

            fig_collocations.update_layout(
                barmode="group",
                template="plotly_white",
                height=max(350, len(comparison) * 32),
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis_title="Occurrences in context",
                yaxis_title=None,
                legend_title_text="Position",
                yaxis=dict(autorange="reversed"),
            )

            st.plotly_chart(
                fig_collocations,
                use_container_width=True,
            )

    st.caption(
        "Counts include all appearances of the target word. "
        "A word can appear on both sides in different contexts."
    )


# --------------------------------------------------
# Tab 3: Tables and export
# --------------------------------------------------

with tab_data:

    st.subheader("Word frequency table")

    search_word = st.text_input(
        "Filter words",
        placeholder="Type a word to search...",
    ).strip().lower()

    rows = [
        {"Word": word, "Frequency": count}
        for word, count in frequencies.most_common()
        if search_word in word
    ]

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        height=400,
    )

    st.download_button(
        label="⬇️ Download all frequencies (.txt)",
        data=make_frequency_text(frequencies),
        file_name="word_frequencies.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.download_button(
        label="⬇️ Download frequencies (.csv)",
        data=make_frequency_csv(frequencies),
        file_name="word_frequencies.csv",
        mime="text/csv",
        use_container_width=True,
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption("Text Analyzer · Python + Streamlit + Plotly")
