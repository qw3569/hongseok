import streamlit as st
from openai import OpenAI
import base64

# 페이지 설정
st.set_page_config(
    page_title="논설문 첨삭 도우미 (오홍석 선생님)",
    page_icon="📸",
    layout="wide"
)

# 1. API 클라이언트 설정
try:
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        st.error("🚨 API 키 설정이 필요합니다. (Streamlit Secrets 확인 필요)")
        st.stop()
except Exception as e:
    st.error(f"시스템 오류 발생: {e}")
    st.stop()

# 2. 화면 디자인 (수정된 부분)
st.title("📸 AI 논설문 첨삭 도우미")
st.markdown("""
### 종이에 쓴 글도 OK! 사진만 찍어 올리세요.
직접 타이핑해서 넣어도 되고, **공책에 쓴 글을 사진으로 찍어서** 올려도 됩니다.  
**오홍석 선생님의 비서 AI가 날카롭게 분석해 드립니다.**
""")

col1, col2 = st.columns(2)

# 이미지 파일을 base64로 변환하는 함수
def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# 3. 입력 창
with col1:
    st.info("👇 글을 입력하거나 사진을 올리세요")
    
    tab1, tab2 = st.tabs(["⌨️ 직접 입력하기", "📷 사진 올리기"])
    
    with tab1:
        title_input = st.text_input("제목 (직접 입력)", placeholder="제목을 입력하세요")
        content_input = st.text_area("본문 내용 (직접 입력)", height=400, placeholder="내용을 입력하세요")
        analyze_text_btn = st.button("📝 텍스트로 검토받기", type="primary", use_container_width=True)

    with tab2:
        uploaded_file = st.file_uploader("글씨가 잘 보이게 찍은 사진을 올려주세요", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, caption="업로드된 사진", use_container_width=True)
        analyze_image_btn = st.button("📸 사진으로 검토받기", type="primary", use_container_width=True)

# 4. 분석 함수
def analyze_content(input_type, title=None, content=None, image_base64=None):
    
    # 시스템 프롬프트 (비서 AI 페르소나 적용)
    system_prompt = """
    당신은 '오홍석 선생님의 스마트한 비서 AI'입니다. 
    하지만 글을 평가할 때는 **엄격하고 실력 있는 중학교 국어 선생님의 기준**을 적용해야 합니다.
    학생의 글을 읽고 논리적 허점과 문장력을 비판적으로 분석하여, 글의 수준을 높일 수 있는 구체적인 수정안을 제시하세요.
    
    [평가 기준 13가지]
    1. 주제 명확성 2. 독자 고려 3. 문단 통일성 4. 문장 호응 5. 모호한 표현 지양
    6. 논리적 문단 배열 7. 제목의 적절성 8. 적절하고 정확한 어휘 9. 군더더기 문장 삭제
    10. 맞춤법/띄어쓰기 11. 근거 자료 출처 12. 문단 구분 13. 3단 구성(서론-본론-결론)

    [출력 지침]
    1. 각 번호 앞에 이모지(✅, 🔺, ❌) 표시.
    2. 무조건적인 칭찬 지양. 냉정하고 객관적인 어조 유지.
    3. **수정 제안 필수:** 문맥상 어색한 부분은 "이 문장은 ~게 고치는 것이 더 자연스럽습니다"라고 대안 제시.
    4. 어휘 수준을 높일 수 있는 표현 적극 제안.
    """

    messages = [{"role": "system", "content": system_prompt}]

    if input_type == "text":
        user_content = f"""
        [분석 대상]
        - 제목: {title}
        - 내용: {content}
        
        위 글을 오홍석 선생님의 기준(13가지)으로 비판적으로 분석해주세요.
        """
        messages.append({"role": "user", "content": user_content})

    elif input_type == "image":
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": "이 이미지에 있는 글자들을 읽어서, 먼저 **[추출된 텍스트]**를 보여주고, 그 다음에 오홍석 선생님의 기준(13가지)에 맞춰서 **[첨삭 결과]**를 자세히 작성해 주세요."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        })

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.6,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"시스템 오류가 발생했습니다: {str(e)}"

# 5. 결과 출력
with col2:
    st.subheader("🧐 오홍석 선생님 비서 AI의 분석")
    
    if analyze_text_btn:
        if not title_input or not content_input:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner("비서 AI가 텍스트를 분석 중입니다..."):
                result = analyze_content("text", title=title_input, content=content_input)
                st.success("분석 완료!")
                st.markdown(result)

    if analyze_image_btn:
        if not uploaded_file:
            st.warning("사진을 먼저 올려주세요.")
        else:
            with st.spinner("비서 AI가 사진을 읽고 분석 중입니다... (시간이 조금 걸려요 ⏳)"):
                image_base64 = encode_image(uploaded_file)
                if image_base64:
                    result = analyze_content("image", image_base64=image_base64)
                    st.success("분석 완료!")
                    st.markdown(result)
                else:
                    st.error("이미지 처리에 실패했습니다.")
