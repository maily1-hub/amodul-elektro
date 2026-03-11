import streamlit as st
import pandas as pd

# 1. NASTAVENIE STRÁNKY
st.set_page_config(page_title="AModul-Elektro", layout="wide", page_icon="⚡")

st.title("⚡ AModul-Elektro: Nákupný Asistent")
st.markdown("---")

# 2. FUNKCIA NA NAČÍTANIE DÁT
@st.cache_data
def load_data():
    try:
        # Skúsime načítať s bodkočiarkou, čo je štandard pre slovenský Excel
        df = pd.read_csv("data.csv", sep=";", encoding="utf-8")
    except:
        # Ak by to zlyhalo, skúsime automatickú detekciu
        df = pd.read_csv("data.csv", sep=None, engine="python", encoding="utf-8")
    return df

# Načítanie databázy
try:
    inventory = load_data()
    st.success("Databáza produktov bola úspešne načítaná.")
except Exception as e:
    st.error(f"Chyba pri načítaní súboru: {e}")
    st.stop()

# 3. HLAVNÁ ČASŤ - VYHĽADÁVANIE
st.subheader("🔍 Vyhľadávanie v cenníku")
search_query = st.text_input("Zadajte názov tovaru alebo kód (napr. kábel, istič...)", "")

if search_query:
    # Vyhľadávanie v stĺpcoch (predpokladáme, že máš stĺpce 'Názov' alebo 'Kód')
    # Kód je odolný voči veľkým/malým písmenám
    mask = inventory.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
    results = inventory[mask]
    
    if not results.empty:
        st.write(f"Nájdené položky ({len(results)}):")
        st.dataframe(results, use_container_width=True)
    else:
        st.warning("Nenašli sa žiadne zhodné položky.")

st.markdown("---")

# 4. SEKCOA PRE OBJEDNÁVKU
st.subheader("📝 Rýchly dopyt")
user_input = st.text_area("Sem vložte zoznam (Kód - Množstvo)", height=150, placeholder="752101 - 10ks\n752102 - 5ks")

if st.button("Overiť dostupnosť a cenu"):
    if user_input:
        st.info("Logika pre hromadné spracovanie dopytu bude doplnená v ďalšom kroku.")
    else:
        st.warning("Najskôr zadajte nejaký text.")

# PÄTIČKA
st.sidebar.info("Verzia 1.0 - Pripojené k data.csv")
