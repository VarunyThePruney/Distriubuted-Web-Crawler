import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(
    page_title="Distributed Research Crawler",
    layout="wide"
)

st.title("Distributed Research Paper Dashboard")
st.markdown("Explore crawled arXiv computer science papers")

def get_connection():
    return mysql.connector.connect(
         host="localhost",
        user="crawler_user",
        password="crawler_pass",
        database="crawler_db"
    )

@st.cache_data
def load_data():

    conn = get_connection()

    query = """
    SELECT
        p.id,
        p.paper_id,
        p.title,
        p.abstract,
        p.published,
        p.priority_score,

        GROUP_CONCAT(
            DISTINCT a.name
            SEPARATOR ', '
        ) AS authors,

        GROUP_CONCAT(
            DISTINCT s.name
            SEPARATOR ', '
        ) AS subjects

    FROM papers p

    LEFT JOIN paper_authors pa
        ON p.id = pa.paper_id

    LEFT JOIN authors a
        ON pa.author_id = a.id

    LEFT JOIN paper_subjects ps
        ON p.id = ps.paper_id

    LEFT JOIN subjects s
        ON ps.subject_id = s.id

    GROUP BY p.id

    ORDER BY p.id DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

try:
    df = load_data()

except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()
    
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
            f"**Published:** {row['published'].date() if pd.notnull(row['published']) else 'Unknown'}"
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
