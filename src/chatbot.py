# src/chatbot.py
import streamlit as st
from src.query_engine import build_query_engine

st.title("Recomendador de Artistas")

query_engine = build_query_engine()

prompt = st.text_input("Describe qué estilo de dibujo o pintura te interesa:")

if st.button("Recomendar"):
    with st.spinner("Generando recomendación..."):
        try:
            response = query_engine.query(prompt)
            st.success(str(response))
        except Exception as e:
            st.error(f"Error al obtener la recomendación: {e}")
