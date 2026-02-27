from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Calories Photos", page_icon="🍽️", layout="wide")

DEFAULT_CALORIES = {"Plat": 550, "Boisson": 120}

if "entries" not in st.session_state:
    st.session_state.entries = []

st.title("🍽️ Journal de calories (photos)")
st.write(
    "Ajoute des photos de tes plats et boissons, calcule les calories, "
    "et visualise la consommation par jour."
)

with st.form("add_entry_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        image = st.file_uploader(
            "Photo du plat / boisson", type=["png", "jpg", "jpeg", "webp"]
        )
        entry_type = st.selectbox("Type", options=["Plat", "Boisson"])

    with col2:
        entry_date = st.date_input("Date", value=date.today())
        name = st.text_input("Nom (optionnel)", placeholder="Ex: Salade, Jus d'orange")

    with col3:
        quantity = st.number_input("Quantité", min_value=1, value=1, step=1)
        calories_input = st.number_input(
            "Calories par portion (optionnel)",
            min_value=0,
            value=0,
            step=1,
            help="Laisse 0 pour utiliser l'estimation automatique.",
        )

    submitted = st.form_submit_button("Ajouter l'entrée")

if submitted:
    if image is None:
        st.error("Ajoute une photo avant de valider.")
    else:
        calories_per_portion = (
            int(calories_input) if calories_input > 0 else DEFAULT_CALORIES[entry_type]
        )
        total_calories = calories_per_portion * int(quantity)
        label = name.strip() if name.strip() else f"{entry_type} sans nom"

        st.session_state.entries.append(
            {
                "Date": entry_date,
                "Type": entry_type,
                "Nom": label,
                "Quantité": int(quantity),
                "Calories/portion": int(calories_per_portion),
                "Total calories": int(total_calories),
                "Image bytes": image.getvalue(),
                "Image type": image.type,
            }
        )
        st.success("Entrée ajoutée.")

st.info(
    "Estimation automatique utilisée si calories non renseignées : "
    "Plat = 550 kcal/portion, Boisson = 120 kcal/portion."
)

entries = st.session_state.entries

if not entries:
    st.warning("Aucune entrée pour le moment.")
    st.stop()

entries_df = pd.DataFrame(entries)

st.subheader("Total des calories pour une journée")
selected_date = st.date_input("Choisis une date", value=date.today(), key="selected_day")
daily_total = int(
    entries_df.loc[entries_df["Date"] == selected_date, "Total calories"].sum()
)
st.metric("Calories consommées", f"{daily_total} kcal")

st.subheader("Historique")
for idx, entry in enumerate(reversed(entries), start=1):
    left, right = st.columns([1, 3])
    with left:
        st.image(entry["Image bytes"], use_container_width=True)
    with right:
        st.markdown(
            f"**{entry['Nom']}**  \n"
            f"Date: {entry['Date']} • Type: {entry['Type']}  \n"
            f"Quantité: {entry['Quantité']} • Calories/portion: {entry['Calories/portion']}  \n"
            f"**Total: {entry['Total calories']} kcal**"
        )
    if idx < len(entries):
        st.divider()

st.subheader("Graphique des calories par jour")
chart_df = entries_df.groupby("Date", as_index=False)["Total calories"].sum().sort_values("Date")
chart_df = chart_df.rename(columns={"Date": "Jour", "Total calories": "Calories"})
st.bar_chart(chart_df, x="Jour", y="Calories", use_container_width=True)
