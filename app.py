import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="AModul-Elektro", layout="wide", page_icon="⚡")

st.title("⚡ AModul-Elektro: Nákupný Asistent")

@st.cache_data
def load_data():
    # Načítame CSV a povieme Pythonu, že desatinná čiarka je čiarka
    df = pd.read_csv("data.csv", sep=";", decimal=",")
    df.columns = df.columns.str.strip()
    # Pre istotu ešte raz vynútime konverziu stĺpca s cenou na číslo
    df['Cena_bez_DPH'] = pd.to_numeric(df['Cena_bez_DPH'].astype(str).str.replace(',', '.'), errors='coerce')
    return df

try:
    inventory = load_data()
except Exception as e:
    st.error(f"Chyba pri načítaní: {e}")
    st.stop()

# --- HLAVNÁ LOGIKA VÝPOČTU ---
st.subheader("📝 Zadajte dopyt")
user_input = st.text_area("Vložte zoznam (Kód - Množstvo)", height=150, 
                          placeholder="752101-10\n752102-3")

if st.button("Vypočítať cenu"):
    if user_input:
        lines = user_input.strip().split('\n')
        final_list = []
        total_sum = 0
        
        for line in lines:
            parts = re.split(r'[- \t]+', line.strip())
            if len(parts) >= 2:
                kod = str(parts[0]).strip()
                try:
                    mnozystvo_str = re.sub(r'[^\d,.]+', '', parts[1])
                    mnozstvo = float(mnozystvo_str.replace(',', '.'))
                except:
                    mnozstvo = 0
                
                match = inventory[inventory['Kód'].astype(str).str.strip() == kod]
                
                if not match.empty:
                    nazov = match.iloc[0]['Názov']
                    cena_jednotka = float(match.iloc[0]['Cena_bez_DPH'])
                    spolu = cena_jednotka * mnozstvo
                    total_sum += spolu
                    
                    final_list.append({
                        "Kód": kod,
                        "Položka": nazov,
                        "Množstvo": mnozstvo,
                        "Cena/MJ": f"{cena_jednotka:.3f} €",
                        "Spolu bez DPH": f"{spolu:.2f} €"
                    })
                else:
                    final_list.append({"Kód": kod, "Položka": "❌ NENAŠLO SA", "Množstvo": mnozstvo, "Cena/MJ": "-", "Spolu bez DPH": "-"})

        if final_list:
            df_final = pd.DataFrame(final_list)
            st.table(df_final)
            st.metric("Celková cena objednávky (bez DPH)", f"{total_sum:.2f} €")
            st.success("Výpočet hotový!")
    else:
        st.warning("Zadajte zoznam položiek.")

st.markdown("---")
st.subheader("🔍 Rýchle vyhľadávanie v cenníku")
search = st.text_input("Hľadať podľa názvu alebo kódu")
if search:
    res = inventory[inventory.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(res)
