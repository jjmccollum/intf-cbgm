import psycopg2
import pandas as pd
from collections import Counter

# local postgres
conn = psycopg2.connect(
    host="localhost",
    database="matt_ph11",
    user="ntg")

# these manuscripts belong to family 1 only at matthew
hs_list = ('1','22','118','131','205','209','565','872','884','1192','1210','1278','1582','2193','2372','2542','2713','2886')

cur = conn.cursor()
cur.execute("""
SET search_path TO ntg;
SELECT *
FROM (
         SELECT a1.ms_id   as ms1,
                a2.ms_id   as ms2,
                a1.pass_id as pass_id,
                a1.labez   as labez_of_ms1,
                a2.labez   as labez_of_ms2,
                p.begadr,
                p.endadr
         FROM apparatus a1
                  INNER JOIN passages p
                             ON a1.pass_id = p.pass_id
                  INNER JOIN apparatus a2
                             ON a1.pass_id = a2.pass_id
         WHERE a1.ms_id = 11 -- this is HS 1 in Matthew (not Mark!)
           AND a2.ms_id = 85 -- this is HS 1582 in Matthew (not Mark!)
        ORDER BY a1.pass_id
     ) as app
WHERE labez_of_ms1 != labez_of_ms2"""
)

# debug
# df = pd.DataFrame(cur.fetchall(), columns=['ms1', 'ms2', 'pass_id', 'labez_of_ms1', 'labez_of_ms2','begadr','endadr'])
# print(df)

for item in cur.fetchall():
    pid = item[2]
    cur = conn.cursor()
    cur.execute("""
                SELECT app.ms_id,pass_id,labez,lesart,hs FROM ntg.apparatus as app JOIN ntg.manuscripts as mss ON (mss.ms_id = app.ms_id)
                WHERE pass_id = %s
                AND mss.hs IN %s
                ORDER BY labez;
                """,(pid,hs_list,)) # important! note the comma for converting

    records = cur.fetchall()

    # SELECT * FROM ntg.apparatus WHERE ms_id IN (1,2,3);

    # labez is at pos 2
    labez_list = [item[2] for item in records]

    # use "Counter" to count occurences
    counts = dict(Counter(labez_list))

    # calculate percentage
    for k in counts.keys():
        counts[k] = counts[k] / len(labez_list)

    # if this list is empty, we have no majority
    result = [k for k,v in counts.items() if (v > 0.5)]

    if len(result) == 0:
        print(result)
        print('we have a tie!')
        print(counts)
        # debug
        df = pd.DataFrame(records, columns=['ms_id', 'pass_id', 'labez', 'lesart', 'hs'])
        print(df)
