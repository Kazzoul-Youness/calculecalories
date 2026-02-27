# Application calories à partir de photos (Streamlit)

Cette application permet de :

- Importer des photos de plats et boissons.
- Saisir (ou estimer automatiquement) les calories.
- Additionner les calories par entrée et par journée.
- Afficher un graphique des calories consommées chaque jour.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Déployer sur Streamlit Community Cloud

1. Pousse ce dépôt sur GitHub.
2. Ouvre: `https://share.streamlit.io/deploy`
3. Renseigne:
   - **Repository**: `Kazzoul-Youness/calculecalories`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. Clique sur **Deploy**.

> Dans ton screenshot, l'erreur vient du champ **Main file path** vide/invalide.
> Mets simplement `streamlit_app.py`.

## Notes

- Estimation automatique si calories non renseignées:
  - Plat: **550 kcal** / portion
  - Boisson: **120 kcal** / portion
- Les données sont gardées dans la session Streamlit en mémoire.
