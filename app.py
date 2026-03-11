# --- HLAVNÁ LOGIKA VÝPOČTU ---
st.subheader("📝 Zadajte dopyt")
user_input = st.text_area("Vložte zoznam (Kód alebo Názov - Množstvo)", height=150, 
                          placeholder="752101-10\nCYKY-J 3x1.5 - 50")

default_qty = st.number_input("Predvolené množstvo (ak nie je uvedené v riadku)", min_value=1.0, value=1.0)

if st.button("Vypočítať cenu"):
    if user_input:
        lines = user_input.strip().split('\n')
        final_list = []
        total_sum = 0
        
        for line in lines:
            line = line.strip()
            if not line or "z kazdeho" in line.lower(): continue # Preskočí prázdne riadky a úvodné vety
            
            # Pokus o rozdelenie na Položku a Množstvo (podľa pomlčky vpravo)
            if '-' in line and any(char.isdigit() for char in line.split('-')[-1]):
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
            
            # Vyhľadávanie - najprv skúsime Obj_cislo, potom Nazov_produktu
            match = inventory[
                (inventory['Obj_cislo'].astype(str).str.strip() == hladany_text) | 
                (inventory['Nazov_produktu'].astype(str).str.contains(hladany_text, case=False, na=False))
            ]
            
            if not match.empty:
                # Ak našlo viac položiek (napr. pri CYKY), vezmeme prvú
                hit = match.iloc[0]
                nazov_polozky = hit['Nazov_produktu']
                cena_jednotka = float(hit['Nakupna_EUR'])
                spolu = cena_jednotka * mnozstvo
                total_sum += spolu
                
                final_list.append({
                    "Hľadané": hladany_text,
                    "Nájdené": nazov_polozky,
                    "Množstvo": mnozstvo,
                    "Cena/MJ": f"{cena_jednotka:.3f} €",
                    "Spolu": f"{spolu:.2f} €"
                })
            else:
                final_list.append({"Hľadané": hladany_text, "Nájdené": "❌ NENAŠLO SA", "Množstvo": mnozstvo, "Cena/MJ": "-", "Spolu": "-"})

        if final_list:
            df_final = pd.DataFrame(final_list)
            st.table(df_final)
            st.metric("Celková suma objednávky", f"{total_sum:.2f} €")
