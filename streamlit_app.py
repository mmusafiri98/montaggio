import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess
import os
import time
import json

st.title("OperatorGPT Lite - Contrôle navigateur")

# Historique des actions
if "history" not in st.session_state:
    st.session_state.history = []

# Instruction utilisateur (JSON simplifié)
instruction = st.text_area(
    "Entrez les actions à exécuter en JSON",
    value='''[
    {"action": "goto", "url": "https://example.com"},
    {"action": "click", "selector": "text=More information"},
    {"action": "type", "selector": "input[name='q']", "text": "Streamlit"}
]'''
)

# Fonction pour installer Chromium si nécessaire
def ensure_chromium():
    chromium_path = os.path.expanduser("~/.cache/ms-playwright/chromium-1129/chrome-linux/chrome")
    if not os.path.exists(chromium_path):
        st.info("Téléchargement de Chromium pour Playwright...")
        subprocess.run(["playwright", "install", "chromium"], check=True)

# Fonction pour exécuter le plan
def execute_plan(plan):
    try:
        ensure_chromium()  # Installer Chromium si absent
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # headless=True pour le cloud
            page = browser.new_page()
            for step in plan:
                action = step.get("action")
                if action == "goto":
                    url = step.get("url")
                    page.goto(url)
                    st.info(f"Aller sur : {url}")
                    time.sleep(2)
                elif action == "click":
                    selector = step.get("selector")
                    page.click(selector)
                    st.info(f"Clic sur : {selector}")
                    time.sleep(1)
                elif action == "type":
                    selector = step.get("selector")
                    text = step.get("text")
                    page.fill(selector, text)
                    st.info(f"Taper '{text}' dans {selector}")
                    time.sleep(1)
            st.success("Plan exécuté")
            browser.close()
    except Exception as e:
        st.error(f"Erreur : {e}")

# Bouton pour exécuter le plan
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

