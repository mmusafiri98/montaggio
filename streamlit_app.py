import streamlit as st
import time

st.title("Simulation Amazon - Bot")

# Liste des étapes
steps = [
    {"action": "goto", "url": "https://example.com"},
    {"action": "click", "selector": "input#search"},
    {"action": "type", "selector": "input#search", "text": "wireless headphones"},
    {"action": "click", "selector": "button#submit"}
]

# Historique des actions
if "history" not in st.session_state:
    st.session_state.history = []

if st.button("Exécuter la simulation"):
    for step in steps:
        action = step["action"]
        if action == "goto":
            st.info(f"Aller sur {step['url']}")
        elif action == "click":
            st.info(f"Clic simulé sur {step['selector']}")
        elif action == "type":
            st.info(f"Taper '{step['text']}' dans {step['selector']}")
        time.sleep(1)
    
    st.success("Simulation terminée")
    st.session_state.history.append(steps)

# Affichage de l'historique
st.subheader("Historique")
for i, plan in enumerate(st.session_state.history):
    st.write(f"Plan {i+1} : {plan}")

