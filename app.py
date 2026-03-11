import streamlit as st
import pandas as pd

# 1. NASTAVENIE STRÁNKY
st.set_page_config(page_title="AModul-Elektro", layout="wide")
st.title("⚡ AModul-Elektro: Nákupný Asistent")

# 2. NAČÍTANIE DÁT (Váš upravený súbor)
@st.cache_data
def load_data():
    # Tu načítame váš excel/csv s nákupnými cenami
    df = pd.read_csv("data.csv") 
    return df

try:
    inventory = load_data()
except:
    st.error("Chýba dátový súbor 'data.csv'!")
    st.stop()

# 3. VSTUP OD ZÁKAZNÍKA
st.subheader("Zadajte dopyt (Formát: Kód - Množstvo)")
user_input = st.text_area("Príklad: 752101 - 10, 3559-A01345 - 5", height=150)

if st.button("Vytvoriť objednávku"):
    orders = []
    total_price = 0
    total_profit = 0
    
    # Spracovanie textu na riadky
    lines = user_input.strip().split('\n')
    for line in lines:
        if '-' in line:
            kod, mnozstvo = line.split('-')
            kod = kod.strip()
            qty = int(mnozstvo.strip())
            
            # Vyhľadanie v databáze
            item = inventory[inventory['Kod'] == kod]
            if not item.empty:
                row = item.iloc[0]
                predaj_j = row['Predajna_EUR']
                nakup_j = row['Nakupna_EUR']
                sklad = row['Sklad_ks']
                vyrobca = row['Sklad_vyrobcu']
                
                # Logika dostupnosti
                if qty <= sklad:
                    status = "✅ SKLADOM - Ihneď"
                elif qty <= (sklad + vyrobca):
                    status = "🕒 DOSTUPNÉ - 24/48h"
                else:
                    status = f"❌ NA DOPYT (chýba {qty - (sklad + vyrobca)} ks)"
                
                total_item = predaj_j * qty
                total_price += total_item
                total_profit += (predaj_j - nakup_j) * qty
                
                orders.append({
                    "Kód": kod,
                    "Názov": row['Nazov'],
                    "Množstvo": qty,
                    "Cena/j": f"{predaj_j:.2f} €",
                    "Celkom": f"{total_item:.2f} €",
                    "Dostupnosť": status
                })

    # ZOBRAZENIE VÝSLEDKOV
    if orders:
        st.table(pd.DataFrame(orders))
        st.success(f"### Celková cena objednávky: {total_price:.2f} € s DPH")
        
        # INTERNÁ SEKCIA (Chránená heslom alebo skrytá)
        with st.expander("🔑 Interná zóna (Iba pre majiteľa)"):
            st.write(f"**Čistý zisk z tejto objednávky:** {total_profit:.2f} €")

            st.write(f"**Marža:** {((total_profit/total_price)*100):.1f} %")

