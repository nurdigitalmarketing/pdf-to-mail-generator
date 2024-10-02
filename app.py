import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
from openai import OpenAI
import json

def extract_text_from_pdf(file):
    """Estrae il testo dal file PDF."""
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Errore durante l'estrazione del testo: {e}")
        return ""

def extract_keywords_from_csv(file):
    """Estrae le keyword e i relativi dati da un CSV."""
    try:
        df = pd.read_csv(file)
        return df.to_dict(orient="records")
    except Exception as e:
        st.error(f"Errore durante la lettura del file CSV: {e}")
        return []

def generate_email(client, report_text, keyword_data, client_name, contact_name, timeframe, your_name):
    """Genera il contenuto dell'email utilizzando i dati estratti e l'LLM."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"""
            Genera una email formattata per inviare i risultati SEO basandoti sui seguenti dati:

            Dati generali del report:
            {report_text}

            Keyword e performance:
            {json.dumps(keyword_data, indent=2)}

            Nome cliente: {client_name}
            Nome del referente: {contact_name}
            Periodo analizzato: {timeframe}
            Nome del mittente: {your_name}
        """}
    ]

    response = client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=messages
    )

    return response.choices[0].message.content.strip()

# UI di Streamlit
st.set_page_config(page_title="Mail from SEO report Generator", layout="centered")

st.title('Mail from SEO report Generator')
st.markdown("""
**SEO Report Generator** è uno strumento che consente di generare email personalizzate basate su dati SEO provenienti da report PDF e file CSV. 

Il sistema estrae automaticamente le informazioni più rilevanti, come acquisizione utenti, engagement, geografia del traffico e performance delle query organiche, e le compila in un'email formattata in HTML.

""")

st.markdown("""---""")

api_key = st.text_input("🔑 _Inserisci la tua API key di OpenAI_, la recuperi dalla [dashboard](https://platform.openai.com/api-keys).", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    uploaded_pdf = st.file_uploader("Carica il PDF del report", type="pdf")
    uploaded_csv = st.file_uploader("Carica il CSV delle keyword", type="csv")

    if uploaded_pdf and uploaded_csv:
        client_name = st.text_input("Nome del cliente")
        contact_name = st.text_input("Nome del referente")
        timeframe = st.text_input("Periodo analizzato")
        your_name = st.text_input("Il tuo nome")

        if st.button("Genera Mail"):
            if not all([client_name, contact_name, timeframe, your_name]):
                st.error("Per favore, compila tutti i campi richiesti.")
            else:
                with st.spinner("Generazione dell'email in corso..."):
                    report_text = extract_text_from_pdf(uploaded_pdf)
                    keyword_data = extract_keywords_from_csv(uploaded_csv)
                    email_content = generate_email(client, report_text, keyword_data, client_name, contact_name, timeframe, your_name)

                    if email_content:
                        st.markdown(email_content, unsafe_allow_html=True)
