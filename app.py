import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="LinkedIn Interactions Parser", layout="centered")

st.title("📊 LinkedIn Interactions Parser")

# ---- Inputs ----
post_url = st.text_input("🔗 URL du post LinkedIn")

reactions_raw = st.text_area(
    "👍 Copier-coller ici les réactions LinkedIn (texte brut)",
    height=250,
    placeholder="Exemple :\nlove\nSophie Courtin-bernardoVoir le profil de Sophie Courtin-bernardo\n..."
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
    Règle : capturer tout ce qui suit 'Voir le profil de ' jusqu'à la fin de la ligne.
    """
    names = []
    for line in text.splitlines():
        if "Voir le profil de" in line:
            name = line.split("Voir le profil de", 1)[1].strip()
            if name:
                names.append(name)
    return ", ".join(names) + (", " if names else "")

# ---- Traitement ----
if st.button("🚀 Générer le tableau"):
    reactions_parsed = parse_reactions(reactions_raw)

    # pour commentaires & reposts : simple nettoyage (remplacer retours ligne par ", ")
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

    st.subheader("✅ Résultat")
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

