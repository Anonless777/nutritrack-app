import streamlit as st
import datetime
import json
import os

# ──────────────────────────────────────────────
# CONFIG & THEME
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="NutriTrack – Manajemen Nutrisi Harian",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look
st.markdown("""
<style>
    /* Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0c29 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Cards */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 18px;
        backdrop-filter: blur(12px);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
    }
    div[data-testid="stMetric"] label {
        color: #a5b4fc !important;
        font-weight: 500;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #e0e7ff !important;
        font-weight: 700;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        transform: translateY(-1px);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 500;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        font-weight: 500;
    }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* Headings */
    h1, h2, h3 { color: #e0e7ff !important; }

    /* Progress bars */
    .stProgress > div > div {
        border-radius: 10px;
        height: 10px !important;
    }

    /* Glass card helper */
    .glass-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(12px);
        margin-bottom: 16px;
    }
    .glass-card h4 {
        margin-top: 0;
        color: #c4b5fd !important;
    }

    /* Success / info boxes */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* Table */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA PERSISTENCE (JSON file)
# ──────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "nutritrack_data.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"profile": {}, "entries": {}, "custom_foods": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Load once into session state
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# ──────────────────────────────────────────────
# FOOD DATABASE (per 100 g / ml unless noted)
# ──────────────────────────────────────────────
DEFAULT_FOODS = [
    {"nama": "Nasi Putih (100g)", "kalori": 130, "protein": 2.7, "karbohidrat": 28.2, "lemak": 0.3, "serat": 0.4},
    {"nama": "Nasi Merah (100g)", "kalori": 111, "protein": 2.6, "karbohidrat": 23.5, "lemak": 0.9, "serat": 1.8},
    {"nama": "Roti Gandum (1 lembar)", "kalori": 69, "protein": 3.6, "karbohidrat": 11.6, "lemak": 1.1, "serat": 1.9},
    {"nama": "Telur Ayam (1 butir)", "kalori": 74, "protein": 6.3, "karbohidrat": 0.4, "lemak": 5.0, "serat": 0.0},
    {"nama": "Dada Ayam (100g)", "kalori": 165, "protein": 31.0, "karbohidrat": 0.0, "lemak": 3.6, "serat": 0.0},
    {"nama": "Ikan Salmon (100g)", "kalori": 208, "protein": 20.4, "karbohidrat": 0.0, "lemak": 13.4, "serat": 0.0},
    {"nama": "Tempe (100g)", "kalori": 192, "protein": 18.5, "karbohidrat": 7.6, "lemak": 10.8, "serat": 1.4},
    {"nama": "Tahu (100g)", "kalori": 76, "protein": 8.1, "karbohidrat": 1.9, "lemak": 4.8, "serat": 0.3},
    {"nama": "Pisang (1 buah)", "kalori": 89, "protein": 1.1, "karbohidrat": 22.8, "lemak": 0.3, "serat": 2.6},
    {"nama": "Apel (1 buah)", "kalori": 52, "protein": 0.3, "karbohidrat": 13.8, "lemak": 0.2, "serat": 2.4},
    {"nama": "Bayam (100g)", "kalori": 23, "protein": 2.9, "karbohidrat": 3.6, "lemak": 0.4, "serat": 2.2},
    {"nama": "Brokoli (100g)", "kalori": 34, "protein": 2.8, "karbohidrat": 6.6, "lemak": 0.4, "serat": 2.6},
    {"nama": "Susu Full Cream (250ml)", "kalori": 156, "protein": 8.0, "karbohidrat": 12.3, "lemak": 8.3, "serat": 0.0},
    {"nama": "Yogurt (150g)", "kalori": 92, "protein": 5.3, "karbohidrat": 12.0, "lemak": 2.5, "serat": 0.0},
    {"nama": "Kentang (100g)", "kalori": 77, "protein": 2.0, "karbohidrat": 17.5, "lemak": 0.1, "serat": 2.2},
    {"nama": "Mie Instan (1 bungkus)", "kalori": 380, "protein": 8.0, "karbohidrat": 52.0, "lemak": 14.0, "serat": 2.0},
    {"nama": "Oatmeal (40g)", "kalori": 150, "protein": 5.0, "karbohidrat": 27.0, "lemak": 2.5, "serat": 4.0},
    {"nama": "Alpukat (½ buah)", "kalori": 120, "protein": 1.5, "karbohidrat": 6.4, "lemak": 11.0, "serat": 5.0},
    {"nama": "Kacang Almond (30g)", "kalori": 170, "protein": 6.0, "karbohidrat": 6.0, "lemak": 15.0, "serat": 3.5},
    {"nama": "Ubi Jalar (100g)", "kalori": 86, "protein": 1.6, "karbohidrat": 20.1, "lemak": 0.1, "serat": 3.0},
]

# Merge custom foods
all_foods = DEFAULT_FOODS + data.get("custom_foods", [])

# ──────────────────────────────────────────────
#  SIDEBAR – Profile & Daily Target
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥗 NutriTrack")
    st.caption("Kelola asupan nutrisi harianmu")
    st.divider()

    st.markdown("### 👤 Profil Pengguna")
    profile = data.get("profile", {})

    nama = st.text_input("Nama", value=profile.get("nama", ""), placeholder="Masukkan nama")
    umur = st.number_input("Umur (tahun)", min_value=1, max_value=120, value=profile.get("umur", 25))
    jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"],
                                 index=0 if profile.get("jk", "Laki-laki") == "Laki-laki" else 1)
    berat = st.number_input("Berat Badan (kg)", min_value=10.0, max_value=300.0,
                            value=float(profile.get("berat", 65.0)), step=0.5)
    tinggi = st.number_input("Tinggi Badan (cm)", min_value=50.0, max_value=250.0,
                             value=float(profile.get("tinggi", 170.0)), step=0.5)
    aktivitas = st.selectbox("Tingkat Aktivitas", [
        "Tidak aktif (jarang olahraga)",
        "Ringan (1-3x/minggu)",
        "Sedang (3-5x/minggu)",
        "Aktif (6-7x/minggu)",
        "Sangat aktif (atlet)"
    ], index=profile.get("aktivitas_idx", 1))

    aktivitas_multiplier = {
        "Tidak aktif (jarang olahraga)": 1.2,
        "Ringan (1-3x/minggu)": 1.375,
        "Sedang (3-5x/minggu)": 1.55,
        "Aktif (6-7x/minggu)": 1.725,
        "Sangat aktif (atlet)": 1.9,
    }

    # BMR Mifflin-St Jeor
    if jenis_kelamin == "Laki-laki":
        bmr = 10 * berat + 6.25 * tinggi - 5 * umur + 5
    else:
        bmr = 10 * berat + 6.25 * tinggi - 5 * umur - 161

    tdee = bmr * aktivitas_multiplier[aktivitas]

    st.divider()
    st.markdown("### 🎯 Target Harian")
    target_kalori = st.number_input("Kalori (kkal)", min_value=500, max_value=6000,
                                    value=profile.get("target_kalori", int(round(tdee))), step=50)
    target_protein = st.number_input("Protein (g)", min_value=10, max_value=500,
                                     value=profile.get("target_protein", int(round(berat * 1.6))), step=5)
    target_karbo = st.number_input("Karbohidrat (g)", min_value=50, max_value=800,
                                   value=profile.get("target_karbo", int(round(target_kalori * 0.5 / 4))), step=5)
    target_lemak = st.number_input("Lemak (g)", min_value=10, max_value=300,
                                   value=profile.get("target_lemak", int(round(target_kalori * 0.25 / 9))), step=5)
    target_serat = st.number_input("Serat (g)", min_value=5, max_value=100,
                                   value=profile.get("target_serat", 30), step=1)

    if st.button("💾 Simpan Profil", use_container_width=True):
        akt_list = list(aktivitas_multiplier.keys())
        data["profile"] = {
            "nama": nama,
            "umur": umur,
            "jk": jenis_kelamin,
            "berat": berat,
            "tinggi": tinggi,
            "aktivitas_idx": akt_list.index(aktivitas),
            "target_kalori": target_kalori,
            "target_protein": target_protein,
            "target_karbo": target_karbo,
            "target_lemak": target_lemak,
            "target_serat": target_serat,
        }
        save_data(data)
        st.success("Profil tersimpan!")

    st.divider()
    st.markdown(f"**BMR:** {bmr:,.0f} kkal")
    st.markdown(f"**TDEE:** {tdee:,.0f} kkal")

# ──────────────────────────────────────────────
# MAIN CONTENT
# ──────────────────────────────────────────────
today_str = datetime.date.today().isoformat()

# Header
greeting = f"Halo, **{nama}**! 👋" if nama else "Selamat datang! 👋"
st.markdown(f"# {greeting}")
st.markdown(f"📅 **{datetime.date.today().strftime('%A, %d %B %Y')}**")
st.divider()

# Tabs
tab_dashboard, tab_tambah, tab_database, tab_riwayat = st.tabs([
    "📊 Dashboard", "➕ Tambah Asupan", "🍎 Database Makanan", "📅 Riwayat"
])

# ──────────────────────────────────────────────
# TAB 1: DASHBOARD
# ──────────────────────────────────────────────
with tab_dashboard:
    # Today's totals
    today_entries = data.get("entries", {}).get(today_str, [])
    total_kal = sum(e["kalori"] for e in today_entries)
    total_pro = sum(e["protein"] for e in today_entries)
    total_kar = sum(e["karbohidrat"] for e in today_entries)
    total_lem = sum(e["lemak"] for e in today_entries)
    total_ser = sum(e["serat"] for e in today_entries)

    st.markdown("### 📈 Ringkasan Hari Ini")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        delta_kal = target_kalori - total_kal
        st.metric("🔥 Kalori", f"{total_kal:,} kkal", f"Sisa {delta_kal:,}" if delta_kal > 0 else "Target tercapai ✅")
    with col2:
        st.metric("🥩 Protein", f"{total_pro:.1f} g", f"Sisa {target_protein - total_pro:.1f}" if total_pro < target_protein else "✅")
    with col3:
        st.metric("🍚 Karbohidrat", f"{total_kar:.1f} g", f"Sisa {target_karbo - total_kar:.1f}" if total_kar < target_karbo else "✅")
    with col4:
        st.metric("🧈 Lemak", f"{total_lem:.1f} g", f"Sisa {target_lemak - total_lem:.1f}" if total_lem < target_lemak else "✅")
    with col5:
        st.metric("🌾 Serat", f"{total_ser:.1f} g", f"Sisa {target_serat - total_ser:.1f}" if total_ser < target_serat else "✅")

    st.markdown("### 📊 Progress Harian")
    col_a, col_b = st.columns(2)

    def progress_bar(label, current, target, emoji=""):
        pct = min(current / target, 1.0) if target > 0 else 0
        color = "🟢" if pct >= 0.9 else ("🟡" if pct >= 0.5 else "🔴")
        st.markdown(f"**{emoji} {label}** — {current:.0f} / {target} ({pct*100:.0f}%) {color}")
        st.progress(pct)

    with col_a:
        progress_bar("Kalori", total_kal, target_kalori, "🔥")
        progress_bar("Protein", total_pro, target_protein, "🥩")
        progress_bar("Serat", total_ser, target_serat, "🌾")
    with col_b:
        progress_bar("Karbohidrat", total_kar, target_karbo, "🍚")
        progress_bar("Lemak", total_lem, target_lemak, "🧈")

        # Calorie balance pie-style breakdown
        if total_kal > 0:
            st.markdown("**📐 Distribusi Makronutrien**")
            cal_from_pro = total_pro * 4
            cal_from_kar = total_kar * 4
            cal_from_lem = total_lem * 9
            total_macro_cal = cal_from_pro + cal_from_kar + cal_from_lem
            if total_macro_cal > 0:
                st.markdown(f"- Protein: {cal_from_pro/total_macro_cal*100:.0f}%")
                st.markdown(f"- Karbohidrat: {cal_from_kar/total_macro_cal*100:.0f}%")
                st.markdown(f"- Lemak: {cal_from_lem/total_macro_cal*100:.0f}%")

    # Today's entry list
    if today_entries:
        st.markdown("### 🗒️ Daftar Makanan Hari Ini")
        for i, e in enumerate(today_entries):
            waktu_label = e.get("waktu", "")
            with st.expander(f"{waktu_label}  ·  **{e['nama']}** — {e['kalori']} kkal", expanded=False):
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.markdown(f"**Kalori:** {e['kalori']} kkal")
                c2.markdown(f"**Protein:** {e['protein']} g")
                c3.markdown(f"**Karbo:** {e['karbohidrat']} g")
                c4.markdown(f"**Lemak:** {e['lemak']} g")
                c5.markdown(f"**Serat:** {e['serat']} g")
                if st.button(f"🗑️ Hapus", key=f"del_{today_str}_{i}"):
                    data["entries"][today_str].pop(i)
                    save_data(data)
                    st.rerun()
    else:
        st.info("Belum ada makanan yang dicatat hari ini. Mulai tambahkan di tab **➕ Tambah Asupan**!")

# ──────────────────────────────────────────────
# TAB 2: TAMBAH ASUPAN
# ──────────────────────────────────────────────
with tab_tambah:
    st.markdown("### ➕ Catat Asupan Makanan")

    mode = st.radio("Metode input:", ["Pilih dari database", "Input manual"], horizontal=True)

    waktu = st.selectbox("Waktu makan", ["🌅 Sarapan", "☀️ Makan Siang", "🌆 Makan Malam", "🍪 Camilan"])

    if mode == "Pilih dari database":
        food_names = [f["nama"] for f in all_foods]
        selected = st.selectbox("Pilih makanan:", food_names)
        porsi = st.number_input("Jumlah porsi", min_value=0.25, max_value=10.0, value=1.0, step=0.25)

        food = next(f for f in all_foods if f["nama"] == selected)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"#### 📋 Detail Nutrisi ({porsi}x porsi)")
        pc1, pc2, pc3, pc4, pc5 = st.columns(5)
        pc1.metric("Kalori", f"{food['kalori'] * porsi:.0f}")
        pc2.metric("Protein", f"{food['protein'] * porsi:.1f} g")
        pc3.metric("Karbo", f"{food['karbohidrat'] * porsi:.1f} g")
        pc4.metric("Lemak", f"{food['lemak'] * porsi:.1f} g")
        pc5.metric("Serat", f"{food['serat'] * porsi:.1f} g")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✅ Tambahkan ke catatan", key="add_db", use_container_width=True):
            entry = {
                "nama": f"{food['nama']} x{porsi}",
                "kalori": round(food["kalori"] * porsi, 1),
                "protein": round(food["protein"] * porsi, 2),
                "karbohidrat": round(food["karbohidrat"] * porsi, 2),
                "lemak": round(food["lemak"] * porsi, 2),
                "serat": round(food["serat"] * porsi, 2),
                "waktu": waktu,
            }
            data.setdefault("entries", {}).setdefault(today_str, []).append(entry)
            save_data(data)
            st.success(f"✅ **{entry['nama']}** berhasil ditambahkan!")
            st.rerun()

    else:  # Manual
        nama_makanan = st.text_input("Nama makanan", placeholder="Contoh: Nasi Goreng Spesial")
        mc1, mc2 = st.columns(2)
        with mc1:
            m_kalori = st.number_input("Kalori (kkal)", min_value=0, max_value=5000, value=0, step=10)
            m_protein = st.number_input("Protein (g)", min_value=0.0, max_value=500.0, value=0.0, step=0.5)
            m_serat = st.number_input("Serat (g)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
        with mc2:
            m_karbo = st.number_input("Karbohidrat (g)", min_value=0.0, max_value=800.0, value=0.0, step=0.5)
            m_lemak = st.number_input("Lemak (g)", min_value=0.0, max_value=300.0, value=0.0, step=0.5)

        col_save_1, col_save_2 = st.columns(2)
        with col_save_1:
            if st.button("✅ Tambahkan", key="add_manual", use_container_width=True):
                if nama_makanan.strip():
                    entry = {
                        "nama": nama_makanan.strip(),
                        "kalori": m_kalori,
                        "protein": m_protein,
                        "karbohidrat": m_karbo,
                        "lemak": m_lemak,
                        "serat": m_serat,
                        "waktu": waktu,
                    }
                    data.setdefault("entries", {}).setdefault(today_str, []).append(entry)
                    save_data(data)
                    st.success(f"✅ **{nama_makanan}** berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.warning("⚠️ Nama makanan tidak boleh kosong.")

        with col_save_2:
            if st.button("💾 Simpan ke Database Makanan", key="save_custom", use_container_width=True):
                if nama_makanan.strip():
                    custom = {
                        "nama": nama_makanan.strip(),
                        "kalori": m_kalori,
                        "protein": m_protein,
                        "karbohidrat": m_karbo,
                        "lemak": m_lemak,
                        "serat": m_serat,
                    }
                    data.setdefault("custom_foods", []).append(custom)
                    save_data(data)
                    st.success(f"💾 **{nama_makanan}** tersimpan di database!")
                    st.rerun()
                else:
                    st.warning("⚠️ Nama makanan tidak boleh kosong.")

# ──────────────────────────────────────────────
# TAB 3: DATABASE MAKANAN
# ──────────────────────────────────────────────
with tab_database:
    st.markdown("### 🍎 Database Makanan")

    search = st.text_input("🔍 Cari makanan...", placeholder="Ketik nama makanan")

    filtered = [f for f in all_foods if search.lower() in f["nama"].lower()] if search else all_foods

    if filtered:
        # Show as table
        import pandas as pd
        df = pd.DataFrame(filtered)
        df.columns = ["Nama", "Kalori (kkal)", "Protein (g)", "Karbohidrat (g)", "Lemak (g)", "Serat (g)"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Makanan tidak ditemukan.")

    # Custom food management
    custom_foods = data.get("custom_foods", [])
    if custom_foods:
        st.divider()
        st.markdown("### 📝 Makanan Custom Anda")
        for i, cf in enumerate(custom_foods):
            col_cf, col_del = st.columns([5, 1])
            col_cf.markdown(f"**{cf['nama']}** — {cf['kalori']} kkal | P: {cf['protein']}g | K: {cf['karbohidrat']}g | L: {cf['lemak']}g | S: {cf['serat']}g")
            if col_del.button("🗑️", key=f"del_cf_{i}"):
                data["custom_foods"].pop(i)
                save_data(data)
                st.rerun()

# ──────────────────────────────────────────────
# TAB 4: RIWAYAT
# ──────────────────────────────────────────────
with tab_riwayat:
    st.markdown("### 📅 Riwayat Asupan")

    entries = data.get("entries", {})
    if entries:
        dates_sorted = sorted(entries.keys(), reverse=True)

        # Summary chart (last 7 days)
        last_7 = dates_sorted[:7]
        if last_7:
            st.markdown("#### 📈 Kalori 7 Hari Terakhir")
            import pandas as pd
            chart_data = []
            for d in reversed(last_7):
                day_entries = entries[d]
                chart_data.append({
                    "Tanggal": d,
                    "Kalori": sum(e["kalori"] for e in day_entries),
                    "Target": target_kalori,
                })
            chart_df = pd.DataFrame(chart_data).set_index("Tanggal")
            st.line_chart(chart_df, color=["#818cf8", "#f472b6"])

            # Macro breakdown per day
            st.markdown("#### 📊 Ringkasan Nutrisi per Hari")
            summary_data = []
            for d in reversed(last_7):
                day_entries = entries[d]
                summary_data.append({
                    "Tanggal": d,
                    "Kalori": sum(e["kalori"] for e in day_entries),
                    "Protein (g)": round(sum(e["protein"] for e in day_entries), 1),
                    "Karbo (g)": round(sum(e["karbohidrat"] for e in day_entries), 1),
                    "Lemak (g)": round(sum(e["lemak"] for e in day_entries), 1),
                    "Serat (g)": round(sum(e["serat"] for e in day_entries), 1),
                })
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.divider()

        # Detailed per-day log
        selected_date = st.selectbox("Pilih tanggal:", dates_sorted)
        if selected_date:
            day_data = entries[selected_date]
            st.markdown(f"#### Catatan — {selected_date}")
            for i, e in enumerate(day_data):
                with st.expander(f"{e.get('waktu', '')}  ·  **{e['nama']}** — {e['kalori']} kkal"):
                    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
                    rc1.markdown(f"**Kalori:** {e['kalori']}")
                    rc2.markdown(f"**Protein:** {e['protein']} g")
                    rc3.markdown(f"**Karbo:** {e['karbohidrat']} g")
                    rc4.markdown(f"**Lemak:** {e['lemak']} g")
                    rc5.markdown(f"**Serat:** {e['serat']} g")
                    if st.button("🗑️ Hapus", key=f"del_hist_{selected_date}_{i}"):
                        data["entries"][selected_date].pop(i)
                        if not data["entries"][selected_date]:
                            del data["entries"][selected_date]
                        save_data(data)
                        st.rerun()

            # Clear entire day
            if st.button(f"🗑️ Hapus semua catatan tanggal {selected_date}", use_container_width=True):
                del data["entries"][selected_date]
                save_data(data)
                st.rerun()
    else:
        st.info("Belum ada riwayat. Mulai catat asupan makananmu!")

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:13px;'>"
    "🥗 <b>NutriTrack</b> — Aplikasi Manajemen Nutrisi Harian &nbsp;|&nbsp; "
    "Dibuat dengan ❤️ menggunakan Streamlit"
    "</div>",
    unsafe_allow_html=True
)
