import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="AModul-Elektro", layout="wide", page_icon="⚡")

st.title("⚡ AModul-Elektro: Nákupný Asistent")

@st.cache_data
def load_data():
    # Použijeme encoding='utf-8-sig', ktorý automaticky odstráni neviditeľné BOM znaky
    df = pd.read_csv("data.csv", sep=";", decimal=",", encoding='utf-8-sig')
    
    # Vyčistíme názvy stĺpcov od medzier a skrytých znakov
    df.columns = df.columns.str.strip()
    
    # Pre istotu: ak sa stĺpec volá inak, skúsime ho nájsť podľa obsahu
    # (Tento riadok premenuje prvý stĺpec na 'Kód', ak by sa volal akokoľvek divne)
    df.rename(columns={df.columns[0]: 'Kód'}, inplace=True)
    
    # Prevod ceny na číslo
    df['Cena_bez_DPH'] = pd.to_numeric(df['Cena_bez_DPH'].astype(str).str.replace(',', '.'), errors='coerce')
    return df

try:
    inventory = load_data()
except Exception as e:
    st.error(f"Chyba pri načítaní databázy: {e}")
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
            # Rozdelenie podľa pomlčky alebo medzery
            parts = re.split(r'[- \t]+', line.strip())
            if len(parts) >= 2:
                vstupny_kod = str(parts[0]).strip()
                try:
                    mnozystvo_str = re.sub(r'[^\d,.]+', '', parts[1])
                    mnozstvo = float(mnozystvo_str.replace(',', '.'))
                except:
                    mnozstvo = 0
                
                # Vyhľadávanie (odolné voči formátu kódu)
                match = inventory[inventory['Kód'].astype(str).str.strip() == vstupny_kod]
                
                if not match.empty:
                    priezvisko = match.iloc[0]['Názov']
                    cena_jednotka = float(match.iloc[0]['Cena_bez_DPH'])
                    spolu = cena_jednotka * mnozstvo
                    total_sum += spolu
                    
                    final_list.append({
                        "Kód": vstupny_kod,
                        "Položka": priezvisko,
                        "Množstvo": mnozstvo,
                        "Cena/MJ": f"{cena_jednotka:.3f} €",
                        "Spolu bez DPH": f"{spolu:.2f} €"
                    })
                else:
                    final_list.append({"Kód": vstupny_kod, "Položka": "❌ NENAŠLO SA", "Množstvo": mnozstvo, "Cena/MJ": "-", "Spolu bez DPH": "-"})

        if final_list:
            df_final = pd.DataFrame(final_list)
            st.table(df_final)
            st.metric("Celková cena objednávky (bez DPH)", f"{total_sum:.2f} €")
            st.success("Výpočet úspešne dokončený!")
    else:
        st.warning("Zadajte zoznam položiek na spracovanie.")

st.markdown("---")
st.subheader("🔍 Prehliadať cenník")
search = st.text_input("Hľadať v databáze (názov/kód)")
if search:
    res = inventory[inventory.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(res)
