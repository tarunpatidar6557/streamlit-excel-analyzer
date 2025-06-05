import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
import io
import tempfile
import toml
import os
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="CSV EDA Tool", layout="wide")
st.title("📊 CSV Explorer with ydata-profiling")


# theme = st.sidebar.selectbox("Choose Theme", ["Light", "Dark"])

#Side bar navigation
st.sidebar.title("🧭 Navigation")
section = st.sidebar.radio("Go to", [
    "1️⃣ Upload",
    "2️⃣ Preprocess",
    "3️⃣ Profile",
    "4️⃣ Download",
    "5️⃣ Visualize"
])

#Upload Section
if section == "1️⃣ Upload":
    st.subheader("📁 Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], key = "uploader")
    if uploaded_file is not None:
        st.session_state['df'] = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded and data saved in memory.")

if section == "2️⃣ Preprocess":
    if 'df' not in st.session_state:
        st.warning("⚠️ Please upload a file first.")
    else:
        df = st.session_state['df']
        st.subheader("📌 Data Preview")
        st.dataframe(df.head())

        st.subheader("🧮 Select Columns for Profiling")
        selected_columns = st.multiselect("Choose columns", df.columns.tolist(), default=df.columns.tolist())

        drop_na = st.checkbox("🧹 Drop rows with missing values", value=False)

        if selected_columns:
            filtered_df = df[selected_columns]
            if drop_na:
                filtered_df = filtered_df.dropna()
                st.info(f"Remaining rows after dropping NAs: {filtered_df.shape[0]}")

            # Save cleaned version to session
            st.session_state['filtered_df'] = filtered_df
        else:
            st.warning("Please select at least one column to generate the report.")

# Profile
if section == "3️⃣ Profile":
    if 'filtered_df' not in st.session_state:
        st.warning("⚠️ Please preprocess your data first.")
    else:
        st.subheader("🧠 Profiling Report")
        profile = ProfileReport(st.session_state['filtered_df'], explorative=True)
        st_profile_report(profile)

        # Save report to session
        st.session_state['profile'] = profile

# Download
if section == "4️⃣ Download":
    if 'profile' not in st.session_state:
        st.warning("⚠️ Generate the profiling report first.")
    else:
        st.subheader("⬇️ Download Profiling Report")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            st.session_state['profile'].to_file(tmp_file.name)
            tmp_file.seek(0)
            html_bytes = tmp_file.read()

        st.download_button(
            label="📄 Download HTML Report",
            data=html_bytes,
            file_name="profile_report.html",
            mime="text/html"
        )

if section == "5️⃣ Visualize":
    st.subheader("📊 Custom Visualizations")

    if 'filtered_df' not in st.session_state:
        st.warning("⚠️ Please preprocess your data first.")
    else:
        df = st.session_state['filtered_df']
        chart_type = st.selectbox("Choose Chart Type", ["Correlation Heatmap", "Pairplot", "Histogram", "Bar Chart"])

        if chart_type == "Correlation Heatmap":
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr()
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
                st.pyplot(fig)
            else:
                st.warning("Need at least 2 numeric columns for heatmap.")

        elif chart_type == "Pairplot":
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if len(numeric_cols) >= 2:
                st.info("Rendering pairplot... this may take a few seconds.")
                fig = sns.pairplot(df[numeric_cols])
                st.pyplot(fig)
            else:
                st.warning("Need at least 2 numeric columns.")

        elif chart_type == "Histogram":
            col = st.selectbox("Choose column", df.columns.tolist())
            fig = px.histogram(df, x=col)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Bar Chart":
            col = st.selectbox("Choose column", df.columns.tolist())
            if df[col].dtype == 'object':
                top_vals = df[col].value_counts().nlargest(20).reset_index()
                fig = px.bar(top_vals, x='index', y=col, labels={'index': col, col: 'Count'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Bar chart works best with categorical data.")


theme_choice = st.sidebar.selectbox("🎨 Choose Theme", ["Light", "Dark"])

config_path = os.path.join(".streamlit", "config.toml")

if st.sidebar.button("Apply Theme"):
    new_base = "light" if theme_choice == "Light" else "dark"

    config_data = {
        "theme": {
            "base": new_base,
            "primaryColor": "#00FFAA",
            "backgroundColor": "#0E1117" if new_base == "dark" else "#FFFFFF",
            "secondaryBackgroundColor": "#262730" if new_base == "dark" else "#F0F2F6",
            "textColor": "#FAFAFA" if new_base == "dark" else "#000000",
            "font": "sans serif"
        }
    }

    os.makedirs(".streamlit", exist_ok=True)
    with open(config_path, "w") as f:
        toml.dump(config_data, f)

    st.success("✅ Theme updated in config. Please reload the app to apply it.")