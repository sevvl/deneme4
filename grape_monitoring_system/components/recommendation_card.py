import streamlit as st
from models.recommendation import Recommendation

def recommendation_card(rec: Recommendation):
    """
    Displays a single recommendation as a card.
    """
    st.markdown(f"### {rec.recommendation_type.replace('_', ' ').title()} Önerisi")
    st.write(f"**Açıklama:** {rec.description}")
    st.write(f"**Öncelik:** {'⭐' * rec.priority} ({rec.priority}/5)")
    if rec.implementation_date:
        st.write(f"**Uygulama Tarihi:** {rec.implementation_date.strftime('%Y-%m-%d')}")
    st.markdown("--- ")

