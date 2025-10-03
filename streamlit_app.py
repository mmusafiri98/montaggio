import streamlit as st
import json
import urllib.parse

st.set_page_config(page_title="OperatorGPT Lite - Amazon", layout="wide")
st.title("OperatorGPT Lite - Simulation Amazon")

# Historique des plans
if "history" not in st.session_state:
    st.session_state.history = []

# Instruction JSON pour simuler des actions
instruction = st.text_area(
    "Entrez les actions à exécuter en JSON",
    value='''[
    {"action": "goto", "url": "https://www.amazon.com"},
    {"action": "search", "query": "wireless headphones"}
]'''
)

def execute_plan(plan):
    """
    Simule les actions sur le site et affiche l'URL dans un iframe si possible
    """
    url_to_show = None
    for step in plan:
        action = step.get("action")
        
        if action == "goto":
            url_to_show = step.get("url")
            st.info(f"➡️ Aller sur : {url_to_show}")
        
        elif action == "search":
            query = step.get("query")
            if url_to_show and "amazon.com" in url_to_show:
                # Générer URL de recherche Amazon
                query_encoded = urllib.parse.quote(query)
                url_to_show = f"{url_to_show}/s?k={query_encoded}"
                st.info(f"🔍 Recherche sur Amazon : {query}")
            else:
                st.warning("Impossible de faire une recherche : URL non définie ou non Amazon")
        
        else:
            st.warning(f"Action non prise en charge : {action}")

    if url_to_show:
        # Afficher le site / résultats dans un iframe
        st.subheader("Vue web simulée")
        try:
            st.components.v1.iframe(url_to_show, height=600)
        except Exception as e:
            st.warning(f"Impossible d'afficher le site dans un iframe : {e}")

# Bouton pour exécuter le plan
if st.button("Exécuter le plan"):
    try:
        plan = json.loads(instruction)
        st.session_state.history.append(plan)
        execute_plan(plan)
        st.success("✅ Plan exécuté (simulation)")
    except Exception as e:
        st.error(f"JSON invalide : {e}")

# Affichage de l'historique
st.subheader("Historique des plans exécutés")
for i, plan in enumerate(st.session_state.history):
    st.write(f"Plan {i+1} : {plan}")

