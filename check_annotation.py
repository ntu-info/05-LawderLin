# Check annotation.parquet

import pyarrow.parquet as pq
import pandas as pd

file_path = 'annotations.parquet'
try:
    table = pq.read_table(file_path)
    df = table.to_pandas()
    # terms = [col.split("terms_abstract_tfidf__") for col in df.columns.tolist() if "terms_abstract_tfidf__" in col]
    # terms = [term for term in terms if not term[1].isdigit()]  # Filter out numbers

    print(df["weight"])
    
    """
    print("Parquet file read successfully.")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Number of rows: {len(df)}")
    print("Sample data:")
    print(df.head())

    # Write column names to a text file
    with open('annotation_columns.txt', 'w') as f:
        for col in df.columns:
            if "terms_abstract_tfidf__" in col:
                f.write(f"{col.split('terms_abstract_tfidf__')[1]}\n")
    """
except Exception as e:
    print(f"Failed to read Parquet file: {e}")