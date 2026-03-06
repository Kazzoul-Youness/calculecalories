import streamlit as st
import requests
import base64
import json
from datetime import datetime, date, timedelta
import io

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Calorie Tracker", page_icon="🥗", layout="centered")

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL_VISION = "meta-llama/llama-3.2-11b-vision-instruct:free"
MODEL_TEXT   = "google/gemma-3-12b-it:free"
API_URL      = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://calculecalories.streamlit.app",
    "X-Title": "Calorie Tracker"
}

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "profile": None,
        "meals": [],
        "water": 0,
        "history": {},
        "last_day": str(date.today()),
        "page": "journal",
        "pending_meal": None,
        "pending_meal_txt": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    today = str(date.today())
    if st.session_state.last_day != today:
        total = sum(m["calories"] for m in st.session_state.meals)
        st.session_state.history[st.session_state.last_day] = {
            "calories": total,
            "meals": st.session_state.meals.copy()
        }
        st.session_state.meals = []
        st.session_state.water = 0
        st.session_state.last_day = today

init_state()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header {visibility: hidden;}
  .block-container {padding: 1rem 1rem 5rem !important;}
  .big-num {font-size: 2.5rem; font-weight: 800; color: #6c63ff; text-align: center;}
  .meal-row {display: flex; justify-content: space-between; padding: 8px 0;
             border-bottom: 1px solid #f0f0f0;}
  .badge-green {background:#e8fff0;color:#1a8a4a;border:1.5px solid #b3f0ce;
                border-radius:10px;padding:8px 12px;font-weight:600;margin-top:8px;display:block;}
  .badge-red {background:#fff0f0;color:#c0392b;border:1.5px solid #ffc0c0;
              border-radius:10px;padding:8px 12px;font-weight:600;margin-top:8px;display:block;}
  .badge-warn {background:#fff8e1;color:#b86e00;border:1.5px solid #ffe0a0;
               border-radius:10px;padding:8px 12px;font-weight:600;margin-top:8px;display:block;}
</style>
""", unsafe_allow_html=True)

# ── OpenRouter helpers ────────────────────────────────────────────────────────
PROMPT_JSON = 'Réponds UNIQUEMENT en JSON valide sans markdown ni backticks: {"name":"Nom du plat","calories":350,"emoji":"🍝","details":"1 phrase explication"}'

def call_openrouter(messages: list, model: str) -> dict:
    resp = requests.post(API_URL, headers=HEADERS, json={
        "model": model,
        "max_tokens": 300,
        "messages": messages
    }, timeout=30)
    if not resp.ok:
        raise Exception(f"OpenRouter error {resp.status_code}: {resp.text}")
    raw = resp.json()["choices"][0]["message"]["content"]
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def analyze_image(img_bytes: bytes) -> dict:
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")  # fix PNG/RGBA
    img.thumbnail((800, 800))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return call_openrouter([{
        "role": "user",
        "content": [
            {"type": "text", "text": f"Analyse ce plat et estime les calories totales. {PROMPT_JSON}"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]
    }], MODEL_VISION)

def analyze_text(txt: str) -> dict:
    return call_openrouter([{
        "role": "user",
        "content": f'L\'utilisateur a mangé: "{txt}". Estime les calories totales. {PROMPT_JSON}'
    }], MODEL_TEXT)

# ── Navigation ────────────────────────────────────────────────────────────────
cols = st.columns(4)
for pg, ic, lb in [("journal","🍽️","Journal"),("eau","💧","Eau"),("historique","📊","Historique"),("profil","👤","Profil")]:
    with cols[["journal","eau","historique","profil"].index(pg)]:
        if st.button(f"{ic} {lb}", key=f"nav_{pg}", use_container_width=True):
            st.session_state.page = pg
            st.rerun()

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SETUP PROFIL
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.profile is None:
    st.markdown("### 👋 Configure ton profil")
    prenom = st.text_input("Prénom")
    sex    = st.radio("Sexe", ["👨 Homme", "👩 Femme"], horizontal=True)
    age    = st.number_input("Âge", 10, 100, 30)
    poids  = st.number_input("Poids (kg)", 30.0, 300.0, 70.0)
    taille = st.number_input("Taille (cm)", 100.0, 250.0, 170.0)
    act_options = {
        "😴 Sédentaire": 1.2,
        "🚶 Légèrement actif (1-3x/sem)": 1.375,
        "🏃 Modérément actif (3-5x/sem)": 1.55,
        "💪 Très actif (6-7x/sem)": 1.725,
        "🔥 Sport intense quotidien": 1.9
    }
    activite_label = st.selectbox("Niveau d'activité", list(act_options.keys()))

    if st.button("✅ Calculer mon objectif", use_container_width=True, type="primary"):
        if prenom:
            s    = "h" if "Homme" in sex else "f"
            bmr  = (10*poids + 6.25*taille - 5*age + 5) if s=="h" else (10*poids + 6.25*taille - 5*age - 161)
            tdee = round(bmr * act_options[activite_label])
            st.session_state.profile = {
                "prenom": prenom, "sex": s, "age": age,
                "poids": poids, "taille": taille,
                "bmr": round(bmr), "tdee": tdee,
                "objectif": tdee - 500,
                "waterGoal": round((poids * 35) / 250)
            }
            st.session_state.page = "journal"
            st.rerun()
        else:
            st.warning("Entre ton prénom !")
    st.stop()

p = st.session_state.profile

# ══════════════════════════════════════════════════════════════════════════════
# JOURNAL
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "journal":
    today_str = datetime.now().strftime("%A %d %B %Y")
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#6c63ff,#ff6b9d);border-radius:20px;
    padding:20px;color:white;margin-bottom:20px'>
    <h2 style='margin:0'>🍽️ Journal du jour</h2>
    <p style='opacity:.85;margin:4px 0 0'>{today_str} — {p['prenom']}</p></div>
    """, unsafe_allow_html=True)

    total = sum(m["calories"] for m in st.session_state.meals)
    goal  = p["objectif"]
    rem   = goal - total

    st.markdown(f"<div class='big-num'>{total}</div><p style='text-align:center;color:#aaa'>/ {goal} kcal objectif</p>", unsafe_allow_html=True)
    st.progress(min(total / goal, 1.0))

    if total > 0:
        if rem > 0:
            st.markdown(f"<div class='badge-green'>✅ Il te reste <b>{rem} kcal</b> aujourd'hui</div>", unsafe_allow_html=True)
        elif rem > -200:
            st.markdown(f"<div class='badge-warn'>⚠️ Objectif dépassé de <b>{abs(rem)} kcal</b></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='badge-red'>🚨 Dépassement de <b>{abs(rem)} kcal</b> !</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ➕ Ajouter un repas")
    tab_photo, tab_text = st.tabs(["📷 Photo", "✍️ Texte / Vocal 🎤"])

    with tab_photo:
        uploaded = st.camera_input("📷 Prends une photo") or \
                   st.file_uploader("Ou importe une photo", type=["jpg","jpeg","png","webp"])
        if uploaded:
            with st.spinner("🤖 Analyse de ton plat en cours..."):
                try:
                    result = analyze_image(uploaded.getvalue())
                    st.session_state.pending_meal = result
                except Exception as e:
                    st.error(f"Erreur : {e}")

        if st.session_state.pending_meal:
            r = st.session_state.pending_meal
            st.success(f"{r['emoji']} **{r['name']}** — 🔥 **{r['calories']} kcal**\n\n_{r['details']}_")
            if st.button("✅ Ajouter ce repas", key="add_photo", use_container_width=True, type="primary"):
                st.session_state.meals.append(r)
                st.session_state.pending_meal = None
                st.rerun()

    with tab_text:
        st.caption("💡 Sur iPhone : appuie sur le micro 🎤 du clavier pour dicter !")
        txt = st.text_area("Qu'est-ce que tu as mangé ?",
                           placeholder="Ex: 2 barres de chocolat, une pomme, un café...",
                           key="txt_input")
        if st.button("🔍 Estimer les calories", use_container_width=True, type="primary"):
            if txt.strip():
                with st.spinner("🤖 Calcul en cours..."):
                    try:
                        result = analyze_text(txt)
                        st.session_state.pending_meal_txt = result
                    except Exception as e:
                        st.error(f"Erreur : {e}")
            else:
                st.warning("Écris ce que tu as mangé !")

        if st.session_state.pending_meal_txt:
            r = st.session_state.pending_meal_txt
            st.success(f"{r['emoji']} **{r['name']}** — 🔥 **{r['calories']} kcal**\n\n_{r['details']}_")
            if st.button("✅ Ajouter ce repas", key="add_txt", use_container_width=True, type="primary"):
                st.session_state.meals.append(r)
                st.session_state.pending_meal_txt = None
                st.rerun()

    st.markdown("---")
    st.markdown("### 🗒️ Repas du jour")
    if not st.session_state.meals:
        st.caption("Aucun repas ajouté")
    else:
        for i, m in enumerate(st.session_state.meals):
            c1, c2, c3 = st.columns([1, 5, 1])
            c1.write(m.get("emoji","🍽️"))
            c2.write(f"**{m['name']}** — 🔥 {m['calories']} kcal")
            if c3.button("🗑️", key=f"del_{i}"):
                st.session_state.meals.pop(i)
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# EAU
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "eau":
    st.markdown("""<div style='background:linear-gradient(135deg,#43c6f5,#0077b6);
    border-radius:20px;padding:20px;color:white;margin-bottom:20px'>
    <h2 style='margin:0'>💧 Hydratation</h2></div>""", unsafe_allow_html=True)

    goal_w  = p["waterGoal"]
    count_w = st.session_state.water

    st.markdown(f"<div class='big-num'>{count_w}</div><p style='text-align:center;color:#aaa'>/ {goal_w} verres (250ml)</p>", unsafe_allow_html=True)
    st.progress(min(count_w / goal_w, 1.0))

    glasses = "".join(["🥤" if i < count_w else "🫙" for i in range(goal_w)])
    st.markdown(f"<p style='font-size:26px;text-align:center;letter-spacing:3px'>{glasses}</p>", unsafe_allow_html=True)

    if count_w >= goal_w:
        st.success("🎉 Objectif atteint ! Bravo !")
    else:
        st.warning(f"💧 Encore **{goal_w - count_w} verre(s)** à boire")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ 1 verre", use_container_width=True, type="primary"):
            if st.session_state.water < goal_w:
                st.session_state.water += 1
                st.rerun()
    with c2:
        if st.button("➖ 1 verre", use_container_width=True):
            if st.session_state.water > 0:
                st.session_state.water -= 1
                st.rerun()

    st.info("⏰ **Rappel :** Pense à boire un verre toutes les heures !")

# ══════════════════════════════════════════════════════════════════════════════
# HISTORIQUE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "historique":
    st.markdown("""<div style='background:linear-gradient(135deg,#6c63ff,#ff6b9d);
    border-radius:20px;padding:20px;color:white;margin-bottom:20px'>
    <h2 style='margin:0'>📊 Historique</h2>
    <p style='opacity:.85;margin:4px 0 0'>Tes 7 derniers jours</p></div>""", unsafe_allow_html=True)

    goal      = p["objectif"]
    today_key = str(date.today())
    today_tot = sum(m["calories"] for m in st.session_state.meals)

    labels, cals = [], []
    for i in range(6, -1, -1):
        d   = date.today() - timedelta(days=i)
        key = str(d)
        cal = today_tot if key == today_key else st.session_state.history.get(key, {}).get("calories", 0)
        labels.append(d.strftime("%a %d"))
        cals.append(cal)

    try:
        import altair as alt, pandas as pd
        df = pd.DataFrame({
            "Jour": labels,
            "Calories": cals,
            "Couleur": ["#ee0979" if c > goal else "#6c63ff" for c in cals]
        })
        bar = alt.Chart(df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X("Jour:N", sort=None),
            y=alt.Y("Calories:Q"),
            color=alt.Color("Couleur:N", scale=None),
            tooltip=["Jour","Calories"]
        ).properties(height=220)
        rule = alt.Chart(pd.DataFrame({"y":[goal]})).mark_rule(
            color="#ff6b9d", strokeDash=[5,5], strokeWidth=2
        ).encode(y="y:Q")
        st.altair_chart(bar + rule, use_container_width=True)
    except:
        st.bar_chart(dict(zip(labels, cals)))

    st.markdown("---")
    for label, cal in zip(reversed(labels), reversed(cals)):
        icon  = "✅" if 0 < cal <= goal else ("⚠️" if cal > goal else "—")
        color = "#1a8a4a" if 0 < cal <= goal else ("#c0392b" if cal > goal else "#bbb")
        txt   = f"{cal} kcal" if cal > 0 else "Pas de données"
        st.markdown(f"<div class='meal-row'><span style='color:#888'>{label}</span><span style='color:{color};font-weight:700'>{icon} {txt}</span></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PROFIL
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "profil":
    st.markdown(f"""<div style='background:linear-gradient(135deg,#6c63ff,#ff6b9d);
    border-radius:20px;padding:20px;color:white;margin-bottom:20px'>
    <h2 style='margin:0'>👤 {p['prenom']}</h2></div>""", unsafe_allow_html=True)

    for label, val in [
        ("Sexe", "👨 Homme" if p['sex']=='h' else "👩 Femme"),
        ("Âge", f"{p['age']} ans"),
        ("Poids", f"{p['poids']} kg"),
        ("Taille", f"{p['taille']} cm"),
        ("BMR", f"{p['bmr']} kcal"),
        ("TDEE", f"{p['tdee']} kcal"),
        ("Objectif eau", f"💧 {p['waterGoal']} verres"),
    ]:
        c1, c2 = st.columns(2)
        c1.caption(label); c2.markdown(f"**{val}**")

    st.markdown("---")
    st.markdown(f"<div class='big-num'>{p['objectif']}</div><p style='text-align:center;color:#aaa'>kcal / jour (déficit -500 kcal)</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("✏️ Modifier mon profil", use_container_width=True):
        st.session_state.profile = None
        st.rerun()
