
import sqlite3

def convert_sqlite_to_csv(db_file, csv_filename='database.csv'):
    with sqlite3.connect(db_file, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES) as conn:
        db_df = pd.read_sql_query("SELECT * FROM SIM_EVENTS", conn)
    db_df.to_csv(csv_filename, index=False)
    return db_df
