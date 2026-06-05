import streamlit as st
from sqlalchemy import create_engine, event

engine = create_engine(
    f"postgresql+psycopg2://"
    f"{st.secrets['DB_USER']}:"
    f"{st.secrets['DB_PASSWORD']}@"
    f"{st.secrets['DB_HOST']}:"
    f"{st.secrets['DB_PORT']}/"
    f"{st.secrets['DB_NAME']}",
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
)

@event.listens_for(engine, "connect")
def set_search_path(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET search_path TO public")
    cursor.close()