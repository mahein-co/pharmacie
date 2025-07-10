import duckdb
import pandas as pd

def init_duckdb(df):
    """Initialise la base DuckDB avec les données de la pharmacie."""
    if df is not None:
        con = duckdb.connect(database=":memory:")
        con.register("df_view", df)
        con.execute("CREATE TABLE pharmacie AS SELECT * FROM df_view")
        return con
    return None