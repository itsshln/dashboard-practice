import streamlit as st
from sqlalchemy import create_engine

engine = create_engine(
    f"postgresql+psycopg2://"
    f"{st.secrets['DB_USER']}:"
    f"{st.secrets['DB_PASSWORD']}@"
    f"{st.secrets['DB_HOST']}:"
    f"{st.secrets['DB_PORT']}/"
    f"{st.secrets['DB_NAME']}",
    connect_args={
        "sslmode": "require"
    }
)