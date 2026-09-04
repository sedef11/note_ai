import os
import base64
import streamlit as st
from dotenv import load_dotenv
from google import genai
import database as db

# Veritabanını başlat
db.init_db()

st.set_page_config(
    page_title="Prompt Summarizer AI",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RESMİ BASE64 FORMATINA ÇEVİREN FONKSİYON ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

sakura_img_base64 = get_base64_image("assets/sakura.png")
sakura_bg_style = f"url('data:image/png;base64,{sakura_img_base64}')" if sakura_img_base64 else "none"

# --- SAKURA GRADİENT & İDEAL BOYUTLU DAL EFEKTİ CSS ---
st.markdown(f"""
<style>
    /* Arka Plan Gradient */
    .stApp {{
        background: linear-gradient(135deg, #fff0f3 0%, #ffccd5 50%, #fff0f5 100%);
        background-attachment: fixed;
    }}

    /* Üst Kısmın Yarısını Kaplayan ve Tam Görünen Sakura Dalı */
    .sakura-branch-top {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 260px;
        background-image: {sakura_bg_style};
        background-repeat: no-repeat;
        background-size: 550px;
        background-position: top right;
        pointer-events: none;
        z-index: 999999;
        opacity: 0.9;
        /* Beyaz arka planı yok edip pembe tonların kusursuz harmanlanmasını sağlar */
        mix-blend-mode: multiply; 
    }}

    /* Başlık ve Font Renkleri */
    h1, h2, h3, h4 {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #5c1d39 !important;
    }}

    /* Cam Efektli Kutular (Glassmorphism) */
    div[data-testid="stForm"], div.stPopover > button, div.element-container div.stMarkdown > div[style*="background"] {{
        background: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 182, 193, 0.5) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(255, 105, 180, 0.1) !important;
    }}

    /* Pembe Not Kutusu Stili */
    .pink-note-box {{
        background: rgba(255, 228, 225, 0.85);
        border-left: 5px solid #ff69b4;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: #4a2335;
        box-shadow: 0px 4px 10px rgba(255, 105, 180, 0.15);
    }}
    .pink-note-box strong {{
        color: #d81b60;
    }}
    .pink-note-box small {{
        color: #884466;
    }}

    /* Sözlük Kelime Kartı */
    .dict-card {{
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid #ffb6c1;
        border-radius: 14px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.1);
        transition: transform 0.2s;
    }}
    .dict-card:hover {{
        transform: translateY(-2px);
    }}

    /* Sidebar Cam Efekti */
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 240, 243, 0.8) !important;
        backdrop-filter: blur(8px) !important;
        border-right: 1px solid #ffccd5;
    }}

    /* Tab Tasarımları */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px;
        padding: 8px 16px;
        background-color: rgba(255, 255, 255, 0.5);
        color: #884466;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #ff69b4 !important;
        color: white !important;
        font-weight: bold;
    }}

    /* Sidebar İpucu Kutusu */
    section[data-testid="stSidebar"] div[data-testid="stAlert"] {{
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 12px !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stAlert"] * {{
        color: #ffffff !important;
    }}

    /* Buton Tasarımları */
    .stApp button[data-testid="stBaseButton-primary"],
    .stApp button[kind="primary"],
    .stApp button[type="submit"],
    div.stButton > button[type="primary"],
    button[kind="primary"] {{
        background: linear-gradient(135deg, #2b1020 0%, #121212 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 182, 193, 0.4) !important;
        font-weight: bold !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 15px rgba(92, 29, 57, 0.25) !important;
        transition: all 0.3s ease-in-out !important;
    }}

    .stApp button[data-testid="stBaseButton-primary"] *,
    .stApp button[kind="primary"] *,
    .stApp button[type="submit"] * {{
        color: #ffffff !important;
    }}

    .stApp button[data-testid="stBaseButton-primary"]:hover,
    .stApp button[kind="primary"]:hover,
    .stApp button[type="submit"]:hover {{
        background: linear-gradient(135deg, #4a1c35 0%, #1a1a1a 100%) !important;
        border-color: #ff69b4 !important;
        box-shadow: 0 0 15px rgba(255, 105, 180, 0.4) !important;
        transform: translateY(-1px);
    }}
</style>

<!-- SAKURA DALI KATMANI -->
<div class="sakura-branch-top"></div>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# --- 1. GİRİŞ / KAYIT EKRANI ---
if st.session_state.user is None:
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("<h1 style='text-align: center;'>✨ Prompt Summarizer AI</h1>", unsafe_allow_html=True)
        st.caption("<p style='text-align: center;'>Akıllı Özetleme Asistanı</p>", unsafe_allow_html=True)
        st.write("")
        
        tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

        with tab1:
            st.subheader("Giriş Yap")
            login_username = st.text_input("Kullanıcı Adı", key="login_user")
            login_password = st.text_input("Şifre", type="password", key="login_pass")
            st.write("")
            if st.button("Giriş Yap", use_container_width=True, type="primary"):
                user = db.login_user(login_username, login_password)
                if user:
                    st.session_state.user = user
                    st.success(f"Hoş geldin {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı!")

        with tab2:
            st.subheader("Yeni Hesap Oluştur")
            reg_fullname = st.text_input("Ad Soyad", key="reg_name")
            reg_username = st.text_input("Kullanıcı Adı", key="reg_user")
            reg_password = st.text_input("Şifre", type="password", key="reg_pass")
            st.write("")
            if st.button("Kayıt Ol", use_container_width=True, type="primary"):
                if reg_fullname and reg_username and reg_password:
                    success, msg = db.register_user(reg_fullname, reg_username, reg_password)
                    if success:
                        st.success(msg)
                    else:
                        st.warning(msg)
                else:
                    st.error("Lütfen tüm alanları doldurun.")

# --- 2. ANA UYGULAMA ---
else:
    current_user = st.session_state.user

    # --- Sol Yan Menü ---
    with st.sidebar:
        st.title("🌸 Workspace")
        st.markdown(f"**Kullanıcı:** {current_user['full_name']}")
        st.caption(f"@{current_user['username']}")
        
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.user = None
            if "last_result" in st.session_state:
                del st.session_state.last_result
            st.rerun()

        st.divider()
        st.header("⚙️ Özet Ayarları")
        summary_length = st.select_slider(
            "Özet Detay Seviyesi:",
            options=["Çok Kısa", "Dengeli", "Detaylı"],
            value="Dengeli"
        )
        st.info("💡 **İpucu:** Çıktı metninden istediğiniz yerleri kopyalayıp aşağıdaki kutuya yapıştırarak not alabilirsiniz.")

    tab_main, tab_history, tab_dict = st.tabs(["🚀 Çalışma Alanı", "💖 Geçmiş & Notlarım", "📖 Sözlüğüm"])

    # --- TAB 1: ÇALIŞMA ALANI ---
    with tab_main:
        st.subheader("✨ Soru Sor / Prompt Gir & Not Al")
        
        col_in, col_out = st.columns(2, gap="medium")

        with col_in:
            st.markdown("#### 📥 Prompt / Soru Girin")
            user_input = st.text_area(
                "Ders konusu, soru veya özetlenmesini istediğiniz metin:",
                height=320,
                placeholder="Örn: Yapay zeka ve makine öğrenmesi arasındaki fark nedir? Detaylı açıkla..."
            )
            btn_generate = st.button("⚡ Cevapla ve Özeti Çıkar", use_container_width=True, type="primary")

        with col_out:
            st.markdown("#### 📌 Yapay Zeka Çıktısı & Özet")
            
            if btn_generate:
                if not api_key:
                    st.error("API Anahtarı (.env dosyasında GEMINI_API_KEY) bulunamadı!")
                elif not user_input.strip():
                    st.warning("Lütfen bir soru veya prompt girin.")
                else:
                    with st.spinner("Gemini ders notlarınızı ve cevabı hazırlıyor..."):
                        try:
                            client = genai.Client(api_key=api_key)
                            
                            system_instruction = f"""
                            Sen öğrenmeyi kolaylaştıran uzman bir eğitim asistanısın. Kullanıcının girdiği promptu/soruyu analiz et ve yanıtını İKİ KISIM halinde Türkçe olarak ver:

                            ### 🤖 Yapay Zeka Yanıtı
                            (Kullanıcının sorusuna veya konusuna detaylı, öğretici ve net bir cevap ver.)

                            ---
                            ### 📌 Girdiğiniz Promptun Özeti
                            (Kullanıcının girdiği promptu/soruyu '{summary_length}' detay seviyesinde kısa ve öz olarak özetle.)
                            """

                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[system_instruction, user_input]
                            )
                            
                            summary_result = response.text
                            st.session_state.last_result = summary_result
                            
                            # Veritabanına kaydet
                            saved_id = db.save_summary(current_user["id"], user_input, summary_result)
                            st.session_state.last_summary_id = saved_id

                        except Exception as e:
                            st.error(f"Hata oluştu: {e}")
            
            # Üretilen sonucu göster
            if "last_result" in st.session_state and st.session_state.last_result:
                
                st.markdown(st.session_state.last_result)
                st.divider()
                
                current_summary_id = st.session_state.get("last_summary_id")

                # --- NOT EKLEME ALANI ---
                st.markdown("### 📝 Not Al")
                
                with st.form(key="pink_note_form", clear_on_submit=True):
                    note_text_input = st.text_area(
                        "Kaydetmek istediğiniz not:",
                        height=100,
                        placeholder="Kaydetmek istediğiniz notu buraya yazabilirsiniz..."
                    )
                    submit_note = st.form_submit_button("💖 Notlarıma Kaydet", use_container_width=True)
                    
                    if submit_note:
                        if note_text_input.strip():
                            db.add_note(current_summary_id, current_user["id"], note_text_input.strip())
                            st.success("🌸 Notunuz veritabanına başarıyla kaydedildi!")
                            st.rerun()
                        else:
                            st.warning("Boş not eklenemez.")
                
                # Bu yanıta ait eklenen notları göster
                if current_summary_id:
                    existing_notes = db.get_notes_by_summary(current_summary_id)
                    if existing_notes:
                        st.write("")
                        st.markdown("##### 💖 Bu Cevaptan Alınan Notlar:")
                        for n in existing_notes:
                            st.markdown(f"""
                            <div class="pink-note-box">
                                🖊️ <strong>"{n['note_text']}"</strong>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("Sol tarafa promptunuzu veya ders sorunuzu girip **Cevapla ve Özeti Çıkar** butonuna bastığınızda yapay zeka cevabı ve özeti burada görünecektir.")

    # --- TAB 2: GEÇMİŞ VE NOTLAR ---
    with tab_history:
        st.subheader("📜 Ders Geçmişi ve Kaydedilen Notlar")
        history = db.get_user_history(current_user["id"])

        if not history:
            st.info("Henüz geçmiş bir soru veya özet kaydınız bulunmuyor.")
        else:
            for item in history:
                with st.expander(f"🕒 {item['created_at']} | 💬 Prompt: {item['original_text'][:60]}..."):
                    c1, c2 = st.columns([2, 1])
                    
                    with c1:
                        st.markdown("**Sorduğunuz Prompt / Soru:**")
                        st.info(item['original_text'])
                        st.markdown("**Yapay Zeka Yanıtı ve Özeti:**")
                        st.markdown(item['summary_text'])
                    
                    with c2:
                        st.markdown("### 💖 Notlar")
                        
                        notes = db.get_notes_by_summary(item['id'])
                        
                        if notes:
                            for n in notes:
                                st.markdown(f"""
                                <div class="pink-note-box">
                                    🖊️ <strong>"{n['note_text']}"</strong><br>
                                    <small>📅 {n['created_at']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.caption("Bu cevap için henüz not alınmamış.")

    # --- TAB 3: SÖZLÜĞÜM (YENİ) ---
    with tab_dict:
        st.subheader("📖 Dil Öğrenme Sözlüğüm")
        st.markdown("Yeni öğrendiğin kelimeleri, anlamlarını ve hangi dilde olduklarını buraya kaydederek kendi kelime arşivini oluşturabilirsin!")
        
        col_add, col_list = st.columns([1, 1.5], gap="large")

        with col_add:
            st.markdown("#### ✍️ Yeni Kelime Ekle")
            with st.form(key="dict_form", clear_on_submit=True):
                new_word = st.text_input("Kelime (Örn: Resilient)")
                new_meaning = st.text_input("Anlamı / Türkçe Karşılığı (Örn: Dayanıklı, dirençli)")
                new_lang = st.selectbox("Dil", ["İngilizce", "Almanca", "Fransızca", "İspanyolca", "Diğer"])
                
                submit_word = st.form_submit_button("🌸 Sözlüğe Ekle", use_container_width=True)
                
                if submit_word:
                    if new_word.strip() and new_meaning.strip():
                        db.add_dictionary_word(current_user["id"], new_word.strip(), new_meaning.strip(), new_lang)
                        st.success(f"✨ '{new_word}' sözlüğünüze eklendi!")
                        st.rerun()
                    else:
                        st.warning("Lütfen kelime ve anlam alanlarını doldurun.")

        with col_list:
            st.markdown("#### 📚 Kayıtlı Kelimelerim")
            
            # Arama filtresi
            search_query = st.text_input("🔍 Kelimelerde Ara:", placeholder="Kelime veya anlam ara...")
            
            user_words = db.get_user_dictionary(current_user["id"])
            
            # Filtreleme
            if search_query:
                user_words = [w for w in user_words if search_query.lower() in w['word'].lower() or search_query.lower() in w['meaning'].lower()]

            if not user_words:
                st.info("Henüz sözlüğünüze eklenmiş bir kelime bulunmuyor.")
            else:
                for w in user_words:
                    col_w_info, col_w_del = st.columns([4, 1])
                    with col_w_info:
                        st.markdown(f"""
                        <div class="dict-card">
                            <span style="background: #ff69b4; color: white; padding: 2px 8px; border-radius: 8px; font-size: 11px; font-weight: bold;">{w['language']}</span>
                            <h4 style="margin: 6px 0 2px 0; color: #5c1d39 !important;">{w['word']}</h4>
                            <p style="margin: 0; color: #4a2335;">📌 <strong>{w['meaning']}</strong></p>
                            <small style="color: #884466;">📅 {w['created_at']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_w_del:
                        st.write("")
                        st.write("")
                        if st.button("🗑️", key=f"del_word_{w['id']}", help="Kelimeyi sil"):
                            db.delete_dictionary_word(w['id'])
                            st.rerun()