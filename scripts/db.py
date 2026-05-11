import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "crawler_user",
    "password": "crawler_pass",
    "database": "crawler_db"
}

def get_connection():
    return mysql.connector.connect(
        **DB_CONFIG
    )

def insert_paper(cursor, paper):
    query = """
    INSERT IGNORE INTO papers
    (
        paper_id,
        title,
        abstract,
        published,
        priority_score
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        paper["paper_id"],
        paper["title"],
        paper["abstract"],
        paper["published"],
        paper["priority_score"]
    )

    cursor.execute(query, values)

    cursor.execute(
        """
        SELECT id
        FROM papers
        WHERE paper_id=%s
        """,
        (paper["paper_id"],)
    )

    result = cursor.fetchone()
    return result[0]

def insert_author(cursor, name):
    cursor.execute(
        """
        INSERT IGNORE INTO authors(name)
        VALUES (%s)
        """,
        (name,)
    )

    cursor.execute(
        """
        SELECT id
        FROM authors
        WHERE name=%s
        """,
        (name,)
    )
    return cursor.fetchone()[0]

def insert_subject(cursor, subject):
    cursor.execute(
        """
        INSERT IGNORE INTO subjects(name)
        VALUES (%s)
        """,
        (subject,)
    )

    cursor.execute(
        """
        SELECT id
        FROM subjects
        WHERE name=%s
        """,
        (subject,)
    )

    return cursor.fetchone()[0]

def insert_keyword(cursor, keyword):
    cursor.execute(
        """
        INSERT IGNORE INTO keywords(word)
        VALUES (%s)
        """,
        (keyword,)
    )

    cursor.execute(
        """
        SELECT id
        FROM keywords
        WHERE word=%s
        """,
        (keyword,)
    )

    return cursor.fetchone()[0]

def link_paper_author(cursor, paper_id, author_id):
    cursor.execute(
        """
        INSERT IGNORE INTO paper_authors
        (paper_id, author_id)
        VALUES (%s, %s)
        """,
        (paper_id, author_id)
    )

def link_paper_subject(cursor, paper_id, subject_id):
    cursor.execute(
        """
        INSERT IGNORE INTO paper_subjects
        (paper_id, subject_id)
        VALUES (%s, %s)
        """,
        (paper_id, subject_id)
    )
    
def link_paper_keyword(cursor, paper_id, keyword_id):
    cursor.execute(
        """
        INSERT IGNORE INTO paper_keywords
        (paper_id, keyword_id)
        VALUES (%s, %s)
        """,
        (paper_id, keyword_id)
    )

def insert_stats(cursor, paper_id, stats):
    cursor.execute(
        """
        INSERT IGNORE INTO paper_stats
        (
            paper_id,
            word_count,
            keyword_count
        )
        VALUES (%s, %s, %s)
        """,
        (
            paper_id,
            stats["word_count"],
            stats["keyword_count"]
        )
    )