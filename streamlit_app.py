import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image
import io
import time
import json

st.title("OperatorGPT Lite - Automatisation Web avec Selenium")

# Historique des plans
if "history" not in st.session_state:
    st.session_state.history = []

instruction = st.text_area(
    "Entrez les actions à exécuter en JSON",
    value='''[
    {"action": "goto", "url": "https://www.wikipedia.com"},
    {"action": "search", "query": "Elon Musk"}
]'''
)

def screenshot(driver):
    """Prend une capture d'écran et renvoie une image PIL"""
    png = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(png))
    return img

def execute_plan(plan):
    """Exécute le plan en utilisant Selenium et montre les captures"""
    # Config Chrome headless
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # headless mais possibilité de voir les captures
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    for step in plan:
        action = step.get("action")
        
        if action == "goto":
            url = step.get("url")
            driver.get(url)
            st.info(f"Aller sur : {url}")
            time.sleep(2)
            st.image(screenshot(driver))
            
        elif action == "search":
            query = step.get("query")
            try:
                # Cherche la barre de recherche
                search_box = driver.find_element(By.NAME, "search")  # Pour Wikipedia
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                st.info(f"Recherche sur le site : {query}")
                time.sleep(3)
                st.image(screenshot(driver))
            except Exception as e:
                st.error(f"Recherche impossible : {e}")
        
        else:
            st.warning(f"Action non supportée : {action}")

    driver.quit()
    st.success("Plan exécuté")

if st.button("Exécuter le plan"):
    try:
        plan = json.loads(instruction)
        st.session_state.history.append(plan)
        execute_plan(plan)
    except Exception as e:
        st.error(f"JSON invalide : {e}")

# Historique
st.subheader("Historique des plans exécutés")
for i, plan in enumerate(st.session_state.history):
    st.write(f"Plan {i+1} : {plan}")

