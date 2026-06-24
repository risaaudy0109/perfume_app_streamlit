import streamlit as st

st.set_page_config(
    page_title="Prediksi Potensi Pendapatan Parfum",
    page_icon="",
    layout="wide"
)

# css/style

st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#FFF8FC,#F5F0FF);
}

.hero{
    background:white;
    padding:35px;
    border-radius:20px;
    text-align:center;
    box-shadow:0px 4px 15px rgba(0,0,0,0.08);
}

.title{
    font-size:50px;
    font-weight:800;
    color:#6A4C93;
}

.card{
    background:white;
    padding:25px;
    border-radius:20px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
    text-align:center;
    min-height:260px;
}

.metric{
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
    text-align:center;
}

.metric-number{
    font-size:35px;
    font-weight:bold;
    color:#6A4C93;
}

.footer{
    text-align:center;
    color:gray;
}
</style>
""", unsafe_allow_html=True)

# HERO

st.markdown("""
<div class="hero">
    <div class="title"> Prediksi Potensi Pendapatan Parfum</div>
</div>
""", unsafe_allow_html=True)

st.write("")



# about
st.subheader("Tentang Aplikasi")

st.info("""
Aplikasi ini digunakan untuk memprediksi **Potensi Pendapatan (Revenue Potential)** produk parfum berdasarkan karakteristik produk dan performa penjualannya.

Prediksi dilakukan menggunakan dua model Machine Learning:

- Ridge Regression
- Artificial Neural Network (ANN)

Variabel yang digunakan meliputi:

- Brand
- Gender
- Product Type
- Available Stock
- Price Category
- Market Segment
- Sales Performance
- Brand Popularity
- Country
- Inventory Status
- Stock Turnover
""")

# fitur

st.subheader(" Fitur Utama")

col1, col2 = st.columns(2)

with col1:

    st.markdown("""
    <div class="card">
        <h2>Visualisasi Data</h2>

    </div>
    """, unsafe_allow_html=True)

    # Streamlit Multipage
    if st.button("Buka Halaman Visualisasi"):
        st.switch_page("pages/1_visualization.py")

with col2:

    st.markdown("""
    <div class="card">
        <h2>Prediksi Revenue</h2>
        
    </div>
    """, unsafe_allow_html=True)

    if st.button("Buka Halaman Prediksi"):
        st.switch_page("pages/2_prediction.py")

st.divider()

# petunjuk
st.subheader("Cara Menggunakan")

st.markdown("""
### 1. Buka Halaman Visualisasi
Pelajari pola dan karakteristik data parfum.

### 2. Buka Halaman Prediksi
Masukkan spesifikasi produk parfum.

### 3. Pilih Model Machine Learning
Gunakan Ridge Regression atau ANN.

### 4. Klik Prediksi
Sistem akan menampilkan estimasi Revenue Potential.

### 5. Gunakan Hasil Prediksi
Sebagai dasar pengambilan keputusan bisnis dan strategi pemasaran.
""")

st.divider()