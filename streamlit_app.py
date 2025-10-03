import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import json

st.title("OperatorGPT Lite - Contrôle navigateur (headless)")

if "history" not in st.session_state:
    st.session_state.history = []

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
    output_area = st.empty()  # Zone qui sera mise à jour en temps réel

    try:
        for step in plan:
            action = step.get("action")
            
            if action == "goto":
                url = step.get("url")
                current_url = url
                resp = session.get(url)
                soup = BeautifulSoup(resp.text, "html.parser")
                output_area.markdown(f"### Aller sur : {url}")
                output_area.code(soup.prettify()[:1000])  # affiche les 1000 premiers caractères
                time.sleep(2)
                
            elif action == "click":
                selector = step.get("selector")
                soup = BeautifulSoup(session.get(current_url).text, "html.parser")
                element = soup.select_one(selector)
                if element and element.has_attr("href"):
                    current_url = element["href"]
                    resp = session.get(current_url)
                    soup = BeautifulSoup(resp.text, "html.parser")
                    output_area.markdown(f"### Clic simulé sur : {selector} → {current_url}")
                    output_area.code(soup.prettify()[:1000])
                else:
                    output_area.warning(f"Aucun lien trouvé pour {selector}")
                time.sleep(2)
                
            elif action == "type":
                selector = step.get("selector")
                text = step.get("text")
                output_area.markdown(f"### Taper '{text}' dans {selector} (simulation)")
                time.sleep(2)
        
        output_area.success("Plan exécuté (headless)")
        
    except Exception as e:
        output_area.error(f"Erreur : {e}")

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

