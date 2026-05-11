import time

from scripts.celery_app import celery
from scripts.db import *
from scripts.utils import *

@celery.task(name="scripts.worker.process")
def process(pid):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        paper = parse_abstract(pid)
        paper_id = insert_paper(cursor, paper)

        for a in paper["authors"]:
            aid = insert_author(cursor, a)
            link_paper_author(cursor, paper_id, aid)

        for s in paper["subjects"]:
            sid = insert_subject(cursor, s)
            link_paper_subject(cursor, paper_id, sid)

        kws = extract_keywords(paper["abstract"])

        for k in kws:
            kid = insert_keyword(cursor, k)
            link_paper_keyword(cursor, paper_id, kid)

        stats = compute_stats(paper)
        insert_stats(cursor, paper_id, stats)
        conn.commit()
        print(f"Saved: {pid}")

    except Exception as e:
        conn.rollback()
        print(f"Error: {pid} -> {e}")
        
    finally:
        cursor.close()
        conn.close()

    sleep_time = 15
    print(f"Sleeping {sleep_time}s")
    time.sleep(sleep_time)