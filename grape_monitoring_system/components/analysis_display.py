import streamlit as st
from models.analysis import Analysis
from models.recommendation import Recommendation
from components.recommendation_card import recommendation_card
from services.database_service import DatabaseService
from datetime import datetime
import json

db_service = DatabaseService()

def analysis_display_component(analysis: Analysis, recommendations: list[Recommendation]):
    st.header("🔬 Analiz Sonuçları")
    if analysis:
        st.subheader("Tespit Edilen Hastalık")
        if analysis.disease_detected and analysis.disease_detected != "Unknown":
            st.success(f"**{analysis.disease_detected}**")
            st.info(f"Güven Skoru: {analysis.confidence_score * 100:.2f}%")
            
            # Attempt to extract explanation from raw Gemini response if it's JSON
            explanation_from_json = None
            if analysis.gemini_response:
                try:
                    gemini_json = json.loads(analysis.gemini_response)
                    explanation_from_json = gemini_json.get('explanation')
                except json.JSONDecodeError:
                    pass # Not a valid JSON, will display raw response later

            if explanation_from_json:
                st.write(f"Açıklama: {explanation_from_json}")
            
        elif analysis.disease_detected == "Healthy":
            st.success("Hastalık belirtisi tespit edilmedi. Üzüm bitkiniz sağlıklı!")
            st.info(f"Güven Skoru: {analysis.confidence_score * 100:.2f}%")
            
            # Attempt to extract explanation from raw Gemini response for healthy case if it's JSON
            explanation_from_json = None
            if analysis.gemini_response:
                try:
                    gemini_json = json.loads(analysis.gemini_response)
                    explanation_from_json = gemini_json.get('explanation')
                except json.JSONDecodeError:
                    pass # Not a valid JSON, will display raw response later

            if explanation_from_json:
                st.write(f"Açıklama: {explanation_from_json}")
        else:
            st.warning("Hastalık tespiti yapılamadı veya AI yanıtı ayrıştırılamadı.")

        st.subheader("Öneriler")
        if recommendations:
            for rec in recommendations:
                recommendation_card(rec)
        else:
            st.info("Bu analiz için henüz bir öneri bulunmamaktadır.")

        # Display the raw Gemini response for debugging and full context
        if analysis.gemini_response:
            with st.expander("Tam AI Yanıtı (Geliştirici Notu)"):
                st.code(analysis.gemini_response, language='json') # Try to display as JSON, falls back to text

        st.markdown("--- ")
        st.subheader("📝 Takip Notları")
        follow_up_notes = st.text_area("Bu analizle ilgili not ekle:", key=f"follow_up_note_{analysis.id}")
        if st.button("Takip Notu Ekle", key=f"add_follow_up_{analysis.id}"):
            if follow_up_notes and analysis.id:
                db_service.add_follow_up(analysis.id, "pending", follow_up_notes)
                st.success("Takip notu başarıyla eklendi!")
                st.rerun()
            else:
                st.warning("Lütfen bir not girin ve analizin kaydedildiğinden emin olun.")
        
        st.markdown("**Mevcut Takip Notları:**")
        if analysis.id:
            follow_ups = db_service.get_follow_ups_by_analysis_id(analysis.id)
            if follow_ups:
                for fu in follow_ups:
                    st.markdown(f"- **{fu.get('follow_up_date', 'Bilinmiyor')}** ({fu.get('status', 'Bilinmiyor')}): {fu.get('notes', '')}")
            else:
                st.info("Bu analiz için henüz takip notu bulunmamaktadır.")
        else:
            st.info("Analiz kaydedilmediği için takip notları eklenemiyor.")

    else:
        st.info("Henüz bir analiz yapılmadı.")

