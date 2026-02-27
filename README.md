# Application calories à partir de photos (Streamlit + Web)

Tu avais raison : dans la version précédente, si tu ne renseignais pas la case calories, la valeur tombait souvent sur le défaut (550 pour plat), donc plusieurs plats donnaient le même résultat.

Cette version corrige ça avec une estimation **plus intelligente** basée sur des mots-clés du nom saisi (ex: salade, burger, jus, etc.), en plus de l'option manuelle.

## Lancer en local (Streamlit)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Déployer sur Streamlit Community Cloud

1. Pousse le dépôt sur GitHub.
2. Ouvre: `https://share.streamlit.io/deploy`
3. Remplis:
   - **Repository**: `Kazzoul-Youness/calculecalories`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. Clique sur **Deploy**.

## Comment éviter le 550 kcal identique

- Si tu connais les calories, saisis-les manuellement (le plus fiable).
- Sinon, mets un nom explicite, par exemple:
  - `salade concombre` (plus léger)
  - `burger frites` (plus riche)
  - `jus orange` / `soda`
- L'app affiche maintenant le **mode** utilisé (`manuel`, `auto (mot-clé)`, ou `auto (défaut)`).

## Limite importante

Sans service IA externe de vision, l'app ne "comprend" pas vraiment le contenu de la photo: l'estimation automatique reste approximative.
