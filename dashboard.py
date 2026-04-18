import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set tema seaborn
sns.set(style='white')

# Load data
day_df = pd.read_csv("day_data.csv")
hour_df = pd.read_csv("hour_data.csv")

# Memastikan kolom tanggal bertipe datetime
day_df['date'] = pd.to_datetime(day_df['date'])
hour_df['date'] = pd.to_datetime(hour_df['date'])

# Mengurutkan data berdasarkan tanggal
day_df.sort_values(by="date", inplace=True)
day_df.reset_index(inplace=True, drop=True)

# Sidebar untuk profil dan filter data
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

with st.sidebar:
    st.header("Dicoding Data Analysis")
    st.markdown("**Nama:** Jibran Tsaqif") 
    
    st.markdown("---")
    st.header("Filter Data")
    
    # Mengambil nilai minimum dan maksimum tanggal dari data
    min_date = day_df["date"].min()
    max_date = day_df["date"].max()
    
    # Menambahkan widget filter rentang waktu (Kalender)
    date_range = st.date_input(
        label='Pilih Rentang Waktu:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Memastikan rentang waktu berupa tuple dengan 2 nilai (start & end)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

# Memfilter data utama berdasarkan input kalender dari sidebar
main_day_df = day_df[(day_df["date"] >= str(start_date)) & (day_df["date"] <= str(end_date))]
main_hour_df = hour_df[(hour_df["date"] >= str(start_date)) & (hour_df["date"] <= str(end_date))]

# Dashboard utama dengan judul dan beberapa grafik analisis
st.title('🚲 Bike Sharing Analytics Dashboard')
st.markdown("---")

if main_day_df.empty:
    st.warning("Data tidak ditemukan untuk rentang waktu yang dipilih. Silakan ubah filter kalender.")
else:
    # Tampilan ringkasan metrik utama
    st.subheader('Ringkasan Penyewaan')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Penyewaan", value=f"{main_day_df['total_count'].sum():,}")
    with col2:
        st.metric("Pengguna Registered", value=f"{main_day_df['registered'].sum():,}")
    with col3:
        st.metric("Pengguna Casual", value=f"{main_day_df['casual'].sum():,}")
    
    st.markdown("---")

    # Grafik 1: Pengaruh Musim dan Kondisi Cuaca
    st.subheader("Pengaruh Musim dan Kondisi Cuaca")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig1a, ax1a = plt.subplots(figsize=(10, 6))
        season_rent = main_day_df.groupby('season')['total_count'].mean().reset_index()
        sns.barplot(x="season", y="total_count", data=season_rent.sort_values(by="total_count", ascending=False), color="steelblue", ax=ax1a)
        ax1a.set_title("Rata-rata Penyewaan Berdasarkan Musim", fontsize=20)
        ax1a.set_xlabel(None)
        ax1a.set_ylabel("Rata-rata Penyewaan", fontsize=15)
        ax1a.set_ylim(0, 6000)
        st.pyplot(fig1a)
    
    with col_b:
        fig1b, ax1b = plt.subplots(figsize=(10, 6))
        weather_rent = main_day_df.groupby('weather')['total_count'].mean().reset_index()
        sns.barplot(x="weather", y="total_count", data=weather_rent.sort_values(by="total_count", ascending=False), color="steelblue", ax=ax1b)
        ax1b.set_title("Rata-rata Penyewaan Berdasarkan Cuaca", fontsize=20)
        ax1b.set_xlabel(None)
        ax1b.set_ylabel(None)
        st.pyplot(fig1b)
    
    st.markdown("---")
    
    # grafik 2: Analisis Tren Penyewaan per Jam
    st.subheader("Analisis Tren Penyewaan per Jam")
    
    hourly_rent = main_hour_df.groupby('hour')[['total_count', 'casual', 'registered']].mean().reset_index()
    
    col_c, col_d = st.columns(2)
    
    with col_c:
        fig2a, ax2a = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='hour', y='total_count', data=hourly_rent, marker='o', color='tab:blue', linewidth=3, ax=ax2a)
        ax2a.set_title("Total Penyewaan per Jam", fontsize=20)
        ax2a.set_xlabel("Jam", fontsize=15)
        ax2a.set_ylabel("Rata-rata Penyewaan", fontsize=15)
        ax2a.set_xticks(range(0, 24))
        ax2a.grid(linestyle='--', alpha=0.5)
        ax2a.set_ylim(0, 500)
        st.pyplot(fig2a)
    
    with col_d:
        fig2b, ax2b = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='hour', y='registered', data=hourly_rent, marker='o', color='tab:orange', label='Registered', linewidth=3, ax=ax2b)
        sns.lineplot(x='hour', y='casual', data=hourly_rent, marker='o', color='tab:green', label='Casual', linewidth=3, ax=ax2b)
        ax2b.set_title("Casual vs Registered per Jam", fontsize=20)
        ax2b.set_xlabel("Jam", fontsize=15)
        ax2b.set_ylabel(None)
        ax2b.set_xticks(range(0, 24))
        ax2b.grid(linestyle='--', alpha=0.5)
        ax2b.legend(fontsize=12)
        st.pyplot(fig2b)
    
    # grafik 3: Clustering berdasarkan Kategori Waktu
    st.markdown("---")
    st.subheader("Clustering: Kategori Waktu Teramai")

    time_category_df = main_hour_df.groupby('time_category')[['total_count']].mean().reset_index()
    time_category_df['time_category'] = pd.Categorical(time_category_df['time_category'], categories=['Pagi', 'Siang', 'Sore', 'Malam'], ordered=True)
    time_category_df = time_category_df.sort_values('time_category')
    
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.barplot(x='time_category', y='total_count', data=time_category_df, color="steelblue", ax=ax3)
    ax3.set_title("Rata-rata Penyewaan Berdasarkan Kategori Waktu", fontsize=20)
    ax3.set_xlabel(None)
    ax3.set_ylabel("Rata-rata Penyewaan", fontsize=15)
    st.pyplot(fig3)

st.caption("Dicoding Data Analysis Project - Jibran Tsaqif")