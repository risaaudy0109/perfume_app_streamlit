# Parfum Revenue Potential Predictor

Aplikasi Streamlit untuk memprediksi **Revenue Potential** produk parfum
menggunakan 2 model terpisah: **Ridge Regression** dan **ANN (Neural Network)**.

## Struktur File

```
app/
├── app.py                          # Halaman utama Streamlit (UI, navigasi sidebar)
├── prediction.py                   # Logika preprocessing input -> fitur -> prediksi (Ridge & ANN)
├── visualization.py                # Semua chart Plotly (gauge, what-if, koefisien, dll)
├── config.json                     # Metadata: opsi dropdown, statistik data, metrik model
├── preprocessor_combined.joblib    # Gabungan preprocessor Ridge + ANN (1 file, lihat catatan di bawah)
├── best_model_ridge.joblib         # Model Ridge Regression
├── ann_parfum_regression.keras     # Model ANN
└── requirements.txt                # streamlit==1.6.1 + dependensi lain
```

## Cara Menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Catatan Penting / Asumsi yang Diambil

### 1. Mengapa `preprocessor.joblib` & `preprocessor__1_.joblib` digabung jadi SATU file, tapi isinya tetap 2 objek berbeda?

Anda meminta agar kedua preprocessor dijadikan satu file karena dianggap berisi
code yang sama. Setelah dicek isinya **memang strukturnya identik** (sama-sama
dict berisi `scaler`, `ohe`, `ordinal` dengan kategori ordinal/nominal yang
sama persis), **namun nilai hasil fit `RobustScaler`-nya berbeda**:

| File asli                   | Dipakai di      | `Available` di-fit dari |
|------------------------------|-----------------|--------------------------|
| `preprocessor__1_.joblib`   | Ridge (MP01)    | `Available` mentah (median=9, IQR=7) |
| `preprocessor.joblib`       | ANN (MP02)      | `log1p(Available)` (median=2.30) |

Ini berasal langsung dari notebook: MP01 menskalakan `Available` apa adanya,
sedangkan MP02 melakukan `log1p()` pada `Available` sebelum di-scale (lihat
komentar di MP02: *"Available di-log langsung sebagai pengganti kolom
aslinya"*). Karena nilai fit-nya berbeda, **tidak mungkin** memakai satu
`RobustScaler` yang sama untuk kedua model tanpa merusak akurasi salah
satunya.

**Solusi yang diambil**: tetap digabung jadi **satu file `.joblib`**
(`preprocessor_combined.joblib`) berbentuk `{"ridge": {...}, "ann": {...}}`,
sehingga secara file Anda hanya punya 1 file preprocessor, tapi isinya tetap
menyimpan 2 scaler yang benar untuk masing-masing model. `prediction.py` akan
otomatis memilih sub-dict yang sesuai berdasarkan model yang dipanggil.

### 2. Mengapa kolom `Brand` dan `Country` tidak ada di form prediksi?

Di kedua notebook, `Brand` dan `Country` diproses dengan **Target Encoding**
(rata-rata historis `Revenue_Potential` per brand/negara, dengan smoothing).
Tabel lookup hasil target encoding tersebut **tidak diekspor** ke file apa pun
(hanya model `.joblib`/`.keras` dan dict preprocessor `scaler/ohe/ordinal`
yang disimpan) — begitu juga dataset asli (`Perfume_Market_Intelligence_Dataset.csv`)
tidak ikut diupload, sehingga tabel rata-rata per brand/negara tidak bisa
dihitung ulang dengan akurat di sisi aplikasi.

Untuk tetap menjaga input ke model sesuai jumlah fitur yang dilatih (15 fitur),
kolom `TE_Brand` dan `TE_Country` diisi dengan **nilai rata-rata global**
(`te_fallback_value_log` di `config.json`) sebagai pendekatan netral — artinya
prediksi merepresentasikan "brand & negara rata-rata pasar", bukan brand/negara
spesifik. Hal ini sudah dijelaskan langsung di UI aplikasi (lihat caption
"ℹ️" di setiap form).

> Jika di kemudian hari Anda memiliki dataset aslinya, tabel target-encoding
> per brand/negara bisa dihitung ulang dan ditambahkan sebagai input form —
> tinggal tambahkan dict lookup baru dan gunakan nilainya di `prediction.py`
> menggantikan `TE_FALLBACK`.

### 3. Mengapa file `.json` (`config.json`) dibuat, dan apa fungsinya?

`config.json` bukan file dekoratif — file ini **dipakai langsung oleh
`app.py`** untuk:
1. Mengisi pilihan dropdown form (`categorical_options`) — supaya kategori
   yang ditampilkan ke user pasti sama dengan kategori yang dikenal model
   (sumber: `categories_` dari `OrdinalEncoder`/`OneHotEncoder` di notebook).
2. Menentukan rentang & nilai default slider "Available" (`numeric_stats`),
   diambil dari `describe()` dataset di notebook MP01.
3. Menampilkan kartu metrik performa model (R², MAE, RMSE) di tiap halaman
   (`model_metrics`), diambil dari hasil evaluasi yang tercetak di notebook.
4. Menjadi nilai acuan/benchmark (median, rata-rata, kuartil atas) saat
   memvisualisasikan posisi hasil prediksi dibanding "pasar" pada gauge chart.

Tanpa `config.json`, `app.py` tidak punya sumber tunggal untuk semua nilai
tersebut dan harus hardcode di banyak tempat.

### 4. Mengapa tidak ada folder `utils/`?

Sesuai permintaan — semua fungsi preprocessing & prediksi langsung ditulis di
`prediction.py`, dan semua fungsi chart di `visualization.py`, tanpa folder
tambahan. Model (`.joblib`, `.keras`) tetap dipakai langsung sebagai artefak
hasil training dari notebook, tidak diduplikasi logikanya.

### 5. Mengapa Ridge dan ANN ditampilkan di halaman terpisah?

Sesuai permintaan — agar perbedaan hasil dan karakteristik kedua model tetap
terlihat jelas oleh user, prediksi TIDAK digabung/dirata-ratakan jadi satu
angka. Halaman "Perbandingan Model" hanya membandingkan metrik performa
(MAE/RMSE) dan menampilkan hasil prediksi terakhir dari masing-masing halaman
secara berdampingan, tanpa menggabungkan logikanya.

## Kompatibilitas Versi

Ditulis & diuji konsep untuk **streamlit==1.6.1**, sehingga sengaja
menghindari API yang baru tersedia di versi lebih baru:
- Navigasi memakai `st.sidebar.radio` (bukan `st.tabs`, baru ada di 1.11+)
- Caching memakai `st.cache(allow_output_mutation=True)` (bukan
  `st.cache_data`/`st.cache_resource`, baru ada di 1.18+)
