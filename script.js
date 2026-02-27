from datetime import date
import unicodedata

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Calories Photos", page_icon="🍽️", layout="wide")

DEFAULT_CALORIES = {"Plat": 550, "Boisson": 120}
KEYWORD_ESTIMATES = {
    "Plat": [
        (["salade", "soupe", "legume", "concombre"], 250),
        (["poisson", "poulet", "grillade", "fruit de mer", "crevette"], 420),
        (["riz", "pates", "pasta", "couscous"], 500),
        (["dessert", "gateau", "tiramisu", "glace"], 450),
        (["pizza", "burger", "tacos", "frites"], 850),
        (["creme", "fromage", "bacon"], 700),
    ],
    "Boisson": [
        (["eau", "the", "cafe"], 5),
        (["jus", "smoothie"], 110),
        (["soda", "cola"], 150),
        (["milkshake"], 300),
        (["vin", "biere", "alcool", "cocktail"], 180),
    ],
}


if "entries" not in st.session_state:
    st.session_state.entries = []


st.title("🍽️ Journal de calories (photos)")
st.write(
    "Ajoute des photos de tes plats et boissons, calcule les calories, "
    "et visualise la consommation par jour."
)


def normalize(text: str) -> str:
    raw = (text or "").lower()
    return "".join(
        char for char in unicodedata.normalize("NFD", raw) if unicodedata.category(char) != "Mn"
    )


def estimate_calories(entry_type: str, name: str) -> tuple[int, str]:
    normalized_name = normalize(name)
    matches: list[tuple[str, int]] = []

    for keywords, calories in KEYWORD_ESTIMATES.get(entry_type, []):
        for keyword in keywords:
            if keyword in normalized_name:
                matches.append((keyword, calories))

    if matches:
        average = round(sum(cal for _, cal in matches) / len(matches))
        return average, matches[0][0]

    return DEFAULT_CALORIES[entry_type], ""


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
        estimated_calories, matched_keyword = estimate_calories(entry_type, name)
        is_manual = calories_input > 0
        calories_per_portion = int(calories_input) if is_manual else estimated_calories
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
                "Mode": (
                    "manuel"
                    if is_manual
                    else f"auto ({matched_keyword})" if matched_keyword else "auto (défaut)"
                ),
                "Image bytes": image.getvalue(),
            }
        )
        st.success("Entrée ajoutée.")

st.info(
    "Si tu ne saisis pas les calories, l'app estime via des mots-clés du nom "
    "(ex: salade, burger, jus). Sinon, elle applique la valeur manuelle."
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
            f"Mode: {entry['Mode']}  \n"
            f"**Total: {entry['Total calories']} kcal**"
        )
    if idx < len(entries):
        st.divider()

st.subheader("Graphique des calories par jour")
chart_df = (
    entries_df.groupby("Date", as_index=False)["Total calories"].sum().sort_values("Date")
)
chart_df = chart_df.rename(columns={"Date": "Jour", "Total calories": "Calories"})
st.bar_chart(chart_df, x="Jour", y="Calories", use_container_width=True)
