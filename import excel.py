import pandas as pd
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "p5432"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "practice_db"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

excel_file = "/Users/user/Downloads/practice_students.xlsx"

tables = {
    "students": "students",
    "departments": "departments",
    "mentors": "mentors",
    "practice_requests": "practice_requests",
    "documents": "documents",
    "status_history": "status_history",
    "practice_results": "practice_results"
}

for sheet_name, table_name in tables.items():

    print(f"Импорт листа: {sheet_name}")

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
    )

    print(f"✓ Загружено {len(df)} строк в {table_name}")

print("\nИмпорт завершён успешно!")
