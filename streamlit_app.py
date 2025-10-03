import streamlit as st
import json
import urllib.parse

st.title("OperatorGPT Lite - Vue Web YouTube")

# Historique des plans
if "history" not in st.session_state:
    st.session_state.history = []

instruction = st.text_area(
    "Entrez les actions à exécuter en JSON",
    value='''[
    {"action": "goto", "url": "https://www.youtube.com"},
    {"action": "search", "query": "Impossible James Arthur"}
]'''
)

def execute_plan(plan):
    url_to_show = None
    for step in plan:
        action = step.get("action")
        if action == "goto":
            url_to_show = step.get("url")
            st.info(f"Aller sur : {url_to_show}")
        elif action == "search":
            query = step.get("query")
            if url_to_show and "youtube.com" in url_to_show:
                # Générer URL de recherche YouTube
                query_encoded = urllib.parse.quote(query)
                url_to_show = f"https://www.youtube.com/results?search_query={query_encoded}"
                st.info(f"Recherche sur YouTube : {query}")
        else:
            st.warning(f"Action non prise en charge : {action}")

    if url_to_show:
        # Afficher le site / résultats de recherche dans un iframe
        st.components.v1.iframe(url_to_show, height=600)

if st.button("Exécuter le plan"):
    try:
        plan = json.loads(instruction)
        st.session_state.history.append(plan)
        execute_plan(plan)
    except Exception as e:
        st.error(f"JSON invalide : {e}")

st.subheader("Historique des plans exécutés")
for i, plan in enumerate(st.session_state.history):
    st.write(f"Plan {i+1} : {plan}")

