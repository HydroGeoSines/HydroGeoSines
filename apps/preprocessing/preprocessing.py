import numpy
import pandas
import matplotlib
import pygtide
import streamlit

st.subheader("Groundwater pressure dataset")
gw = st.file_uploader("Upload dataset", type=["csv"], key='gw')

st.subheader("Barometric pressure dataset")
bp = st.file_uploader("Upload dataset", type=["csv"], key='bp')

if (gw is not None)&(bp is not None):
    st.subheader("Download standardised gap-filled versions of input datasets")
    st.download_button("Download new GW dataset as CSV",  gw.to_csv().encode('utf-8'), "gw_standardised.csv")
    st.download_button("Download new BP dataset as CSV",  bp.to_csv().encode('utf-8'), "bp_standardised.csv")
