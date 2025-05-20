import streamlit as st
import pandas as pd
from google.cloud import translate_v2 as translate
import tempfile
import os

# Set up page
st.set_page_config(page_title="Translate to English", layout="centered")
st.title("🌍 Translate Text to English")

# Load API key from Streamlit secrets
api_key = st.secrets["google"]["api_key"]
translate_client = translate.Client(api_key=api_key)

# File upload
uploaded_file = st.file_uploader("Upload a single-column CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    if df.shape[1] != 1:
        st.warning("Please upload a file with only one column (text to translate).")
        st.stop()

    text_column = df.columns[0]
    st.success(f"Detected column: {text_column}")

    with st.spinner("Translating... this may take a moment ⏳"):
        detected_languages = []
        translated_texts = []

        for text in df[text_column].astype(str):
            try:
                result = translate_client.translate(text, target_language='en')
                detected_languages.append(result["detectedSourceLanguage"])
                translated_texts.append(result["translatedText"])
            except Exception as e:
                detected_languages.append("error")
                translated_texts.append(f"Error: {str(e)}")

        df["Detected Language"] = detected_languages
        df["Translated to English"] = translated_texts

    st.success("✅ Translation complete!")
    st.dataframe(df)

    # Download link
    def convert_df(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df(df)
    st.download_button(
        label="📥 Download Translated CSV",
        data=csv,
        file_name="translated_text.csv",
        mime="text/csv",
    )
