import streamlit as st
import os
from datetime import datetime
import json
import bcrypt
import sys
import os

# Projenin ana dizinini Python'ın yoluna ekle
# Bu, 'scrape_data' gibi kök dizindeki modülleri bulmasını sağlar.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import streamlit as st
from core.web_search import duckduckgo_search

# ... dosyanın geri kalanı ...
# This comment is added to force Streamlit to clear its cache.

from config.settings import APP_TITLE, APP_ICON
from config.database import init_db # Import init_db
from components.sidebar import create_sidebar
from components.image_upload import image_upload_component
from components.analysis_display import analysis_display_component
from core.disease_analyzer import DiseaseAnalyzer
from core.recommendation_engine import RecommendationEngine
from services.database_service import DatabaseService
from services.image_service import ImageService
from models.analysis import Analysis
from models.user import User
from duckduckgo_search import DDGS # Buradan DDGS'i import ediyoruz

# --- Page Configuration ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Services ---
@st.cache_resource
def get_database_service():
    init_db()
    return DatabaseService()

@st.cache_resource
def get_disease_analyzer():
    return DiseaseAnalyzer()

@st.cache_resource
def get_recommendation_engine():
    return RecommendationEngine()

@st.cache_resource
def get_image_service():
    return ImageService()

db_service = get_database_service()
disease_analyzer = get_disease_analyzer()
recommendation_engine = get_recommendation_engine()
image_service = get_image_service()

# --- Session State Management ---
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

if 'current_recommendations' not in st.session_state:
    st.session_state.current_recommendations = []

if 'raw_gemini_recommendation_response' not in st.session_state:
    st.session_state.raw_gemini_recommendation_response = None

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user' not in st.session_state:
    st.session_state.user = None

# New function to perform web search using the tool
@st.cache_data(ttl=3600) # Cache results for 1 hour
def perform_web_search(query: str):
    # Artık mock sonuçları veya duckduckgo_search içindeki try-except bloklarına gerek yok,
    # çünkü bu mantık core/web_search.py'ye taşındı.
    # Sadece yeni oluşturduğumuz fonksiyonu çağırıyoruz:
    return duckduckgo_search(query)

