import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="AModul-Elektro", layout="wide", page_icon="⚡")

st.title("⚡ AModul-Elektro: Nákupný Asistent")

@st.cache_data
def load_data():
    # Načítanie s automatickým odstránením skrytých znakov (utf-8-sig)
    df = pd.read_csv("data.csv", sep=";", decimal=",", encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    
    # Prevod ceny na číslo - berieme Nakupna_EUR (ak chceš predajnú, zmeň názov nižšie)
    df['Nakupna_EUR'] = pd.to_numeric(df['Nakupna_EUR'].astype(str).str.replace(',', '.'), errors='coerce')
    return df

try:
    inventory = load_data()
except Exception as e:
    st.error(f"Chyba pri načítaní: {e}")
    st.stop()

st.subheader("📝 Zadajte dopyt")
user_input = st.text_area("Vložte zoznam (Obj_cislo - Množstvo)", height=150, 
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
                    mnoz_str = re.sub(r'[^\d,.]+', '', parts[1])
                    mnozstvo = float(mnoz_str.replace(',', '.'))
                except:
                    mnozstvo = 0
                
                # Hľadáme v stĺpci 'Obj_cislo' (upravené podľa tvojho CSV)
                match = inventory[inventory['Obj_cislo'].astype(str).str.strip() == vstupny_kod]
                
                if not match.empty:
                    nazov_polozky = match.iloc[0]['Nazov_produktu']
                    cena_jednotka = float(match.iloc[0]['Nakupna_EUR'])
                    spolu = cena_jednotka * mnozstvo
                    total_sum += spolu
                    
                    final_list.append({
                        "Kód (Obj_č)": vstupny_kod,
                        "Položka": nazov_polozky,
                        "Množstvo": mnozstvo,
                        "Cena/MJ": f"{cena_jednotka:.3f} €",
                        "Spolu": f"{spolu:.2f} €"
                    })
                else:
                    final_list.append({"Kód (Obj_č)": vstupny_kod, "Položka": "❌ NENAŠLO SA", "Množstvo": mnozstvo, "Cena/MJ": "-", "Spolu": "-"})

        if final_list:
            df_final = pd.DataFrame(final_list)
            st.table(df_final)
            st.metric("Celková suma objednávky", f"{total_sum:.2f} €")
            st.success("Hotovo!")
    else:
        st.warning("Zadajte zoznam položiek.")

st.markdown("---")
st.subheader("🔍 Prehľadávať cenník")
search = st.text_input("Hľadať produkt (názov alebo číslo)")
if search:
    res = inventory[inventory.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]
    st.dataframe(res)
