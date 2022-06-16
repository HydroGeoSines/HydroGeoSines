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
    st.subheader("Download baro-corrected groundwater pressure dataset")
    st.download_button("Download as CSV",  gw.to_csv().encode('utf-8'), "gw_corrected.csv")
