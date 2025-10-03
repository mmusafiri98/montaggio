import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import json

st.title("OperatorGPT Lite - Contrôle navigateur (headless)")

# Historique des actions
if "history" not in st.session_state:
    st.session_state.history = []

# Instruction utilisateur (JSON simplifié)
instruction = st.text_area(
    "Entrez les actions à exécuter en JSON",
    value='''[
    {"action": "goto", "url": "https://example.com"},
    {"action": "click", "selector": "a"},
    {"action": "type", "selector": "input[name='q']", "text": "Streamlit"}
]'''
)

def execute_plan(plan):
    session = requests.Session()
    current_url = None
    try:
        for step in plan:
            action = step.get("action")
            if action == "goto":
                url = step.get("url")
                current_url = url
                resp = session.get(url)
                soup = BeautifulSoup(resp.text, "html.parser")
                st.info(f"Aller sur : {url}")
                time.sleep(1)
            elif action == "click":
                selector = step.get("selector")
                soup = BeautifulSoup(session.get(current_url).text, "html.parser")
                element = soup.select_one(selector)
                if element and element.has_attr("href"):
                    current_url = element["href"]
                    session.get(current_url)
                    st.info(f"Clic simulé sur : {selector} -> {current_url}")
                else:
                    st.warning(f"Aucun lien trouvé pour {selector}")
                time.sleep(1)
            elif action == "type":
                selector = step.get("selector")
                text = step.get("text")
                st.info(f"Taper '{text}' dans {selector} (simulation)")
                time.sleep(1)
        st.success("Plan exécuté (headless)")
    except Exception as e:
        st.error(f"Erreur : {e}")

if st.button("Exécuter le plan"):
    try:
        plan = json.loads(instruction)
        st.session_state.history.append(plan)
        execute_plan(plan)
    except Exception as e:
        st.error(f"JSON invalide : {e}")

# Affichage de l'historique
st.subheader("Historique des plans exécutés")
for i, plan in enumerate(st.session_state.history):
    st.write(f"Plan {i+1} : {plan}")
