import streamlit as st
from openai import OpenAI
import base64

# 페이지 설정
st.set_page_config(
    page_title="논설문 첨삭 도우미 (오홍석 선생님)",
    page_icon="✒️",
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

# 세션 상태 초기화
if 'extracted_text' not in st.session_state:
    st.session_state['extracted_text'] = ""

# 2. 화면 디자인
st.title("✒️ AI 논설문 첨삭 도우미")
st.markdown("""
### 종이에 쓴 글도 OK! 사진만 찍어 올리세요.
직접 타이핑해서 넣어도 되고, **공책에 쓴 글을 사진으로 찍어서** 올려도 됩니다.  
**오홍석 선생님의 비서 AI가 날카롭게 분석해 드립니다.**
""")

col1, col2 = st.columns(2)

# 이미지 인코딩 함수
def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# [기능 1] 이미지 텍스트 추출
def extract_text_from_images(image_files):
    content_list = [{"type": "text", "text": "이 이미지들에 적힌 '손글씨'를 그대로 읽어서 텍스트로만 바꿔주세요. 오직 글자만 추출해서 보여주세요."}]
    for img_file in image_files:
        base64_image = encode_image(img_file)
        content_list.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content_list}],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류 발생: {str(e)}"

# [기능 2] 최종 분석 함수 (예시 제공 기능 강화)
def analyze_final_text(title, content):
    system_prompt = """
    당신은 '오홍석 선생님의 스마트한 비서 AI'이자, 날카로운 분석력을 가진 중학교 국어 교사입니다.
    학생의 글을 **아래 13가지 평가 기준**에 맞춰 분석하되, 단순히 지적만 하지 말고 **"어떻게 고쳐야 하는지" 구체적인 예시 문장(Rewrite)**을 반드시 제공해야 합니다.

    [상세 평가 가이드라인 (13가지 기준 + 학습 자료)]
    1. **주제 명확성:** 주제가 일관된가?
    2. **독자 고려:** 서론 전략(질문/사례/통계 등)을 썼는가? 경어체(높임말)를 썼는가?
    3. **문단 중심생각:** 한 문단에 하나의 소주제만 있는가?
    4. **문장 호응:** 주어-서술어 호응이 맞는가? (비문 수정 필수)
    5. **표현의 적절성:** 모호하거나 과격한 표현은 없는가?
    6. **문단 순서:** 논리 전개가 자연스러운가?
    7. **제목:** 흥미를 끄는 제목인가?
    8. **어휘:** 적절하고 정확한 어휘인가?
    9. **통일성:** 불필요한 문장은 없는가?
    10. **맞춤법:** 오탈자 체크 (3개 이상)
    11. **근거 및 출처:** 근거 유형(통계/사례/전문가) 다양성 및 출처 명기 여부.
    12. **문단 구분:** 들여쓰기 및 시각적 구분.
    13. **논설문 짜임:** 서론-본론-결론 구조. **특히 결론이 [요약-재확인-전망] 단계를 갖췄는가?**

    [피드백 작성 규칙 - 예시 강화]
    1. **말투:** 정중하지만 냉철한 분석조(하십시오체/해요체).
    2. **형식:** 각 번호마다 이모지(✅, 🔺, ❌) 표시.
    3. **구체적 개선 예시 (가장 중요):**
       - 🔺나 ❌ 평가를 내린 항목은 **반드시 "이렇게 바꿔보세요"라고 예시 문장을 작성해 주세요.**
       - (예시) "서론이 밋밋합니다." (X) 
       - (예시) "서론에 독자의 흥미를 끄는 요소가 부족합니다. **질문 던지기 전략을 활용하여 다음과 같이 시작해보면 어떨까요?**
         👉 **수정 예시:** '여러분은 하루에 스마트폰을 몇 시간이나 보시나요? 무심코 보는 스마트폰이 우리 뇌를 병들게 하고 있다는 사실, 알고 계셨나요?'"
       - (예시) "근거가 빈약합니다." (X)
       - (예시) "근거에 구체적인 수치가 빠져있습니다. **다음과 같이 통계 자료를 인용하는 문장을 추가해 보세요.**
         👉 **수정 예시:** '최근 교육부의 2023년 조사 결과에 따르면, 청소년의 40%가 스마트폰 과의존 위험군에 속한다고 합니다.'"
    """

    user_content = f"""
    [분석 대상]
    - 제목: {title}
    - 내용: {content}
    
    위 글을 분석해주세요. 특히 부족한 부분은 '직접 고쳐쓴 예시 문장'을 들어서 설명해주세요.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.6,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"시스템 오류가 발생했습니다: {str(e)}"

# 3. 입력 창 구성
with col1:
    st.info("👇 글을 입력하거나 사진을 올리세요")
    
    tab1, tab2 = st.tabs(["⌨️ 직접 입력하기", "📷 사진 올리기 (최대 2장)"])
    
    with tab1:
        title_input_1 = st.text_input("제목 (직접 입력)", placeholder="제목을 입력하세요", key="t1")
        content_input_1 = st.text_area("본문 내용 (직접 입력)", height=500, placeholder="내용을 입력하세요", key="c1")
        analyze_btn_1 = st.button("📝 입력한 내용으로 검토받기", type="primary", use_container_width=True)

    with tab2:
        uploaded_files = st.file_uploader(
            "공책을 찍은 사진을 올려주세요 (최대 2장)", 
            type=['png', 'jpg', 'jpeg'], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if len(uploaded_files) > 2:
                st.warning("⚠️ 사진은 최대 2장까지만 선택해주세요.")
                uploaded_files = uploaded_files[:2]
            
            cols = st.columns(len(uploaded_files))
            for idx, file in enumerate(uploaded_files):
                with cols[idx]:
                    st.image(file, caption=f"사진 {idx+1}", use_container_width=True)
            
            if st.button("🔍 사진에서 글자 추출하기 (클릭)", type="secondary", use_container_width=True):
                with st.spinner("사진을 읽고 있습니다... ⏳"):
                    extracted_text = extract_text_from_images(uploaded_files)
                    st.session_state['extracted_text'] = extracted_text
                    st.success("글자를 읽어왔습니다! 아래에서 확인하고 수정해주세요.")

        if st.session_state['extracted_text']:
            st.markdown("---")
            st.subheader("🧐 텍스트 확인 및 수정")
            title_input_2 = st.text_input("글의 제목을 적어주세요", placeholder="제목 입력", key="t2")
            content_input_2 = st.text_area(
                "추출된 본문 내용 (수정 가능)", 
                value=st.session_state['extracted_text'], 
                height=400,
                key="c2"
            )
            analyze_btn_2 = st.button("✨ 수정한 내용으로 최종 검토받기", type="primary", use_container_width=True)

# 4. 결과 출력
with col2:
    st.subheader("🧐 오홍석 선생님 비서 AI의 분석")
    
    if analyze_btn_1:
        if not title_input_1 or not content_input_1:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner("예시를 포함하여 정밀 분석 중입니다..."):
                result = analyze_final_text(title_input_1, content_input_1)
                st.success("분석 완료!")
                st.markdown(result)

    try:
        if 'analyze_btn_2' in locals() and analyze_btn_2:
            if not title_input_2 or not content_input_2:
                st.warning("제목과 본문을 확인해주세요.")
            else:
                with st.spinner("예시를 포함하여 정밀 분석 중입니다..."):
                    result = analyze_final_text(title_input_2, content_input_2)
                    st.success("분석 완료!")
                    st.markdown(result)
    except NameError:
        pass
