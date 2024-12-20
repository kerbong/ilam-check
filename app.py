import streamlit as st
from openai import OpenAI
from datetime import datetime
import os
import streamlit.components.v1 as components

# OpenAI API 설정
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Streamlit 인터페이스 설정
st.title("종합일람표 점검기 (OpenAI API 활용)")

# 사용자 입력: 학기 날짜 설정
st.sidebar.markdown("### 학기 기준 설정")
st.sidebar.write("1학기")
s1_start = st.sidebar.date_input("시작일", value=datetime(2024, 3, 1))
s1_end = st.sidebar.date_input("종료일", value=datetime(2024, 8, 15))
st.sidebar.write("2학기")
s2_start = st.sidebar.date_input("시작일", value=datetime(2024, 8, 16))
s2_end = st.sidebar.date_input("종료일", value=datetime(2025, 2, 28))

# 문장 점검 함수 정의 (OpenAI API 활용)
def check_sentence_with_openai(sentence):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 4o Mini 버전 지정
            messages=[
                {"role": "system", "content": (
                    "You are a helpful assistant that reviews Korean sentences based on the following criteria:\n"
                    "1.문장 끝에 '~할 수 있음.'같은거 없애고, 무조건 명사형 어미 '~함.' '~임.' '~음.'으로 끝내기\n"
                    "2.오탈자\n"
                    "3.띄어쓰기 없거나 두 칸 띄어 쓴 곳\n"
                    "4.문장이 어색한 경우(예:'~고' '~고'의 반복)\n"
                    "5.부정적인 문장 미래가능성으로 바꾸기\n"
                    "6.금지 단어 사용 여부 확인(예: kg -> 킬로그램, AI -> 인공지능)\n"
                    "7.사용 가능한 단어 (예:외국인 성명, 도서명, 일반화된 명사 등)\n"
                    "8.반장, 부반장이나 회장, 부회장이 문장에 있으면 1학기:{s1_start}~{s1_end}, 2학기:{s2_start}~{s2_end}와 일치하는지 확인\n"
                    "9.가장 끝 문장 마침표 후에 띄어쓰기 없게\n"
                )},
                {"role": "user", "content": f"다음 문장을 점검하고 수정된 결과물만 보여줘: {sentence}"}
            ]
        )

        suggestions = response.choices[0].message.content
        return suggestions
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"


# 문장 입력
sentence = st.text_area("문장을 입력하세요", placeholder="여기에 문장을 입력하거나 붙여넣으세요.", height=400)

# 버튼 추가: '문장 점검' 버튼을 클릭하면 OpenAI 함수 실행
if st.button('문장 점검'):
    if sentence:
        st.markdown("**점검 결과:**")
        suggestions = check_sentence_with_openai(sentence)

        # 결과랑 원래 제공한 문장이 같으면 변경내용 없음 표시
        if sentence == suggestions:
            st.write("변경내용 없음")
        else:
           
            st.session_state.suggestions = suggestions  # session_state에 저장

            if suggestions:
                st.write("아래 결과를 클릭하면 바로 복사됩니다.")
                # 복사하려는 텍스트를 포함한 div 태그를 생성합니다.
                components.html(f"""
                    <div id="suggestions-div" style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9; cursor: pointer;">
                        {st.session_state.suggestions}
                    </div>
                    <div id="copy-message" style="color: green; font-size: 14px; padding: 5px;"></div>
                    <script>
                    document.getElementById('suggestions-div').addEventListener('click', async function() {{
                        try {{
                            const text = document.getElementById('suggestions-div').innerText;
                            if (!text) {{
                                document.getElementById('copy-message').innerText = "복사할 내용이 없습니다.";
                                return;
                            }}

                            // Clipboard API를 사용하여 텍스트를 클립보드에 복사합니다.
                            await navigator.clipboard.writeText(text);
                            document.getElementById('copy-message').innerText = "복사되었습니다!";
                        }} catch (err) {{
                            console.error("복사 중 오류 발생:", err);
                            document.getElementById('copy-message').innerText = "복사에 실패했습니다.";
                        }}
                    }});
                    </script>
                """)
            else:
                st.write("문장을 수정할 필요가 없습니다!")