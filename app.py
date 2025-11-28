import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Rose Diagram Generator", page_icon="🌹", layout="wide")

st.title("🌹 Rose Diagram Generator")
st.markdown("**Input data strike dan dip (minimal 25 data masing-masing) untuk menghasilkan Rose Diagram**")

# Sidebar untuk input data
st.sidebar.header("📊 Input Data")

# Input Strike
st.sidebar.subheader("Strike Data")
strike_input = st.sidebar.text_area(
    "Masukkan nilai strike (pisahkan dengan koma atau baris baru):",
    height=150,
    help="Contoh: 185, 170, 173, 170, 198"
)

# Input Dip
st.sidebar.subheader("Dip Data")
dip_input = st.sidebar.text_area(
    "Masukkan nilai dip (pisahkan dengan koma atau baris baru):",
    height=150,
    help="Contoh: 55, 67, 68, 75, 57"
)

# Tombol generate
generate_button = st.sidebar.button("🚀 Generate Diagram", type="primary")

# Fungsi untuk parse input
def parse_input(input_text):
    """Parse input text menjadi list angka"""
    if not input_text.strip():
        return []
    
    # Ganti newline dengan koma, lalu split
    cleaned = input_text.replace('\n', ',').replace(' ', '')
    values = [float(x.strip()) for x in cleaned.split(',') if x.strip()]
    return values

# Fungsi untuk generate diagram
def generate_rose_diagram(strikes, dips):
    """Generate rose diagram dari data strike dan dip"""
    strikes = np.array(strikes) % 360
    dips = np.array(dips)
    
    az = strikes % 180
    dips_folded = dips
    
    az_full = np.concatenate([az, az + 180])
    dips_full = np.concatenate([dips_folded, dips_folded])
    
    bin_deg = 10
    bins = np.arange(0, 360 + bin_deg, bin_deg)
    bin_centers = (bins[:-1] + bins[1:]) / 2.0
    theta = np.deg2rad(bin_centers)
    width = np.deg2rad(bin_deg)
    
    counts = np.zeros(len(bin_centers))
    dip_means = np.zeros(len(bin_centers))
    
    # Optimasi: hitung np.sum(idx) hanya sekali per iterasi
    for i in range(len(bin_centers)):
        idx = (az_full >= bins[i]) & (az_full < bins[i+1])
        count = np.sum(idx)
        counts[i] = count
        if count > 0:
            dip_means[i] = np.mean(dips_full[idx])
        else:
            dip_means[i] = 0
    
    # Perbaikan: hindari division by zero
    dip_max = dip_means.max()
    dip_norm = dip_means / dip_max if dip_max > 0 else dip_means
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    
    bars = ax.bar(theta, counts, width=width, bottom=0, edgecolor='k', color=plt.cm.viridis(dip_norm))
    
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=dip_means.min(), vmax=dip_means.max()))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.1)
    cbar.set_label('Average Dip (°)', fontsize=12)
    
    ax.set_title('Rose Diagram 360° (Strike with Dip Color)', fontsize=14, pad=20)
    
    return fig

# Main content area
if generate_button:
    # Parse input
    strikes = parse_input(strike_input)
    dips = parse_input(dip_input)
    
    # Validasi
    errors = []
    
    if len(strikes) == 0:
        errors.append("❌ Data strike tidak boleh kosong")
    elif len(strikes) < 25:
        errors.append(f"❌ Data strike minimal 25, saat ini hanya {len(strikes)} data")
    
    if len(dips) == 0:
        errors.append("❌ Data dip tidak boleh kosong")
    elif len(dips) < 25:
        errors.append(f"❌ Data dip minimal 25, saat ini hanya {len(dips)} data")
    
    if len(strikes) != len(dips):
        errors.append(f"❌ Jumlah data strike ({len(strikes)}) dan dip ({len(dips)}) harus sama")
    
    # Tampilkan error atau generate diagram
    if errors:
        for error in errors:
            st.error(error)
    else:
        # Tampilkan info data
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Jumlah Data Strike", len(strikes))
        with col2:
            st.metric("Jumlah Data Dip", len(dips))
        with col3:
            st.metric("Status", "✅ Valid")
        
        # Generate dan tampilkan diagram
        with st.spinner("Generating diagram..."):
            fig = generate_rose_diagram(strikes, dips)
            st.pyplot(fig)
            plt.close(fig)
        
        st.success("✅ Diagram berhasil dihasilkan!")
        
        # Tampilkan preview data
        with st.expander("📋 Preview Data"):
            df_preview = pd.DataFrame({
                'Strike': strikes,
                'Dip': dips
            })
            st.dataframe(df_preview, use_container_width=True)
            
            # Download button untuk CSV
            csv = df_preview.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Download Data sebagai CSV",
                data=csv,
                file_name="rose_diagram_data.csv",
                mime="text/csv"
            )

else:
    # Tampilkan instruksi
    st.info("👈 **Silakan masukkan data di sidebar kiri**")
    
    st.markdown("""
    ### 📝 Cara Penggunaan:
    1. Masukkan data **strike** di kolom pertama (minimal 25 data)
    2. Masukkan data **dip** di kolom kedua (minimal 25 data)
    3. Pastikan jumlah data strike dan dip **sama**
    4. Klik tombol **Generate Diagram**
    5. Diagram akan muncul di halaman ini
    
    ### 💡 Tips:
    - Data dapat dipisahkan dengan **koma** atau **baris baru**
    - Contoh format: `185, 170, 173, 170` atau `185\\n170\\n173\\n170`
    - Nilai strike biasanya antara 0-360 derajat
    - Nilai dip biasanya antara 0-90 derajat
    """)

