"""
MongoDB NoSQL Operational Database Ingestion Connector
Extracts document-based JSON/BSON collections and flattens them into relational Data Warehouse Staging
"""

import os
from typing import Dict, Optional
import duckdb
import pandas as pd

from src.config import DUCKDB_PATH
from src.utils.logger import logger


def ingest_from_mongodb(
    connection_url: Optional[str] = None,
    db_name: str = "retailsphere_nosql",
    db_path: str = str(DUCKDB_PATH)
) -> Dict[str, int]:
    """
    Ingest document collections from MongoDB into relational DuckDB Staging.
    Flattens nested BSON documents into 2D columnar structure for dimensional modeling.
    """
    mongo_uri = connection_url or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    logger.info(f"Connecting to MongoDB NoSQL Database: {db_name}")
    
    collections = ["customers", "products", "orders", "events"]
    loaded_counts = {}
    
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        mongo_db = client[db_name]
        
        con_duck = duckdb.connect(db_path)
        con_duck.execute("CREATE SCHEMA IF NOT EXISTS staging;")
        
        for coll_name in collections:
            try:
                cursor = mongo_db[coll_name].find()
                docs = list(cursor)
                if docs:
                    # Remove Mongo internal ObjectId if string conversion needed
                    for d in docs:
                        if "_id" in d:
                            d["mongo_id"] = str(d.pop("_id"))
                            
                    df = pd.json_normalize(docs)
                    df["_ingested_at"] = pd.Timestamp.now()
                    df["_source_file"] = f"mongodb://{db_name}/{coll_name}"
                    
                    con_duck.register(f"df_{coll_name}_mongo", df)
                    con_duck.execute(f"CREATE OR REPLACE TABLE staging.stg_mongo_{coll_name} AS SELECT * FROM df_{coll_name}_mongo;")
                    con_duck.unregister(f"df_{coll_name}_mongo")
                    
                    loaded_counts[coll_name] = len(df)
                    logger.info(f"Ingested & flattened {len(df):,} NoSQL documents from MongoDB collection: {coll_name}")
            except Exception as ce:
                logger.warning(f"Could not ingest MongoDB collection '{coll_name}': {str(ce)}")
                
        client.close()
        con_duck.close()
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        
    return loaded_counts
