from dotenv import load_dotenv
import os
import streamlit as st

def get_api_key(key_name):
    """
    API kulcsok lekérése prioritási sorrendben:
    1. .env fájlból (ha létezik)
    2. Streamlit secrets-ből (fallback)
    """
    # Próbáljuk betölteni a .env fájlt
    load_dotenv()
    
    # Először próbáljuk az environment változóból
    env_value = os.getenv(key_name)
    if env_value:
        return env_value
    
    # Ha nincs .env-ben, próbáljuk a Streamlit secrets-ből
    try:
        return st.secrets[key_name]
    except (KeyError, AttributeError):
        return None

# API kulcsok beállítása
GOOGLE_API_KEY = get_api_key("GOOGLE_API_KEY")
OPENAI_API_KEY = get_api_key("OPENAI_API_KEY")

# Opcionálisan beállítjuk a secrets-be is backward compatibility-ért
if GOOGLE_API_KEY:
    try:
        st.secrets["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    except:
        pass

if OPENAI_API_KEY:
    try:
        st.secrets["OPENAI_API_KEY"] = OPENAI_API_KEY
    except:
        pass
