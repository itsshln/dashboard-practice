import pandas as pd
from database import engine

query = """
SELECT COUNT(*) AS total_students
FROM students
"""

df = pd.read_sql(query, engine)

print(df)