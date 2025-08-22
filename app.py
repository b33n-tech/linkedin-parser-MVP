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
    return names

def format_comma_separated(names):
    """Retourne le format Airtable : PROFIL, PROFIL, PROFIL, """
    return ", ".join(names) + (", " if names else "")

# ---- Traitement ----
if st.button("🚀 Générer le tableau"):
    # Parsing
    reactions_list = parse_reactions(reactions_raw)
    reactions_parsed = format_comma_separated(reactions_list)

    comments_list = [c.strip() for c in comments_raw.splitlines() if c.strip()]
    comments_parsed = format_comma_separated(comments_list)

    reposts_list = [r.strip() for r in reposts_raw.splitlines() if r.strip()]
    reposts_parsed = format_comma_separated(reposts_list)

    # ---- Résumé global ----
    df = pd.DataFrame([{
        "Post (url)": post_url,
        "Réactions (Airtable)": reactions_parsed,
        "Commentaires (Airtable)": comments_parsed,
        "Reposts (Airtable)": reposts_parsed
    }])

    st.subheader("✅ Résultat (format Airtable)")
    st.dataframe(df)

    # ---- Compteurs ----
    st.markdown(f"""
    **📊 Statistiques :**  
    - {len(reactions_list)} réactions  
    - {len(comments_list)} commentaires  
    - {len(reposts_list)} reposts
    """)

    # ---- Vue listes (1 profil = 1 ligne) ----
    st.subheader("📋 Résultat sous forme de liste")

    max_len = max(len(reactions_list), len(comments_list), len(reposts_list))

    reactions_col = reactions_list + [""] * (max_len - len(reactions_list))
    comments_col = comments_list + [""] * (max_len - len(comments_list))
    reposts_col = reposts_list + [""] * (max_len - len(reposts_list))

    tab_list = pd.DataFrame({
        "Réactions": reactions_col,
        "Commentaires": comments_col,
        "Reposts": reposts_col
    })

    st.dataframe(tab_list)

    # ---- Export Excel ----
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Résumé")
        tab_list.to_excel(writer, index=False, sheet_name="Détail")

    st.download_button(
        label="📥 Télécharger en XLSX",
        data=output.getvalue(),
        file_name="linkedin_interactions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
