from __future__ import annotations
from pathlib import Path
import sqlite3, json, time
import pandas as pd
from .config import settings

DDL="""CREATE TABLE IF NOT EXISTS interactions(
 id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT DEFAULT CURRENT_TIMESTAMP, query TEXT, intent TEXT,
 provider TEXT, latency_ms REAL, confidence TEXT, grounded INTEGER, abstained INTEGER, feedback INTEGER,
 metadata TEXT);"""

def _connect():
    path=settings.resolve(settings.monitoring_db); path.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(path); con.execute(DDL); con.commit(); return con

def log_interaction(query, intent, provider, latency_ms, confidence, grounded, abstained, metadata=None):
    con=_connect(); con.execute("INSERT INTO interactions(query,intent,provider,latency_ms,confidence,grounded,abstained,metadata) VALUES(?,?,?,?,?,?,?,?)",
        (query,intent,provider,latency_ms,confidence,int(grounded),int(abstained),json.dumps(metadata or {},default=str)))
    rowid=con.execute("SELECT last_insert_rowid()").fetchone()[0]; con.commit(); con.close(); return rowid

def record_feedback(rowid:int,value:int):
    con=_connect(); con.execute("UPDATE interactions SET feedback=? WHERE id=?",(value,rowid)); con.commit(); con.close()

def interactions() -> pd.DataFrame:
    con=_connect(); df=pd.read_sql_query("SELECT * FROM interactions ORDER BY id",con); con.close(); return df
