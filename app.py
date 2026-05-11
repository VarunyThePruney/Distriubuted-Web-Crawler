import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Distributed Research Crawler",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Distributed Research Paper Dashboard")
st.markdown("Explore crawled arXiv computer science papers")

# =========================
# DATABASE CONNECTION
# =========================

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="crawler_user",
        password="crawler_pass",
        database="crawler_db"
    )

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():

    conn = get_connection()

    query = """
    SELECT
        paper_id,
        title,
        authors,
        abstract,
        subjects,
        published,
        priority_score
    FROM papers
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# =========================
# LOAD DATABASE
# =========================

try:
    df = load_data()

except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.header("Filters")

# Search bar
search_query = st.sidebar.text_input(
    "Search Papers",
    placeholder="Search title or abstract"
)

# AI filter
ai_only = st.sidebar.checkbox("AI-related papers only")

# Priority slider
max_priority = int(df["priority_score"].max())

priority_range = st.sidebar.slider(
    "Priority Range",
    min_value=0,
    max_value=max_priority,
    value=(0, max_priority)
)

# Sorting
sort_option = st.sidebar.selectbox(
    "Sort By",
    ["Priority", "Newest"]
)

# =========================
# FILTERING LOGIC
# =========================

filtered_df = df.copy()

# Search filtering
if search_query:

    filtered_df = filtered_df[
        filtered_df["title"].str.contains(
            search_query,
            case=False,
            na=False
        )

        |

        filtered_df["abstract"].str.contains(
            search_query,
            case=False,
            na=False
        )
    ]

# AI keywords
AI_KEYWORDS = [
    "llm",
    "ai",
    "machine learning",
    "deep learning",
    "transformer",
    "neural"
]

# AI filtering
if ai_only:

    pattern = "|".join(AI_KEYWORDS)

    filtered_df = filtered_df[
        filtered_df["title"].str.contains(
            pattern,
            case=False,
            na=False
        )

        |

        filtered_df["abstract"].str.contains(
            pattern,
            case=False,
            na=False
        )
    ]

# Priority filtering
filtered_df = filtered_df[
    (filtered_df["priority_score"] >= priority_range[0])

    &

    (filtered_df["priority_score"] <= priority_range[1])
]

# Sorting
if sort_option == "Priority":

    filtered_df = filtered_df.sort_values(
        by="priority_score"
    )

else:

    filtered_df = filtered_df.sort_values(
        by="published",
        ascending=False
    )

# =========================
# METRICS
# =========================

st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

# Total papers
col1.metric(
    "Total Papers",
    len(filtered_df)
)

# Average priority
avg_priority = round(
    filtered_df["priority_score"].mean(),
    2
)

col2.metric(
    "Average Priority",
    avg_priority
)

# AI keyword count
ai_count = 0

for kw in AI_KEYWORDS:

    ai_count += filtered_df["title"].str.contains(
        kw,
        case=False,
        na=False
    ).sum()

col3.metric(
    "AI Keyword Matches",
    ai_count
)

# =========================
# ANALYTICS CHART
# =========================

st.subheader("Priority Distribution")

fig, ax = plt.subplots(figsize=(8, 4))

filtered_df["priority_score"].hist(
    ax=ax,
    bins=20
)

ax.set_xlabel("Priority Score")
ax.set_ylabel("Paper Count")

st.pyplot(fig)

# =========================
# PAPER DISPLAY
# =========================

st.subheader("Papers")

for _, row in filtered_df.iterrows():

    with st.container(border=True):

        st.markdown(f"## {row['title']}")

        st.markdown(
            f"**Paper ID:** {row['paper_id']}"
        )

        st.markdown(
            f"**Authors:** {row['authors']}"
        )

        st.markdown(
            f"**Subjects:** {row['subjects']}"
        )

        st.markdown(
            f"**Published:** {row['published']}"
        )

        st.markdown(
            f"**Priority Score:** {row['priority_score']}"
        )

        st.markdown("### Abstract")

        st.write(row["abstract"])

        paper_url = (
            f"https://arxiv.org/abs/{row['paper_id']}"
        )

        st.link_button(
            "Open Paper",
            paper_url
        )

        st.divider()