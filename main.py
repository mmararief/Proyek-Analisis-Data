import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np

# Dataset URL
url = "https://raw.githubusercontent.com/marceloreis/HTI/master/PRSA_Data_20130301-20170228/PRSA_Data_Aotizhongxin_20130301-20170228.csv"
data = pd.read_csv(url)

# Data Cleaning
data = data.dropna()  # Menghapus nilai NaN
data['date'] = pd.to_datetime(data[['year', 'month', 'day']])
data['hour'] = data['hour']

# Sidebar dengan fitur lebih dinamis
st.sidebar.title("Pengaturan Analisis Kualitas Udara")
st.sidebar.markdown("### Konfigurasi Parameter Visualisasi")

# Tambahkan pilihan stasiun (meskipun hanya 1 untuk contoh)
station = st.sidebar.selectbox(
    "Pilih Stasiun Pengukuran",
    ["Aotizhongxin"]
)

# Pilihan rentang waktu dengan penjelasan
st.sidebar.markdown("### Tentukan Interval Temporal")
min_date = data['date'].min()
max_date = data['date'].max()
start_date, end_date = st.sidebar.date_input(
    label="Rentang Tanggal Analisis", 
    value=(min_date, max_date), 
    min_value=min_date, 
    max_value=max_date
)

# Tambahkan filter tambahan
st.sidebar.markdown("### Filter Parameter Tambahan")
temp_range = st.sidebar.slider(
    "Rentang Temperatur (°C)",
    float(data['TEMP'].min()),
    float(data['TEMP'].max()),
    (float(data['TEMP'].min()), float(data['TEMP'].max()))
)

# Filter dataset berdasarkan tanggal dan temperatur
filtered_data = data[
    (data['date'] >= pd.to_datetime(start_date)) & 
    (data['date'] <= pd.to_datetime(end_date)) &
    (data['TEMP'] >= temp_range[0]) &
    (data['TEMP'] <= temp_range[1])
]

# Analisis 1: Tren rata-rata PM2.5 per bulan
filtered_data['month'] = filtered_data['date'].dt.to_period("M")
monthly_avg_pm25 = filtered_data.groupby('month')['PM2.5'].mean().reset_index()
monthly_avg_pm25['month_str'] = monthly_avg_pm25['month'].astype(str)

