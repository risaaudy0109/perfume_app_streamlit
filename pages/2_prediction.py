import streamlit as st
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf

# ======= Konfigurasi Halaman =======
st.set_page_config(
    page_title="Prediksi Revenue Potential Parfum",
    page_icon="",
    layout="wide"
)

st.title("Prediksi Revenue Potential Parfum")
st.write("Masukkan data produk parfum untuk mendapatkan estimasi Revenue Potential.")

# ======= Pilih Model =======
st.subheader("Pilih Model Prediksi")
model_choice = st.radio(
    "Model yang digunakan:",
    options=["Ridge Regression"],
    horizontal=True
)

# Load Model & Preprocessor
@st.cache_resource
def load_ridge():
    model      = joblib.load("models/best_model_ridge.joblib")
    prep       = joblib.load("models/preprocessor.joblib")
    return model, prep

# langsung pakai Ridge
model, prep = load_ridge()


# ======= Fungsi Preprocessing =======
def preprocess_input(raw: dict, prep: dict) -> np.ndarray:
    scaler   = prep["scaler"]
    ohe      = prep["ohe"]
    ordinal  = prep["ordinal"]
    te_maps  = prep["te_maps"]
    feat_cols = prep["feature_cols"]

    brand   = raw["Brand"]
    country = raw["Country"]
    avail   = raw["Available"]

    # ── Target Encoding: Brand & Country ──
    te_brand_map  = te_maps["Brand"]
    te_country_map = te_maps["Country"]
    te_brand   = te_brand_map["map"].get(brand,   te_brand_map["global_mean"])
    te_country = te_country_map["map"].get(country, te_country_map["global_mean"])

    # ── Numeric (Available) ──
    # Kedua model (Ridge & ANN) menggunakan preprocessing yang sama:
    # log1p(Available) → RobustScaler
    avail_scaled = scaler.transform([[np.log1p(avail)]])[0][0]

    # ── Ordinal Encoding ──
    ordinal_cols = [
        "Price_Category", "Market_Segment", "Sales_Performance",
        "Brand_Popularity", "Inventory_Status", "Stock_Turnover"
    ]
    ord_input = pd.DataFrame([[
        raw["Price_Category"], raw["Market_Segment"], raw["Sales_Performance"],
        raw["Brand_Popularity"], raw["Inventory_Status"], raw["Stock_Turnover"]
    ]], columns=ordinal_cols)
    ord_values = ordinal.transform(ord_input)[0]

    # ── One-Hot Encoding ──
    ohe_input = pd.DataFrame([[raw["Gender"], raw["Product_Type"]]],
                              columns=["Gender", "Product_Type"])
    ohe_values = ohe.transform(ohe_input)[0]
    ohe_cols   = ohe.get_feature_names_out(["Gender", "Product_Type"])

    # ── Gabung sesuai urutan feature_cols ──
    row = {}
    row["Available"]   = avail_scaled
    for col, val in zip(ordinal_cols, ord_values):
        row[col] = val
    row["TE_Brand"]   = te_brand
    row["TE_Country"] = te_country
    for col, val in zip(ohe_cols, ohe_values):
        row[col] = val

    X = pd.DataFrame([row])[feat_cols].fillna(0)
    return X.values

# Form Input
st.divider()
st.subheader("📝 Isi Data Produk Parfum")

col1, col2 = st.columns(2)

with col1:
    brand = st.selectbox("Brand:", options=[
        "Chanel", "Dior", "Gucci", "Versace", "Prada", "Tom Ford",
        "Yves Saint Laurent", "Dolce & Gabbana", "Givenchy", "Armani", "Unknown"
    ], key="brand")

    gender = st.selectbox("Gender:", options=["Men", "Women"], key="gender")

    product_type = st.selectbox("Product Type:", options=["EDP", "EDT", "Cologne", "Unknown"], key="product_type")

    available = st.number_input("Available (stok unit):", min_value=0, max_value=10000, value=100, key="available")

    price_category = st.selectbox("Price Category:", options=["Budget", "Mid-Range", "Luxury"], key="price_category")

    inventory_status = st.selectbox("Inventory Status:", options=["Low Stock", "Medium Stock", "High Stock"], key="inventory_status")

with col2:
    country = st.selectbox("Country:", options=[
        "France", "Italy", "USA", "UK", "Germany", "Spain", "Japan", "Unknown"
    ], key="country")

    market_segment = st.selectbox("Market Segment:", options=["Mass Market", "Premium", "Luxury"], key="market_segment")

    sales_performance = st.selectbox("Sales Performance:", options=["Low Seller", "Medium Seller", "High Seller"], key="sales_performance")

    brand_popularity = st.selectbox("Brand Popularity:", options=["Low", "Medium", "High"], key="brand_popularity")

    stock_turnover = st.selectbox("Stock Turnover:", options=["Slow", "Moderate", "Fast"], key="stock_turnover")

# Tombol Prediksi
st.divider()
if st.button("🔮 Prediksi Revenue Potential", use_container_width=True):
    raw_input = {
        "Brand"            : st.session_state.brand,
        "Country"          : st.session_state.country,
        "Gender"           : st.session_state.gender,
        "Product_Type"     : st.session_state.product_type,
        "Available"        : st.session_state.available,
        "Price_Category"   : st.session_state.price_category,
        "Market_Segment"   : st.session_state.market_segment,
        "Sales_Performance": st.session_state.sales_performance,
        "Brand_Popularity" : st.session_state.brand_popularity,
        "Inventory_Status" : st.session_state.inventory_status,
        "Stock_Turnover"   : st.session_state.stock_turnover,
    }

    mtype = "ann" if model_choice == "Artificial Neural Network (ANN)" else "ridge"

    try:
        X_input = preprocess_input(raw_input, prep)

        if mtype == "ann":
            pred_log = model.predict(X_input, verbose=0).flatten()[0]
        else:
            pred_log = model.predict(X_input)[0]

        # Kembalikan ke skala asli (kebalikan log1p)
        prediction = np.expm1(pred_log)

        st.success(f"Estimasi Revenue Potential: **Rp {prediction:,.2f}**")
        st.info(
            f"ℹHasil prediksi menggunakan model **{model_choice}**. "
            "Angka ini adalah estimasi berdasarkan model Machine Learning, bukan nilai pasti."
        )

    except Exception as e:
        st.error(f"Terjadi kesalahan saat prediksi: {e}")

