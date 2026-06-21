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
    "Студенты": "students",
    "Подразделения": "departments",
    "Наставники": "mentors",
    "Заявки_на_практику": "practice_requests",
    "Документы": "documents",
    "История_статусов": "status_history",
    "Результаты_практики": "practice_results"
}

column_mapping = {

    "students": {
        "ID_студента": "student_id",
        "ФИО": "full_name",
        "ВУЗ": "university",
        "Специальность": "speciality",
        "Email": "email",
        "Телефон": "phone"
    },

    "departments": {
        "ID_подразделения": "department_id",
        "Наименование": "name"
    },

    "mentors": {
        "ID_наставника": "mentor_id",
        "ID_подразделения": "department_id",
        "ФИО": "full_name",
        "Должность": "position"
    },

    "practice_requests": {
        "ID_заявки": "request_id",
        "ID_студента": "student_id",
        "ID_подразделения": "department_id",
        "ID_наставника": "mentor_id",
        "Дата_заявки": "created_at",
        "Дата_согласования": "approved_at",
        "Начало_практики": "practice_start",
        "Окончание_практики": "practice_end",
        "Текущий_статус": "current_status"
    },

    "documents": {
        "ID_документа": "document_id",
        "ID_заявки": "request_id",
        "Тип_документа": "document_type",
        "Дата_загрузки": "upload_date",
        "Корректен": "is_valid"
    },

    "status_history": {
        "ID_истории": "history_id",
        "ID_заявки": "request_id",
        "Статус": "status_name",
        "Дата_изменения": "changed_at"
    },

    "practice_results": {
        "ID_результата": "result_id",
        "ID_заявки": "request_id",
        "Оценка_наставника": "mentor_score",
        "Оценка_подразделения": "department_score",
        "Оценка_студента": "student_score",
        "Рекомендован_в_кадровый_резерв": "reserve_recommendation"
    }
}

for sheet_name, table_name in tables.items():

    print(f"Импорт листа: {sheet_name}")

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name
    )

    if table_name in column_mapping:
        df = df.rename(columns=column_mapping[table_name])

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
    )

    print(f"✓ Загружено {len(df)} строк")

print("Импорт завершён успешно")
