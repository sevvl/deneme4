import streamlit as st
from services.database_service import DatabaseService
from datetime import datetime

def community_forum_component(db_service: DatabaseService, user_id: int):
    st.header("💬 Topluluk Forumu")

    # Display existing questions
    st.subheader("Sorular")
    questions = db_service.get_questions()

    # Question Submission Form
    with st.expander("Yeni Soru Sor", expanded=False):
        with st.form(key='question_form'):
            question_title = st.text_input("Sorunuzun Başlığı")
            question_text = st.text_area("Sorunuzun Detayı")
            submit_question = st.form_submit_button("Soruyu Gönder")

            if submit_question:
                if not question_title or not question_text:
                    st.warning("Lütfen başlık ve soru detayını girin.")
                else:
                    added_id = db_service.add_question(user_id, question_title, question_text)
                    if added_id:
                        st.success("Sorunuz başarıyla eklendi!")
                        st.rerun()
                    else:
                        st.error("Sorunuz eklenirken bir hata oluştu.")

    if questions:
        for q in questions:
            display_date = q['created_at'] if q['created_at'] else "Bilinmiyor"
            if isinstance(display_date, str):
                try:
                    display_date = datetime.strptime(display_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    pass # Keep as is if parsing fails
            
            with st.expander(f"**{q['title']}** - {q['user_name']} ({display_date})"):
                st.write(q['question_text'])
                st.markdown("--- ")
                st.subheader("Cevaplar")
                answers = db_service.get_answers_for_question(q['id'])
                if answers:
                    for a in answers:
                        answer_display_date = a['created_at'] if a['created_at'] else "Bilinmiyor"
                        if isinstance(answer_display_date, str):
                            try:
                                answer_display_date = datetime.strptime(answer_display_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                            except ValueError:
                                pass # Keep as is if parsing fails
                        st.markdown(f"**{a['user_name']}** ({answer_display_date}): {a['answer_text']}")
                    st.markdown("--- ")
                else:
                    st.info("Henüz bir cevap yok.")

                # Answer Submission Form
                with st.form(key=f'answer_form_{q['id']}'):
                    answer_text = st.text_area("Cevabınızı Yazın", key=f"answer_text_{q['id']}")
                    submit_answer = st.form_submit_button("Cevapla")

                    if submit_answer:
                        if not answer_text:
                            st.warning("Lütfen cevabınızı girin.")
                        else:
                            added_id = db_service.add_answer(q['id'], user_id, answer_text)
                            if added_id:
                                st.success("Cevabınız eklendi!")
                                st.rerun()
                            else:
                                st.error("Cevabınız eklenirken bir hata oluştu.")
    else:
        st.info("Henüz soru sorulmamış.") 