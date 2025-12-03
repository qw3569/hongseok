import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="6학년 국어 글 고쳐쓰기 도우미",
    page_icon="📝",
    layout="wide"
)

# 1. API 클라이언트 설정
# (Streamlit Secrets에 저장된 API 키를 불러옵니다)
try:
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        st.error("🚨 선생님! API 키 설정이 필요해요. (Streamlit Secrets에 설정해주세요)")
        st.stop()
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.stop()

# 2. 화면 디자인
st.title("📝 글 고쳐쓰기 AI 선생님")
st.markdown("""
### 👋 안녕! 글 고쳐쓰기 공부를 하러 왔구나.
여러분이 쓴 논설문을 아래 빈칸에 적어보세요. 
선생님이 알려주신 **13가지 기준**으로 꼼꼼하게 검토해 줄게요.
""")

col1, col2 = st.columns(2)

# 3. 입력 창 (왼쪽 화면)
with col1:
    st.info("👇 여기에 글을 써보세요")
    title = st.text_input("글의 제목", placeholder="제목을 입력하세요")
    content = st.text_area("글의 내용", height=500, placeholder="여기에 내용을 쓰세요.")
    
    analyze_btn = st.button("✨ 내 글 검토받기", type="primary", use_container_width=True)

# 4. 피드백 생성 함수 (핵심 기능!)
def get_detailed_feedback(title, content):
    prompt = f"""
    당신은 초등학교 6학년 학생들을 가르치는 국어 선생님입니다.
    학생이 작성한 논설문을 읽고, 아래 [평가 기준]에 따라 하나씩 꼼꼼하게 피드백을 해주세요.

    [학생이 쓴 글]
    - 제목: {title}
    - 내용: {content}

    [평가 기준 13가지]
    1. 무엇을 쓴 글인지 주제가 명확한가?
    2. 읽는 사람(독자)을 고려했는가? (높임말 사용, 독자의 관심 유도 등)
    3. 한 문단에 하나의 중심 생각만 담겨 있는가?
    4. 문장 호응(주어와 서술어 등)이 자연스러운가?
    5. 모호하거나 지나치게 단호한 표현은 없는가?
    6. 문단의 순서가 자연스러운가?
    7. 제목이 흥미를 끄는가?
    8. 어려운 낱말 없이 이해하기 쉬운가?
    9. 주제와 관련 없는 문장은 없는가?
    10. 맞춤법과 띄어쓰기는 정확한가?
    11. 근거 자료의 출처가 명확한가?
    12. 문단 구분이 잘 되어 있는가? (들여쓰기 등)
    13. 논설문의 짜임(서론-본론-결론)이 잘 갖춰졌는가?

    [피드백 작성 규칙 - 꼭 지켜주세요!]
    1. 말투: 초등학생에게 말하듯 친절하고 부드러운 '해요체'를 쓰세요. (예: "이 부분은 이렇게 고치면 좋겠어요.")
    2. 형식: 각 번호 앞에 이모지(✅, ⚠️, ❌)를 표시하세요.
       - ✅: 아주 잘함
       - ⚠️: 조금 아쉬움 (보완 필요)
       - ❌: 고쳐야 함
    3. **내용 (가장 중요):** 단순히 "잘했어요"나 "고치세요"라고 하지 말고, 
       **반드시 학생이 쓴 문장을 따옴표("")로 가져와서 보여주고, 어떻게 고치면 좋을지 예시를 들어주세요.**
       (예: "'스마트폰은 나빠요'라고 하기보다는 '스마트폰은 눈 건강에 해롭습니다'라고 구체적으로 쓰면 더 설득력이 있어요.")
    4. 마무리: 마지막에는 글 전체에 대한 따뜻한 총평과 응원의 말을 3줄 정도로 남겨주세요.
    """

    try:
        # GPT-4o 사용 (성능 최우선) / 비용 절약 시 "gpt-4o-mini"로 변경 가능
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": "You are a warm, encouraging, and detailed elementary school teacher."}, 
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"앗, 오류가 났어요: {str(e)}"

# 5. 결과 출력 (오른쪽 화면)
with col2:
    st.subheader("🧐 선생님의 피드백")
    
    if analyze_btn:
        if not title or not content:
            st.warning("제목과 내용을 모두 입력해야 검토할 수 있어요! 😅")
        else:
            with st.spinner("선생님이 글을 꼼꼼히 읽고 있어요... (약 10초 소요) ⏳"):
                result = get_detailed_feedback(title, content)
                
                # 결과 보여주기
                st.success("검토가 끝났습니다! 아래 내용을 읽어보세요.")
                st.markdown(result)
                
                # 복사하기 쉽게 텍스트 영역으로도 제공 (선택 사항)
                with st.expander("복사하기 편한 텍스트로 보기"):
                    st.text_area("피드백 복사하기", value=result, height=300)

