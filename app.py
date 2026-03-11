import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="AModul-Elektro", layout="wide", page_icon="⚡")

st.title("⚡ AModul-Elektro: Nákupný Asistent")

@st.cache_data
def load_data():
    # Načítanie s ošetrením skrytých znakov
    df = pd.read_csv("data.csv", sep=";", decimal=",", encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    
    # AUTOMATICKÁ IDENTIFIKÁCIA STĹPCOV (podľa kľúčových slov)
    for col in df.columns:
        if 'Obj' in col: df.rename(columns={col: 'Obj_cislo'}, inplace=True)
        if 'Nazov' in col or 'Názov' in col: df.rename(columns={col: 'Nazov_produktu'}, inplace=True)
        if 'Nakupna' in col or 'Nákupná' in col: df.rename(columns={col: 'Cena_jednotka'}, inplace=True)
    
    # Prevod ceny na číslo (očista od bordelu)
    if 'Cena_jednotka' in df.columns:
        df['Cena_jednotka'] = pd.to_numeric(df['Cena_jednotka'].astype(str).str.replace(',', '.'), errors='coerce')
    
    return df

try:
    inventory = load_data()
    st.success("Cenník bol úspešne prepojený.")
except Exception as e:
    st.error(f"Chyba pri načítaní databázy: {e}")
    st.stop()

# --- HLAVNÁ LOGIKA VÝPOČTU ---
st.subheader("📝 Zadajte dopyt")
user_input = st.text_area("Vložte zoznam (Kód alebo Názov - Množstvo)", height=150, 
                          placeholder="752101-10\nCYKY-J 3x1.5 - 50")

default_qty = st.number_input("Predvolené množstvo (ak v riadku chýba)", min_value=1.0, value=10.0)

if st.button("Vypočítať cenu"):
    if user_input:
        lines = user_input.strip().split('\n')
        final_list = []
        total_sum = 0
        
        for line in lines:
            line = line.strip()
            if not line or any(x in line.lower() for x in ["z kazdeho", "dobry", "prosim"]): continue
            
            # Rozdelenie na text a množstvo
            if '-' in line:
                parts = line.rsplit('-', 1)
                hladany_text = parts[0].strip()
                try:
                    mnoz_str = re.sub(r'[^\d,.]+', '', parts[1])
                    mnozstvo = float(mnoz_str.replace(',', '.'))
                except:
                    mnozstvo = default_qty
            else:
                hladany_text = line
                mnozstvo = default_qty
            
            # Vyhľadávanie v kóde aj v názve
            match = inventory[
                (inventory['Obj_cislo'].astype(str).str.strip() == hladany_text) | 
                (inventory['Nazov_produktu'].astype(str).str.contains(hladany_text, case=False, na=False))
            ]
            
            if not match.empty:
                hit = match.iloc[0]
                nazov_polozky = hit['Nazov_produktu']
                cena = float(hit['Cena_jednotka']) if not pd.isna(hit['Cena_jednotka']) else 0
                spolu = cena * mnozstvo
                total_sum += spolu
                
                final_list.append({
                    "Položka": nazov_polozky,
                    "Množstvo": mnozstvo,
                    "Cena/MJ": f"{cena:.3f} €",
                    "Spolu": f"{spolu:.2f} €"
                })
            else:
                final_list.append({"Položka": f"❌ {hladany_text} (Nenájdené)", "Množstvo": mnozstvo, "Cena/MJ": "-", "Spolu": "-"})

        if final_list:
            st.table(pd.DataFrame(final_list))
            st.metric("Celková suma bez DPH", f"{total_sum:.2f} €")
    else:
        st.warning("Zadajte zoznam položiek.")

st.markdown("---")
st.subheader("🔍 Rýchly náhľad do cenníka")
search = st.text_input("Hľadať v databáze")
if search:
    st.dataframe(inventory[inventory.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)])
