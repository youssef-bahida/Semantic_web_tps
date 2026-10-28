
import re
import io
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
# Text analysis functions
# --------------------------------------------------

def tokenize(text):
    """Extract words and normalize them to lowercase."""
    return re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)


def analyze_frequencies(words):
    return Counter(words)


def analyze_collocations(words, target, window_size):
    """Count words occurring before and after the target word."""
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
    output = io.StringIO()
    output.write("WORD FREQUENCIES\n")
    output.write("================\n\n")

    for word, count in frequencies.most_common():
        output.write(f"{word}: {count}\n")

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
# Compact input area
# --------------------------------------------------

with st.container(border=True):
    st.subheader("📝 Your text")

    source_col, upload_col = st.columns([1, 2])

    with source_col:
        source = st.radio(
            "Text source",
            ["Upload a .txt file", "Use example.txt"],
            horizontal=False,
        )

    with upload_col:
        uploaded_file = None

        if source == "Upload a .txt file":
            uploaded_file = st.file_uploader(
                "Choose a text file",
                type=["txt"],
                label_visibility="collapsed",
            )
        else:
            st.info(
                "The app will load example.txt from the same "
                "folder as app.py."
            )

text = ""

if source == "Upload a .txt file":
    if uploaded_file is not None:
        try:
            text = uploaded_file.getvalue().decode("utf-8-sig")
        except UnicodeDecodeError:
            st.error("Unable to read this file as UTF-8 text.")
else:
    try:
        with open("example.txt", "r", encoding="utf-8-sig") as file:
            text = file.read()
    except FileNotFoundError:
        st.warning(
            "example.txt was not found. Add it beside app.py "
            "or choose the upload option."
        )

if not text.strip():
    st.info("Load a text file to start the analysis.")
    st.stop()


# --------------------------------------------------
# Compute statistics
# --------------------------------------------------

words = tokenize(text)
frequencies = analyze_frequencies(words)
vocabulary_size = len(frequencies)
unique_once = sum(1 for count in frequencies.values() if count == 1)
top_words = frequencies.most_common(20)

if not words:
    st.warning("No words were detected in this text.")
    st.stop()


# --------------------------------------------------
# Summary metrics
# --------------------------------------------------

st.subheader("📌 Overview")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total words", f"{len(words):,}")
m2.metric("Unique words", f"{vocabulary_size:,}")
m3.metric("Words appearing once", f"{unique_once:,}")
m4.metric(
    "Vocabulary ratio",
    f"{vocabulary_size / len(words) * 100:.1f}%"
)


# --------------------------------------------------
# Tabs keep the page compact
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
            min_value=5,
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
        fig.update_traces(textposition="outside", cliponaxis=False)

        st.plotly_chart(fig, use_container_width=True)

    with right_panel:
        st.subheader("Vocabulary distribution")

        distribution = Counter(frequencies.values())
        distribution_data = [
            {"Occurrences per word": str(count), "Number of words": amount}
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
        words, target, window_size
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
        "⬇️ Download all frequencies (.txt)",
        data=make_frequency_text(frequencies),
        file_name="word_frequencies.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.download_button(
        "⬇️ Download frequencies (.csv)",
        data=(
            "Word,Frequency\n"
            + "\n".join(
                f'"{word.replace(chr(34), chr(34) * 2)}",{count}'
                for word, count in frequencies.most_common()
            )
        ),
        file_name="word_frequencies.csv",
        mime="text/csv",
        use_container_width=True,
    )


st.divider()
st.caption("Text Analyzer · Python + Streamlit + Plotly")