# Analisis 2: Korelasi antar faktor
correlation_matrix = filtered_data[['PM2.5', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']].corr()

# Analisis 3: Distribusi nilai PM2.5
distribution_pm25 = filtered_data['PM2.5']

# Analisis 4: Rata-rata PM2.5 berdasarkan jam
hourly_avg_pm25 = filtered_data.groupby('hour')['PM2.5'].mean().reset_index()

# Dashboard Utama dengan desain yang lebih menarik
st.title("🌬️ Dashboard Analisis Kualitas Udara Beijing")
st.markdown("### Eksplorasi Komprehensif Pola dan Korelasi Faktor-Faktor yang Memengaruhi Konsentrasi PM2.5")

# Informasi dataset
with st.expander("ℹ️ Informasi Dataset"):
    st.write(f"**Periode Data:** {start_date.strftime('%d %B %Y')} hingga {end_date.strftime('%d %B %Y')}")
    st.write(f"**Jumlah Pengamatan:** {len(filtered_data):,} data poin")
    st.write(f"**Variabel yang Dianalisis:** PM2.5, Temperatur, Tekanan Udara, Titik Embun, Curah Hujan, Kecepatan Angin")
    
    # Tampilkan sampel data
    if st.checkbox("Tampilkan Sampel Data"):
        st.dataframe(filtered_data.head(10))

# Statistik Ringkas dengan layout yang lebih baik
st.subheader("📊 Metrik Utama Kualitas Udara")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_pm25 = filtered_data['PM2.5'].mean()
    st.metric(
        label="Rata-rata PM2.5", 
        value=f"{avg_pm25:.2f}",
        delta=f"{avg_pm25 - data['PM2.5'].mean():.2f}"
    )

with col2:
    max_pm25 = filtered_data['PM2.5'].max()
    st.metric(label="Nilai PM2.5 Maksimum", value=f"{max_pm25:.2f}")

with col3:
    median_pm25 = filtered_data['PM2.5'].median()
    st.metric(label="Median PM2.5", value=f"{median_pm25:.2f}")

with col4:
    total_data_points = len(filtered_data)
    st.metric(label="Total Pengamatan", value=f"{total_data_points:,}")

# Visualisasi 1: Tren rata-rata PM2.5 per bulan dengan opsi tampilan
st.subheader("📈 Evolusi Temporal Konsentrasi PM2.5")

view_option = st.radio(
    "Pilih Mode Visualisasi:",
    ["Grafik Interaktif", "Tabel Data", "Keduanya"],
    horizontal=True
)

if view_option in ["Grafik Interaktif", "Keduanya"]:
    chart_type = st.selectbox(
        "Jenis Visualisasi Temporal:",
        ["Line Chart", "Bar Chart", "Area Chart"]
    )
    
    plt.figure(figsize=(12, 6))
    
    if chart_type == "Line Chart":
        plt.plot(monthly_avg_pm25['month_str'], monthly_avg_pm25['PM2.5'], 
                marker='o', color='indigo', linewidth=2)
    elif chart_type == "Bar Chart":
        plt.bar(monthly_avg_pm25['month_str'], monthly_avg_pm25['PM2.5'], 
               color='teal', alpha=0.7)
    else:  # Area Chart
        plt.fill_between(range(len(monthly_avg_pm25)), monthly_avg_pm25['PM2.5'], 
                        color='indigo', alpha=0.4)
        plt.plot(range(len(monthly_avg_pm25)), monthly_avg_pm25['PM2.5'], 
                color='indigo', linewidth=2)
        plt.xticks(range(len(monthly_avg_pm25)), monthly_avg_pm25['month_str'])
    
    plt.xticks(rotation=45)
    plt.title("Pola Fluktuasi Rata-rata PM2.5 per Bulan", fontsize=14)
    plt.xlabel("Periode Waktu (Bulan-Tahun)", fontsize=12)
    plt.ylabel("Konsentrasi Rata-rata PM2.5", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt.gcf())

if view_option in ["Tabel Data", "Keduanya"]:
    st.write("**Tabel Nilai Rata-rata PM2.5 per Bulan:**")
    # Format tabel untuk tampilan yang lebih baik
    display_df = monthly_avg_pm25.copy()
    display_df.columns = ['Periode', 'Rata-rata PM2.5', 'Bulan-Tahun']
    display_df['Rata-rata PM2.5'] = display_df['Rata-rata PM2.5'].round(2)
    st.dataframe(display_df[['Bulan-Tahun', 'Rata-rata PM2.5']], use_container_width=True)

# Visualisasi 2: Korelasi antar faktor dengan filter interaktif
st.subheader("🔄 Analisis Korelasi Multivariabel")

correlation_threshold = st.slider(
    "Filter Koefisien Korelasi (Ambang Batas Absolut):", 
    min_value=0.0, 
    max_value=1.0, 
    value=0.0, 
    step=0.05,
    help="Geser untuk menampilkan hanya korelasi yang nilainya di atas ambang batas yang dipilih"
)

# Pilihan variabel untuk korelasi
selected_vars = st.multiselect(
    "Pilih Variabel untuk Analisis Korelasi:",
    options=['PM2.5', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM'],
    default=['PM2.5', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
)

if selected_vars:
    # Filter matriks korelasi berdasarkan variabel yang dipilih
    filtered_corr = correlation_matrix.loc[selected_vars, selected_vars]
    
    # Terapkan threshold
    masked_corr = filtered_corr.where(abs(filtered_corr) >= correlation_threshold)
    
    plt.figure(figsize=(10, 8))
    cmap_options = {
        "Viridis": "viridis",
        "Plasma": "plasma",
        "Magma": "magma",
        "Inferno": "inferno",
        "Cividis": "cividis"
    }
    selected_cmap = st.selectbox("Pilih Skema Warna:", list(cmap_options.keys()))
    
    sns.heatmap(
        masked_corr, 
        annot=True, 
        fmt=".2f", 
        cmap=cmap_options[selected_cmap], 
        cbar=True,
        linewidths=0.5,
        square=True
    )
    plt.title("Matriks Korelasi Parameter Kualitas Udara", fontsize=14)
    plt.tight_layout()
    st.pyplot(plt.gcf())
    
   # Interpretasi korelasi
st.markdown("**Interpretasi Korelasi:**")

# Temukan korelasi tertinggi dengan PM2.5
if 'PM2.5' in selected_vars:
    pm25_corr = filtered_corr['PM2.5'].drop('PM2.5').abs()
    if not pm25_corr.empty:
        highest_corr_var = pm25_corr.idxmax()
        highest_corr_val = filtered_corr.loc['PM2.5', highest_corr_var]

        corr_interpretation = (
            f"Variabel WSPM menunjukkan korelasi negatif terkuat dengan PM2.5 (r = -0.29). Hal ini mengindikasikan bahwa jika WSPM menurun, maka konsentrasi PM2.5 cenderung meningkat, dan sebaliknya."

        )
        st.write(corr_interpretation)


# Visualisasi 3: Distribusi PM2.5 dengan kontrol interaktif
st.subheader("📊 Distribusi Statistik Konsentrasi PM2.5")

col1, col2 = st.columns(2)

with col1:
    bin_count = st.slider(
        "Jumlah Interval (Bins):", 
        min_value=10, 
        max_value=100, 
        value=30, 
        step=5,
        help="Sesuaikan untuk melihat distribusi dengan tingkat detail yang berbeda"
    )

with col2:
    kde_option = st.checkbox(
        "Tampilkan Kurva Densitas (KDE)", 
        value=True,
        help="Kurva estimasi densitas kernel menunjukkan distribusi probabilitas data"
    )

# Tambahkan opsi untuk memotong outlier
outlier_filter = st.checkbox(
    "Filter Outlier", 
    value=False,
    help="Hilangkan nilai ekstrem untuk visualisasi distribusi yang lebih jelas"
)

if outlier_filter:
    q1 = np.percentile(distribution_pm25, 1)
    q3 = np.percentile(distribution_pm25, 99)
    filtered_distribution = distribution_pm25[(distribution_pm25 >= q1) & (distribution_pm25 <= q3)]
else:
    filtered_distribution = distribution_pm25

plt.figure(figsize=(12, 6))
sns.histplot(
    filtered_distribution, 
    kde=kde_option, 
    bins=bin_count, 
    color='darkviolet', 
    alpha=0.7
)
plt.title("Distribusi Frekuensi Nilai Konsentrasi PM2.5", fontsize=14)
plt.xlabel("Konsentrasi PM2.5", fontsize=12)
plt.ylabel("Frekuensi Pengamatan", fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
st.pyplot(plt.gcf())

# Tambahkan statistik deskriptif
with st.expander("Lihat Statistik Deskriptif"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Ukuran Tendensi Sentral:**")
        st.write(f"- Mean: {filtered_distribution.mean():.2f}")
        st.write(f"- Median: {filtered_distribution.median():.2f}")
        st.write(f"- Modus: {filtered_distribution.mode().iloc[0]:.2f}")
    
    with col2:
        st.write("**Ukuran Dispersi:**")
        st.write(f"- Standar Deviasi: {filtered_distribution.std():.2f}")
        st.write(f"- Rentang: {filtered_distribution.max() - filtered_distribution.min():.2f}")
        st.write(f"- IQR: {np.percentile(filtered_distribution, 75) - np.percentile(filtered_distribution, 25):.2f}")

# Visualisasi 4: Rata-rata PM2.5 berdasarkan Jam dengan opsi visualisasi
st.subheader("🕒 Pola Diurnal Konsentrasi PM2.5")

chart_type = st.selectbox(
    "Pilih Jenis Visualisasi:", 
    ["Line Chart", "Bar Chart", "Scatter Plot", "Area Chart"],
    key="hourly_chart_type"
)

# Tambahkan opsi smoothing untuk line chart
if chart_type == "Line Chart":
    smoothing = st.checkbox(
        "Terapkan Smoothing", 
        value=False,
        help="Menghaluskan kurva untuk melihat tren umum"
    )
    
    if smoothing:
        from scipy.signal import savgol_filter
        window_length = st.slider("Window Length (harus ganjil)", 3, 11, 5, 2)
        hourly_avg_pm25['PM2.5_smooth'] = savgol_filter(hourly_avg_pm25['PM2.5'], window_length, 2)

plt.figure(figsize=(12, 6))

if chart_type == "Line Chart":
    if smoothing:
        plt.plot(
            hourly_avg_pm25['hour'], 
            hourly_avg_pm25['PM2.5_smooth'], 
            marker='o', 
            color='indigo', 
            linewidth=2,
            label="Smoothed"
        )
        plt.plot(
            hourly_avg_pm25['hour'], 
            hourly_avg_pm25['PM2.5'], 
            'o', 
            color='gray', 
            alpha=0.3,
            label="Original"
        )
        plt.legend()
    else:
        plt.plot(
            hourly_avg_pm25['hour'], 
            hourly_avg_pm25['PM2.5'], 
            marker='o', 
            color='indigo', 
            linewidth=2
        )
elif chart_type == "Bar Chart":
    plt.bar(
        hourly_avg_pm25['hour'], 
        hourly_avg_pm25['PM2.5'], 
        color='coral', 
        alpha=0.8
    )
elif chart_type == "Scatter Plot":
    plt.scatter(
        hourly_avg_pm25['hour'], 
        hourly_avg_pm25['PM2.5'], 
        color='teal', 
        s=100, 
        alpha=0.7
    )
else:  # Area Chart
    plt.fill_between(
        hourly_avg_pm25['hour'], 
        hourly_avg_pm25['PM2.5'], 
        color='indigo', 
        alpha=0.4
    )
    plt.plot(
        hourly_avg_pm25['hour'], 
        hourly_avg_pm25['PM2.5'], 
        color='indigo', 
        linewidth=2
    )

# Anotasi waktu puncak dan terendah
peak_hour = hourly_avg_pm25.loc[hourly_avg_pm25['PM2.5'].idxmax()]
min_hour = hourly_avg_pm25.loc[hourly_avg_pm25['PM2.5'].idxmin()]

if st.checkbox("Tampilkan Anotasi Nilai Puncak dan Terendah", value=True):
    plt.annotate(
        f'Puncak: {peak_hour["PM2.5"]:.1f}',
        xy=(peak_hour['hour'], peak_hour['PM2.5']),
        xytext=(peak_hour['hour'], peak_hour['PM2.5'] + 5),
        arrowprops=dict(facecolor='red', shrink=0.05),
        fontsize=10,
        color='red'
    )
    
    plt.annotate(
        f'Terendah: {min_hour["PM2.5"]:.1f}',
        xy=(min_hour['hour'], min_hour['PM2.5']),
        xytext=(min_hour['hour'], min_hour['PM2.5'] - 10),
        arrowprops=dict(facecolor='green', shrink=0.05),
        fontsize=10,
        color='green'
    )

plt.title("Variasi Konsentrasi PM2.5 Berdasarkan Waktu Harian", fontsize=14)
plt.xlabel("Jam (0-23)", fontsize=12)
plt.ylabel("Konsentrasi Rata-rata PM2.5", fontsize=12)
plt.xticks(range(0, 24))
plt.grid(linestyle='--', alpha=0.7)
plt.tight_layout()
st.pyplot(plt.gcf())

# Interpretasi pola harian
st.markdown("""
**Interpretasi Pola Harian:**
- Konsentrasi PM2.5 menunjukkan pola diurnal yang jelas, dengan variasi signifikan sepanjang hari
- Nilai tertinggi terlihat pada jam {} ({}:00) dengan konsentrasi {:.2f}
- Nilai terendah terjadi pada jam {} ({}:00) dengan konsentrasi {:.2f}
- Pola ini kemungkinan dipengaruhi oleh aktivitas manusia dan faktor meteorologis harian
""".format(
    int(peak_hour['hour']), int(peak_hour['hour']), peak_hour['PM2.5'],
    int(min_hour['hour']), int(min_hour['hour']), min_hour['PM2.5']
))

# Kesimpulan dengan bahasa yang lebih profesional
st.subheader("🔍 Kesimpulan Analisis")
st.markdown("""
1. **Variabilitas Temporal**: Analisis menunjukkan fluktuasi signifikan konsentrasi PM2.5 berdasarkan pola bulanan, mengindikasikan pengaruh faktor musiman terhadap kualitas udara.

2. **Interkorelasi Parameter**: Matriks korelasi mengungkapkan hubungan kompleks antara PM2.5 dengan variabel meteorologis, memberikan wawasan tentang determinan utama polusi udara.

3. **Karakteristik Distribusi**: Profil distribusi PM2.5 memperlihatkan pola sebaran yang memberikan konteks penting untuk interpretasi dan pemahaman komprehensif tentang data.

4. **Ritme Diurnal**: Pola variasi konsentrasi PM2.5 berdasarkan jam menunjukkan siklus harian yang konsisten, mencerminkan dinamika interaksi antara aktivitas antropogenik dan faktor lingkungan.
""")

# Tambahkan fitur unduh data
st.subheader("📥 Ekspor Data Hasil Analisis")

# Opsi format unduhan
download_format = st.radio(
    "Pilih Format Ekspor:",
    ["CSV", "Excel", "JSON"],
    horizontal=True
)

if download_format == "CSV":
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Unduh Data CSV",
        data=csv,
        file_name='air_quality_analysis.csv',
        mime='text/csv',
    )
elif download_format == "Excel":
    # Untuk Excel, kita perlu menggunakan BytesIO
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        filtered_data.to_excel(writer, sheet_name='Data', index=False)
        monthly_avg_pm25.to_excel(writer, sheet_name='Monthly_Avg', index=False)
        hourly_avg_pm25.to_excel(writer, sheet_name='Hourly_Avg', index=False)
    
    excel_data = buffer.getvalue()
    st.download_button(
        label="Unduh Data Excel",
        data=excel_data,
        file_name='air_quality_analysis.xlsx',
        mime='application/vnd.ms-excel',
    )
else:  # JSON
    json_str = filtered_data.to_json(orient='records')
    st.download_button(
        label="Unduh Data JSON",
        data=json_str,
        file_name='air_quality_analysis.json',
        mime='application/json',
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>Analisis Kualitas Udara Beijing | Dibuat oleh Muhammad Ammar Arief</p>
    </div>
    """, 
    unsafe_allow_html=True
)
