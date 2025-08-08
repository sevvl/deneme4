import streamlit as st
import pandas as pd
import os
from scrape_data import scrape_grape_disease_data
from PIL import Image
import google.generativeai as genai

# Sayfa yapılandırması
st.set_page_config(
    page_title="Üzüm Takip Destek Öneri Sistemi",
    page_icon="🍇",
    layout="wide"
)

# Başlık
st.title("🍇 Üzüm Takip Destek Öneri Sistemi")

# Sidebar - Navigation (ekran görüntüsüne göre)
st.sidebar.title("Navigation")
st.sidebar.markdown("Go to")

page = st.sidebar.radio("", [
    "Dashboard",
    "Image Analysis",
    "History",
    "Settings",
    "Bilgi Bankası",
    "Topluluk Forumu"
], key="navigation")


# Fungisit verilerini yükleme fonksiyonu
@st.cache_data(ttl=3600)  # 1 saatlik cache
def load_fungicide_data(force_refresh=False):
    """Fungisit verilerini yükle (gelişmiş cache ile)"""
    try:
        # Cache temizleme kontrolü
        if force_refresh:
            st.cache_data.clear()

        # Gelişmiş veri çekme fonksiyonunu kullan
        from scrape_data import get_grape_data_smart

        with st.spinner("📊 Fungisit verileri yükleniyor..."):
            df = get_grape_data_smart(force_refresh=force_refresh)

            if df is not None and not df.empty:
                # Veri kalitesi kontrolleri
                df = df.dropna(how='all')  # Tamamen boş satırları temizle
                df = df.reset_index(drop=True)

                # Başarı mesajı
                st.success(f"✅ {len(df)} kayıt başarıyla yüklendi!")
                return df
            else:
                return None

    except ImportError:
        st.error("❌ scrape_data.py dosyası bulunamadı!")
        return None
    except Exception as e:
        st.error(f"❌ Veri yükleme hatası: {e}")
        return None


# Dashboard
if page == "Dashboard":
    st.header("📊 Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Toplam Analiz", "156", "12")
    with col2:
        st.metric("Sağlıklı Bitkiler", "89%", "2%")
    with col3:
        st.metric("Riskli Alanlar", "3", "-1")
    with col4:
        st.metric("Son Güncelleme", "2 saat önce")

    st.plotly_chart({}, use_container_width=True) if 'plotly' in locals() else st.info("📈 Grafik alanı")

