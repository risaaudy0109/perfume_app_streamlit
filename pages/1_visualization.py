import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ======= Konfigurasi Halaman =======
st.set_page_config(
    page_title="Visualisasi Data Parfum",
    page_icon="",
    layout="wide"
)

# Tema dasar Seaborn agar grafik terlihat bersih & modern
sns.set_theme(style="whitegrid")

st.title("Visualisasi Data Parfum Interaktif")

# Load Data & Pembersihan 
@st.cache_data
def load_data():
    # Menggunakan file yang direferensikan sesuai instruksi
    data = pd.read_csv("data/Perfume_Market_Intelligence_Dataset.csv")
    
    # Relevansi data: Bersihkan kolom Product_Type agar tidak ada duplikasi/Unknown
    if "Product_Type" in data.columns:
        data["Product_Type"] = data["Product_Type"].replace({"Eau De Toilette": "EDT"})
        data["Product_Type"] = data["Product_Type"].replace({"Parfum": "EDP"})
        data = data[data["Product_Type"] != "Unknown"]
        
    return data

df = load_data()

# Sidebar Filter Interaktif
st.sidebar.header("🔍 Filter & Kustomisasi")

price_filter = st.sidebar.selectbox(
    "Kategori Harga",
    ["Semua"] + sorted(df["Price_Category"].dropna().unique().tolist())
)

segment_filter = st.sidebar.selectbox(
    "Market Segment",
    ["Semua"] + sorted(df["Market_Segment"].dropna().unique().tolist())
)

# INTERAKTIF: Tambahkan pencarian teks untuk brand atau produk
search_query = st.sidebar.text_input("🔍 Cari Brand / Nama Produk", "")

# INTERAKTIF: Pilihan palet warna
color_palette = st.sidebar.selectbox(
    "🎨 Palet Warna Grafik",
    ["viridis", "magma", "mako", "rocket", "crest", "Blues_r"]
)

# filter=
filtered_df = df.copy()

if price_filter != "Semua":
    filtered_df = filtered_df[filtered_df["Price_Category"] == price_filter]

if segment_filter != "Semua":
    filtered_df = filtered_df[filtered_df["Market_Segment"] == segment_filter]

if search_query:
    filtered_df = filtered_df[
        filtered_df["Brand"].str.contains(search_query, case=False, na=False) |
        filtered_df["Product"].str.contains(search_query, case=False, na=False)
    ]

# KPI METRICS
# Fungsi format angka besar agar layout metric tetap rapi
def format_revenue(num):
    if num >= 1e6: return f"${num / 1e6:.2f}M"
    if num >= 1e3: return f"${num / 1e3:.1f}K"
    return f"${num:.2f}"

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("💰 Total Revenue Potential", format_revenue(filtered_df["Revenue_Potential"].sum()))
k2.metric("📦 Total Terjual", f"{filtered_df['Sold'].sum():,.0f}")
k3.metric("🏷️ Rata-rata Harga", f"${filtered_df['Price'].mean():,.2f}")
k4.metric("🔥 Rata-rata Demand Score", f"{filtered_df['Demand_Score'].mean():,.1f}")
k5.metric("🏢 Jumlah Brand", f"{filtered_df['Brand'].nunique():,}")

st.markdown("---")

# DASHBOARD
st.subheader("📊 Dashboard Bisnis")

col7, col8 = st.columns(2)

# Visualisasi 1: Donut Chart Proporsi Gender
with col7:
    st.write("### Proporsi Produk berdasarkan Gender")
    gender_count = filtered_df["Gender"].value_counts()

    if not gender_count.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        colors = sns.color_palette("pastel")[0:len(gender_count)]
        
        ax.pie(
            gender_count,
            labels=gender_count.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            wedgeprops={"width": 0.4, "edgecolor": "white"}
        )
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Data tidak tersedia untuk kombinasi filter ini.")

# Visualisasi 2: Peningkatan bagian Jenis Produk
with col8:
    st.write("### Total Produk Terjual per Jenis Produk (Bersih)")
    
    sold_by_type = (
        filtered_df.groupby("Product_Type")["Sold"]
        .sum()
        .reset_index()
        .sort_values(by="Sold", ascending=False)
    )

    if not sold_by_type.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        
        sns.barplot(
            data=sold_by_type, 
            x="Product_Type", 
            y="Sold", 
            hue="Product_Type",
            palette=color_palette, 
            ax=ax,
            legend=False
        )
        
        # Menambahkan nilai label di atas bar secara otomatis
        for p in ax.patches:
            ax.annotate(f'{p.get_height():,.0f}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontsize=9)

        ax.set_xlabel("Jenis Produk (Konsisten)")
        ax.set_ylabel("Jumlah Terjual")
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Data tidak tersedia untuk kombinasi filter ini.")

col9, col10 = st.columns(2)

# Visualisasi 3: Rata-rata Harga per Kategori Harga
with col9:
    st.write("### Rata-rata Harga per Kategori Harga")
    avg_price = filtered_df.groupby("Price_Category")["Price"].mean().reset_index()
    
    # Pengurutan logis kategori harga
    avg_price["Price_Category"] = pd.Categorical(avg_price["Price_Category"], categories=["Budget", "Mid-Range", "Luxury"], ordered=True)
    avg_price = avg_price.sort_values("Price_Category")

    if not avg_price.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=avg_price, x="Price_Category", y="Price", color="#1D9E75", ax=ax)
        
        for p in ax.patches:
            ax.annotate(f'${p.get_height():.2f}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points', fontsize=9)

        ax.set_xlabel("Kategori Harga")
        ax.set_ylabel("Rata-rata Harga")
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Data tidak tersedia.")

# Visualisasi 4: Distribusi Kecepatan Perputaran Stok
with col10:
    st.write("### Distribusi Kecepatan Perputaran Stok")
    turnover_count = filtered_df["Stock_Turnover"].value_counts()

    if not turnover_count.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        colors = sns.color_palette("Set2")[0:len(turnover_count)]
        
        ax.pie(
            turnover_count,
            labels=turnover_count.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            wedgeprops={"width": 0.4, "edgecolor": "white"}
        )
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Data tidak tersedia.")

# Visualisasi 5: Top 10 Brand Berdasarkan Total Produk Terjual
st.subheader("📦 Top 10 Brand Berdasarkan Total Produk Terjual")
top_brand_sold = (
    filtered_df.groupby("Brand")["Sold"]
    .sum()
    .reset_index()
    .sort_values(by="Sold", ascending=False)
    .head(10)
)

if not top_brand_sold.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=top_brand_sold, 
        x="Sold", 
        y="Brand", 
        hue="Brand",
        palette=color_palette, 
        ax=ax,
        legend=False
    )
    
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f'{width:,.0f}', 
                    (width, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', xytext=(5, 0), textcoords='offset points', fontsize=9)

    ax.set_xlabel("Jumlah Terjual")
    ax.set_ylabel("Brand")
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("Tidak ada brand yang cocok dengan kata kunci pencarian Anda.")

# Tabel Hasil Filter
st.subheader("📄 Data Hasil Filter")

st.dataframe(
    filtered_df,
    column_config={
        "Price": st.column_config.NumberColumn("Harga ($)", format="$%.2f"),
        "Revenue_Potential": st.column_config.NumberColumn("Potensi Pendapatan", format="$%.2f"),
        "Sold": st.column_config.NumberColumn("Terjual", format="%d"),
        "Demand_Score": st.column_config.ProgressColumn("Demand Score", min_value=0, max_value=100, format="%.1f")
    },
    use_container_width=True,
    hide_index=True
)