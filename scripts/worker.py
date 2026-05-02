import redis
import time
from db import *
from utils import *

r = redis.Redis(host='localhost', port=6379, db=0)


def process(pid, cursor, conn):
    paper = parse_abstract(pid, r)

    paper_id = insert_paper(cursor, paper)

    # Authors
    for a in paper["authors"]:
        aid = insert_author(cursor, a)
        link_paper_author(cursor, paper_id, aid)

    # Subjects
    for s in paper["subjects"]:
        sid = insert_subject(cursor, s)
        link_paper_subject(cursor, paper_id, sid)

    # Keywords
    kws = extract_keywords(paper["abstract"])
    for k in kws:
        kid = insert_keyword(cursor, k)
        link_paper_keyword(cursor, paper_id, kid)

    # Stats
    stats = compute_stats(paper)
    insert_stats(cursor, paper_id, stats)

    conn.commit()


def main():
    conn = get_connection()
    cursor = conn.cursor()

    print("Worker started...")

    while True:
        item = r.zpopmin("paper_queue")

        if not item:
            time.sleep(1)
            continue
        pid = item[0][0].decode()

        try:
            print(f"Processing: {pid}")
            process(pid, cursor, conn)

        except Exception as e:
            print(f"Error: {pid} -> {e}")
            conn.rollback()


if __name__ == "__main__":
    main()