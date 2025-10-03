import streamlit as st
import json
import time

st.title("OperatorGPT Lite - Vue Web intégrée")

# Historique des plans
if "history" not in st.session_state:
    st.session_state.history = []

instruction = st.text_area(
    "Entrez les actions à exécuter en JSON",
    value='''[
    {"action": "goto", "url": "https://example.com"}
]'''
)

def execute_plan(plan):
    for step in plan:
        action = step.get("action")
        if action == "goto":
            url = step.get("url")
            st.markdown(f"### Aller sur : {url}")
            # Affiche la page via un iframe
            st.components.v1.iframe(url, height=600)
            time.sleep(2)
        elif action == "click":
            selector = step.get("selector")
            st.info(f"Clic simulé sur : {selector} (non interactif dans iframe)")
        elif action == "type":
            selector = step.get("selector")
            text = step.get("text")
            st.info(f"Taper '{text}' dans {selector} (simulation)")

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


