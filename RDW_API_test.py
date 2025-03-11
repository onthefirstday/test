import pandas as pd
from sodapy import Socrata
import streamlit as st


DOMAIN = "opendata.rdw.nl"
DATASET_ID_basis = "m9d7-ebf2"
DATASET_ID_fuel = "8ys7-d773"

# Initialize Socrata client (public datasets don't require authentication)
client = Socrata(DOMAIN, None)

# Define specific columns to fetch
options = st.multiselect(
    "Which columns do you want to load?",
    ['kenteken', 'brandstof_omschrijving', 'co2_uitstoot_gecombineerd']
)

st.write(options)

# Fetch data with selected columns
results = client.get(DATASET_ID_fuel, select=options, limit=10000)

df_fuel = pd.DataFrame.from_records(results)

st.write(df_fuel)