def register_user(name, email, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(name=name, email=email, password_hash=hashed_password)
    user_id = db_service.add_user(new_user)
    if user_id:
        st.success("Kayıt başarılı! Lütfen giriş yapın.")
        st.rerun()
        return True
    else:
        st.error("Kayıt başarısız. Bu e-posta zaten kullanılıyor olabilir.")
        return False

def login_user(email, password):
    user = db_service.get_user_by_email(email)
    if user and user.password_hash and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.user_id = user.id
        st.success(f"Hoş geldiniz, {user.name}!")
        st.rerun()
        return True
    else:
        st.error("Geçersiz e-posta veya şifre.")
        return False

def show_login_page():
    st.title(f"{APP_ICON} {APP_TITLE} - Giriş / Kayıt")
    login_tab, register_tab = st.tabs(["Giriş Yap", "Kayıt Ol"])

    with login_tab:
        st.subheader("Giriş Yap")
        login_email = st.text_input("E-posta", key="login_email")
        login_password = st.text_input("Şifre", type="password", key="login_password")
        if st.button("Giriş Yap", key="login_button"):
            if login_email and login_password:
                login_user(login_email, login_password)
            else:
                st.warning("Lütfen e-posta ve şifrenizi girin.")

    with register_tab:
        st.subheader("Kayıt Ol")
        register_name = st.text_input("Adınız", key="register_name")
        register_email = st.text_input("E-posta", key="register_email")
        register_password = st.text_input("Şifre", type="password", key="register_password")
        confirm_password = st.text_input("Şifreyi Onayla", type="password", key="confirm_password")

        if st.button("Kayıt Ol", key="register_button"):
            if not (register_name and register_email and register_password and confirm_password):
                st.warning("Lütfen tüm alanları doldurun.")
            elif register_password != confirm_password:
                st.error("Şifreler uyuşmuyor.")
            else:
                register_user(register_name, register_email, register_password)

def main():
    if not st.session_state.logged_in:
        show_login_page()
        return

    st.sidebar.markdown(f"**Hoş geldiniz, {st.session_state.user.name}!**")
    if st.sidebar.button("Çıkış Yap", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_id = None
        st.session_state.current_analysis = None
        st.session_state.current_recommendations = []
        st.session_state.raw_gemini_recommendation_response = None
        st.rerun()
        return

    st.title(f"{APP_ICON} {APP_TITLE}")

    page = create_sidebar()

    if page == "Dashboard":
        st.header("📊 Dashboard")
        st.write("Üzüm bağlarınızın sağlığını takip etmek için ana kontrol paneliniz.")
        dashboard_stats = db_service.get_dashboard_stats(st.session_state.user_id)
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Toplam Analiz Sayısı", dashboard_stats["total_analyses"])
        with col_stats2:
            st.metric("Tespit Edilen Farklı Hastalık", dashboard_stats["unique_diseases"])
        with col_stats3:
            st.metric("Aktif Takipler", dashboard_stats["active_follow_ups"])

        st.markdown("--- ")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Son Analizler")
            recent_analyses = db_service.get_analyses_by_user_id(st.session_state.user_id)
            if recent_analyses:
                for i, analysis in enumerate(recent_analyses[:5]):
                    display_date = analysis.analysis_date.strftime('%Y-%m-%d %H:%M') if analysis.analysis_date else "Bilinmiyor"
                    st.markdown(f"**Analiz #{len(recent_analyses) - i}: {display_date}**")
                    st.write(f"Tespit Edilen Hastalık: {analysis.disease_detected}")
                    st.write(f"Güven Skoru: {analysis.confidence_score:.2f}")
                    st.markdown("--- ")
            else:
                st.info("Henüz bir analiz yapılmadı.")

        with col2:
            st.subheader("Aktif Takipler")
            st.info(f"Toplam aktif takip notu: {dashboard_stats['active_follow_ups']}. Detaylar için 'Geçmiş Analizler' sayfasına gidin.")

        st.markdown("--- ")
        st.subheader("📈 Hastalık Trend Grafikleri")
        st.info("Hastalık trend grafikleri ve genel istatistikler burada görüntülenecektir.")

    elif page == "Image Analysis":
        st.header("📷 Görüntü Analizi")
        image_data, image_name = image_upload_component()

        if st.button("Analizi Başlat") and image_data is not None:
            with st.spinner("Görüntü analiz ediliyor..."):
                try:
                    processed_image_data = image_service.resize_image(image_data, max_size=(1024, 1024))
                    processed_image_data = image_service.convert_to_jpeg(processed_image_data)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_name.replace(' ', '_') if image_name else 'uploaded_image.jpeg'}"
                    saved_image_path = image_service.save_image(processed_image_data, unique_filename)
                    analysis_result, raw_gemini_analysis_response = disease_analyzer.analyze_grape_image(processed_image_data)
                    new_analysis = Analysis(
                        user_id=st.session_state.user_id,
                        image_path=saved_image_path,
                        disease_detected=str(analysis_result.get('disease_detected', "Unknown")),
                        confidence_score=float(analysis_result.get('confidence_score', 0.0)),
                        gemini_response=raw_gemini_analysis_response
                    )
                    analysis_id = db_service.add_analysis(new_analysis)
                    if analysis_id is not None:
                        new_analysis.id = analysis_id
                        st.session_state.current_analysis = new_analysis
                        recommendations_list, raw_gemini_recommendation_response = recommendation_engine.generate_recommendations(new_analysis)
                        for rec in recommendations_list:
                            rec.analysis_id = analysis_id
                            db_service.add_recommendation(rec)
                        st.session_state.current_recommendations = recommendations_list
                        st.session_state.raw_gemini_recommendation_response = raw_gemini_recommendation_response
                        st.success("Analiz tamamlandı!")
                        if st.session_state.raw_gemini_recommendation_response:
                            st.subheader("📝 AI Açıklaması (Türkçe)")
                            st.info(st.session_state.raw_gemini_recommendation_response)
                    else:
                        st.error("Analiz veritabanına kaydedilemedi.")
                except Exception as e:
                    st.error(f"Analiz sırasında bir hata oluştu: {e}")
                    st.session_state.current_analysis = None
                    st.session_state.current_recommendations = []

        if st.session_state.current_analysis:
            analysis_display_component(st.session_state.current_analysis, st.session_state.current_recommendations)
        elif image_data is None:
            st.info("Lütfen bir görüntü yükleyin veya kamera ile çekin.")

    elif page == "History":
        st.header("📋 Geçmiş Analizler")
        if st.session_state.user_id is not None:
            user_analyses = db_service.get_analyses_by_user_id(st.session_state.user_id)
        else:
            user_analyses = []
            st.warning("Kullanıcı ID'si bulunamadı. Lütfen giriş yapın.")

        if user_analyses:
            st.write("Son analizleriniz:")
            for i, analysis in enumerate(user_analyses):
                recommendations = db_service.get_recommendations_by_analysis_id(analysis.id) if analysis.id else []
                display_date = analysis.analysis_date.strftime('%Y-%m-%d %H:%M') if analysis.analysis_date else "Bilinmiyor"
                with st.expander(f"Analiz #{len(user_analyses) - i}: {display_date} - {analysis.disease_detected}"):
                    analysis_display_component(analysis, recommendations)
                    if analysis.gemini_response:
                        st.subheader("📝 AI Açıklaması (Türkçe)")
                        st.info(analysis.gemini_response)

                    # Add a delete button for the analysis
                    if st.button(f"Analizi Sil (ID: {analysis.id})", key=f"delete_analysis_{analysis.id}", type="secondary"):
                        if db_service.delete_analysis(analysis.id):
                            st.success(f"Analiz ID: {analysis.id} başarıyla silindi.")
                            st.session_state.current_analysis = None # Clear current analysis if it was deleted
                            st.rerun()
                        else:
                            st.error(f"Analiz ID: {analysis.id} silinirken bir hata oluştu.")
        else:
            st.info("Henüz bir analiz geçmişiniz bulunmamaktadır.")

    elif page == "Bilgi Bankası":
        from components.education import education_component
        education_component(perform_web_search)

    elif page == "Topluluk Forumu":
        from components.community_forum import community_forum_component
        community_forum_component(db_service, st.session_state.user_id)

    elif page == "Settings":
        st.header("⚙️ Ayarlar")
        st.write("Kullanıcı profilinizi ve uygulama ayarlarınızı buradan yönetin.")

        user_id = st.session_state.user_id
        current_user = db_service.get_user_by_id(user_id)

        if current_user:
            st.subheader("Profil Bilgileri")
            with st.form(key='profile_settings_form'):
                # Pre-fill with current user data
                default_name = current_user.name if current_user.name else ""
                default_email = current_user.email if current_user.email else ""
                default_phone = current_user.phone if current_user.phone else ""
                default_location = current_user.location if current_user.location else ""
                default_notifications = current_user.receive_email_notifications if current_user.receive_email_notifications is not None else True

                name = st.text_input("Adınız", value=default_name)
                email = st.text_input("E-posta", value=default_email)
                phone = st.text_input("Telefon Numarası (Opsiyonel)", value=default_phone)
                location = st.text_input("Konum (Opsiyonel)", value=default_location)
                receive_email_notifications = st.checkbox("E-posta Bildirimleri Al", value=default_notifications)

                submit_button = st.form_submit_button(label='Ayarları Kaydet')

                if submit_button:
                    # Update user in DB
                    success = db_service.update_user_settings(
                        user_id=user_id,
                        name=name,
                        email=email,
                        phone=phone,
                        location=location,
                        receive_email_notifications=receive_email_notifications
                    )

                    if success:
                        # Update session state with new data
                        st.session_state.user.name = name
                        st.session_state.user.email = email
                        st.session_state.user.phone = phone
                        st.session_state.user.location = location
                        st.session_state.user.receive_email_notifications = receive_email_notifications
                        st.success("Ayarlar başarıyla güncellendi!")
                        st.rerun()
                    else:
                        st.error("Ayarlar güncellenirken bir hata oluştu.")
        else:
            st.warning("Kullanıcı bilgileri yüklenemedi.")

if __name__ == "__main__":
    main()
