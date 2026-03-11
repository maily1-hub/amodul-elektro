import streamlit as st
import pandas as pd
import os

st.title("Test pripojenia súboru")

# Skontrolujeme, čo vidí systém
st.write("Súbory v priečinku:", os.listdir("."))

if os.path.exists("data.csv"):
    st.success("Súbor data.csv bol nájdený!")
    df = pd.read_csv("data.csv")
    st.write("Ukážka dát:")
    st.dataframe(df.head())
else:
    st.error("Súbor data.csv sa nenašiel v koreňovom adresári.")
