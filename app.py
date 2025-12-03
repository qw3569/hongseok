import streamlit as st
import openai

# 페이지 설정
st.set_page_config(page_title="6학년 국어 글 고쳐쓰기 도우미", page_icon="📝", layout="wide")

# 비밀번호(API 키) 가져오기
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("선생님! API 키 설정이 필요해요. (Streamlit Secrets에 설정해주세요)")

# 메인 화면
st.title("📝 글 고쳐쓰기 도우미")
st.markdown("여러분이 쓴 논설문을 입력하면 AI 선생님이 피드백을 해줍니다.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✍️ 글 입력하기")
    title = st.text_input("글의 제목", placeholder="제목을 입력하세요")
    content = st.text_area("글의 내용", height=400, placeholder="여기에 내용을 쓰세요.")
    analyze_btn = st.button("내 글 검토받기", type="primary")

def get_feedback(title, content):
    prompt = f"""
    당신은 친절한 초등학교 6학년 국어 선생님입니다. 
    아래 학생 글을 13가지 기준으로 검토해주세요.
    말투는 초등학생에게 말하듯 친절하게(해요체) 해주세요.
    
    [글] 제목: {title}, 내용: {content}
    
    [기준]
    1.주제 명확성 2.독자 고려 3.문단 중심생각 4.문장 호응 5.모호한 표현 
    6.문단 순서 7.제목 흥미 8.어휘 수준 9.통일성 10.맞춤법 
    11.자료 출처 12.문단 구분 13.논설문 짜임(서론/본론/결론)

    각 번호마다 이모지(✅, ⚠️, ❌)를 쓰고 구체적 조언을 해주세요.
    마지막엔 3줄 총평을 남겨주세요.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Helpful teacher assistant."}, {"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"오류가 났어요: {str(e)}"

with col2:
    st.subheader("🔍 선생님의 피드백")
    if analyze_btn:
        if not title or not content:
            st.warning("제목과 내용을 모두 써주세요!")
        else:
            with st.spinner("분석 중... 잠시만 기다려주세요!"):
                result = get_feedback(title, content)
                st.markdown(result)
