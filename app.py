import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="LinkedIn Interactions Parser", layout="centered")

st.title("📊 LinkedIn Interactions Parser")

# ---- Inputs ----
post_url = st.text_input("🔗 URL du post LinkedIn")

reactions_raw = st.text_area(
    "👍 Copier-coller ici les réactions LinkedIn (texte brut)",
    height=200,
    placeholder="Exemple :\nlike\nAnthony MiattiVoir le profil de Anthony Miatti\n..."
)

comments_raw = st.text_area(
    "💬 Copier-coller ici les commentaires (optionnel, peut rester vide)",
    height=150,
    placeholder="Exemple :\nJean Dupont\nVoir le profil de Jean Dupont\n..."
)

reposts_raw = st.text_area(
    "🔄 Copier-coller ici les reposts (optionnel, peut rester vide)",
    height=150,
    placeholder="Exemple :\nMarie Curie\nVoir le profil de Marie Curie\n..."
)

# ---- Parsing des réactions ----
def parse_reactions(text):
    """
    Extrait les noms de profils à partir du texte brut des réactions LinkedIn.
    Règle : on prend la ligne juste avant 'Voir le profil de ...'
    """
    names = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "Voir le profil de" in line and i > 0:
            name_candidate = lines[i-1].strip()
            if name_candidate and not any(x in name_candidate.lower() for x in ["like", "celebrate", "support", "insightful", "curious", "love"]):
                names.append(name_candidate)
    # Retourner dans le format attendu pour Airtable
    return ", ".join(names) + (", " if names else "")

# ---- Traitement ----
if st.button("🚀 Générer le tableau"):
    reactions_parsed = parse_reactions(reactions_raw)
    comments_parsed = comments_raw.replace("\n", ", ").strip()
    if comments_parsed:
        comments_parsed += ", "
    reposts_parsed = reposts_raw.replace("\n", ", ").strip()
    if reposts_parsed:
        reposts_parsed += ", "

    df = pd.DataFrame([{
        "Post (url)": post_url,
        "Réactions": reactions_parsed,
        "Commentaires": comments_parsed,
        "Reposts": reposts_parsed
    }])

    st.dataframe(df)

    # ---- Export en Excel ----
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Interactions")

    st.download_button(
        label="📥 Télécharger en XLSX",
        data=output.getvalue(),
        file_name="linkedin_interactions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