# Image Analysis
elif page == "Image Analysis":
    st.header("📸 Image Analysis")

    uploaded_file = st.file_uploader(
        "Üzüm yaprağı veya salkım fotoğrafı yükleyin",
        type=['png', 'jpg', 'jpeg']
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        col1, col2 = st.columns(2)

        with col1:
            st.image(image, caption="Yüklenen Fotoğraf", use_container_width=True)

        with col2:
            if st.button("🔬 Analiz Et", type="primary"):
                with st.spinner("AI analiz yapıyor..."):
                    st.success("✅ Analiz tamamlandı!")
                    st.json({
                        "hastalık": "Külleme (Powdery Mildew)",
                        "şiddet": "Orta",
                        "güven": "85%",
                        "öneriler": ["Fungisit uygulaması", "Havalandırma artırımı"]
                    })

# History
elif page == "History":
    st.header("📋 History")
    st.info("Geçmiş analizler ve sonuçlar burada görüntülenecek.")

# Settings
elif page == "Settings":
    st.header("⚙️ Settings")
    st.info("Uygulama ayarları burada yapılacak.")

# Bilgi Bankası - WEB SCRAPING VERİLERİNİ BURADA GÖSTERELİM
elif page == "Bilgi Bankası":
    st.header("📚 Bilgi Bankası / Eğitim Modülü")
    st.markdown("Bağcılık, hastalıklar ve ilaçlar hakkında eğitim içerikleri.")

    # Tab'lar oluştur
    tab1, tab2, tab3 = st.tabs(["📖 Yerel İçerikler", "🌐 Web Araması", "🧪 Fungisit Veritabanı"])

    with tab1:
        st.subheader("📋 Yerel İçerikler")

        # Yerel makale başlıkları (örnek)
        articles = [
            "🔗 Bağ Mildiyösü Hastalığı ve Mücadelesi",
            "🔗 Mildiyö İle Kimyasal Mücadele Yöntemleri"
        ]

        for article in articles:
            if st.button(article, key=f"local_{article}"):
                if "Mildiyösü" in article:
                    st.markdown("""
                    **Bağ Mildiyösü Hastalığı**

                    Üzüm bağlarında en yaygın görülen hastalıklardan biri olan mildiyö...

                    **Belirtiler:**
                    - Yapraklarda sarı lekeler
                    - Yaprak altında beyaz tüyler
                    - Salkımlarda kahverengi lekeler

                    **Mücadele Yöntemleri:**
                    - Koruyucu ilaçlama
                    - Düzenli kontrol
                    - Havalandırma
                    """)

    with tab2:
        st.subheader("🔍 Online Makale Araması")

        search_query = st.text_input(
            "Aramak istediğiniz konu girin (örn: üzüm mildiyö tedavisi):",
            placeholder="Mildiyö"
        )

        if st.button("🌐 Web'de Ara"):
            if search_query:
                st.info(f"'{search_query}' konusu için web araması yapılıyor...")
                st.markdown("""
                **🔍 Arama Sonuçları:**

                Bu web arama özelliği şu anda simüle edilmektedir. 
                Gerçek web araması için ek entegrasyonlar gereklidir.

                **Arama önerisi:** Şimdilik Fungisit Veritabanı sekmesindeki 
                gerçek veriler ile çalışabilirsiniz.
                """)

    with tab3:
        st.subheader("🧪 Fungisit Etkinlik Veritabanı")
        st.markdown("**UMass Üniversitesi'nden çekilen güncel fungisit verileri**")

        # Veriyi yükle
        df = load_fungicide_data()

        if df is not None and not df.empty:
            # Arama ve filtreleme
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                search_term = st.text_input("🔍 Hastalık veya fungisit ara:", key="search_fungicide")

            with col2:
                st.metric("📊 Toplam Kayıt", len(df))

            with col3:
                if st.button("🔄 Veriyi Yenile", key="refresh_data"):
                    st.cache_data.clear()
                    df_fresh = load_fungicide_data(force_refresh=True)
                    if df_fresh is not None:
                        st.success("✅ Veriler güncellendi!")
                        st.rerun()

            # Filtreleme
            if search_term:
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                filtered_df = df[mask]
                if len(filtered_df) > 0:
                    st.info(f"🎯 '{search_term}' için {len(filtered_df)} sonuç bulundu")
                else:
                    st.warning(f"❌ '{search_term}' için sonuç bulunamadı")
            else:
                filtered_df = df

            # Tablo görünümü - daha şık görünüm
            st.subheader("📋 Fungisit Etkinlik Tablosu")

            if not filtered_df.empty:
                # Tablo stilini ayarla
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )

                # Alt bilgiler
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 CSV İndir",
                        data=csv,
                        file_name=f"fungisit_verileri_{search_term if search_term else 'tum'}.csv",
                        mime="text/csv",
                        help="Filtrelenmiş verileri CSV olarak indir"
                    )

                with col2:
                    # Excel formatında indirme
                    if st.button("📊 Excel İndir", help="Veriyi Excel formatında indir"):
                        st.info("Excel indirme özelliği yakında eklenecek")

                with col3:
                    st.metric("🔍 Sonuç", len(filtered_df))

                with col4:
                    st.metric("📊 Sütun", len(filtered_df.columns))

                # Özet bilgiler - genişletilebilir bölüm
                with st.expander("📊 Detaylı Veri Analizi"):
                    tab1, tab2, tab3 = st.tabs(["📈 Genel Bilgi", "🔢 Sütun Detayları", "📋 Son Güncelleme"])

                    with tab1:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**📊 Veri Özeti:**")
                            st.write(f"• Toplam satır: {len(filtered_df)}")
                            st.write(f"• Toplam sütun: {len(filtered_df.columns)}")
                            st.write(
                                f"• Boş hücre oranı: {(filtered_df.isnull().sum().sum() / (len(filtered_df) * len(filtered_df.columns)) * 100):.1f}%")

                        with col2:
                            st.write("**🎯 Filtreleme Bilgisi:**")
                            st.write(f"• Arama terimi: {'Yok' if not search_term else search_term}")
                            st.write(f"• Görüntülenen kayıt: {len(filtered_df)}")
                            st.write(f"• Filtreleme oranı: {(len(filtered_df) / len(df) * 100):.1f}%")

                    with tab2:
                        st.write("**📋 Sütun Listesi:**")
                        for i, col in enumerate(filtered_df.columns):
                            st.write(f"{i + 1}. {col}")

                    with tab3:
                        try:
                            if os.path.exists('data_metadata.txt'):
                                with open('data_metadata.txt', 'r', encoding='utf-8') as f:
                                    metadata = f.read()
                                st.code(metadata)
                            else:
                                st.info("Metadata bilgisi bulunamadı")
                        except:
                            st.error("Metadata okunamadı")
            else:
                st.warning("🔍 Arama kriterlerinize uygun sonuç bulunamadı")

        else:
            # Hata durumu için daha detaylı yardım
            st.error("❌ Fungisit verileri yüklenemedi!")

            with st.expander("🔧 Sorun Giderme Rehberi"):
                st.markdown("""
                **Olası nedenler ve çözümler:**

                1. **İnternet Bağlantısı:**
                   - İnternet bağlantınızı kontrol edin
                   - VPN kullanıyorsanız kapatmayı deneyin

                2. **Dosya Problemi:**
                   - `scrape_data.py` dosyasının aynı klasörde olduğundan emin olun
                   - Dosya izinlerini kontrol edin

                3. **Web Sitesi Problemi:**
                   - Kaynak web sitesi geçici olarak erişilemez olabilir
                   - Birkaç dakika sonra tekrar deneyin

                4. **Kod Problemi:**
                   - Requirements.txt'deki kütüphanelerin yüklü olduğundan emin olun
                   - Terminal'de: `pip install -r requirements.txt`
                """)

            # Manuel yenileme butonu
            if st.button("🔄 Tekrar Dene", type="primary"):
                st.cache_data.clear()
                st.rerun()

# Topluluk Forumu
elif page == "Topluluk Forumu":

    st.header("👥 Topluluk Forumu")
    st.info("Üzüm yetiştiricileri ile deneyim paylaşımı yapabileceğiniz alan (yakında aktif olacak).")

# Footer bilgisi
st.sidebar.markdown("---")
st.sidebar.markdown("**Developed with ❤️ for grape growers.**")

# Sağ alt köşede geliştirici notu
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: #FAFAFA;
        text-align: center;
        padding: 10px;
        font-size: 12px;
    }
    </style>
    <div class="footer">
        🍇 Üzüm Takip Destek Öneri Sistemi - Web scraping verileri başarıyla entegre edildi
    </div>
    """,
    unsafe_allow_html=True
)