import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Calorie Tracker",
    page_icon="🥗",
    layout="centered"
)

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

components.html(html, height=900, scrolling=True)
