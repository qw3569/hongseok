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

# 2. 화면 디자인
st.title("✒️ AI 논설문 첨삭 도우미")
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
    
    tab1, tab2 = st.tabs(["⌨️ 직접 입력하기", "📷 사진 올리기 (최대 2장)"])
    
    with tab1:
        title_input = st.text_input("제목 (직접 입력)", placeholder="제목을 입력하세요")
        content_input = st.text_area("본문 내용 (직접 입력)", height=500, placeholder="내용을 입력하세요")
        analyze_text_btn = st.button("📝 텍스트로 검토받기", type="primary", use_container_width=True)

    with tab2:
        uploaded_files = st.file_uploader(
            "글씨가 잘 보이게 찍은 사진을 올려주세요 (최대 2장)", 
            type=['png', 'jpg', 'jpeg'], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if len(uploaded_files) > 2:
                st.warning("⚠️ 사진은 최대 2장까지만 선택해주세요. (앞의 2장만 분석합니다)")
                uploaded_files = uploaded_files[:2]
            
            cols = st.columns(len(uploaded_files))
            for idx, file in enumerate(uploaded_files):
                with cols[idx]:
                    st.image(file, caption=f"사진 {idx+1}", use_container_width=True)
                    
        analyze_image_btn = st.button("📸 사진으로 검토받기", type="primary", use_container_width=True)

# 4. 분석 함수 (13가지 기준 + 학습 자료 통합)
def analyze_content(input_type, title=None, content=None, image_files=None):
    
    # 시스템 프롬프트: 13가지 기준을 살리되, 각 항목에 학습 자료의 구체적 전략을 연결함
    system_prompt = """
    당신은 '오홍석 선생님의 스마트한 비서 AI'입니다. 
    학생의 글을 **아래 13가지 평가 기준**에 맞춰 분석하되, **[학습 자료: 논설문 잘 쓰는 법]의 구체적인 전략**을 적용하여 피드백해야 합니다.
    무조건적인 칭찬은 지양하고 **중학교 국어 교사의 시각에서 논리적 허점과 문장력을 비판적으로 검토**하세요.

    [평가 기준 13가지 (학습 자료 내용 통합)]
    1. **주제 명확성:** 무엇을 쓴 글인지 주제가 명확히 드러나는가?
    2. **독자 고려:** 읽는 사람을 고려했는가? (서론에서 공감대 형성, 질문 던지기 등 활용)
    3. **문단 중심생각:** 한 문단에 하나의 중심 생각만 있는가?
    4. **문장 호응:** 주어-서술어 호응 등 문장이 자연스러운가?
    5. **표현의 적절성:** 모호하거나 지나치게 단호한 표현은 없는가?
    6. **문단 순서:** 문단의 연결과 순서가 논리적인가?
    7. **제목:** 사람들이 주목할만한(흥미를 가질만한) 제목인가?
    8. **어휘:** 어렵게 써진 낱말 없이 문맥에 맞는 어휘를 썼는가?
    9. **통일성:** 주제와 관련 없는 군더더기 문장은 없는가?
    10. **맞춤법:** 띄어쓰기, 맞춤법은 정확한가?
    11. **근거 및 출처:** 근거에 사용한 자료(통계, 전문가 의견, 사례)의 출처는 명확한가? (본론 전략)
    12. **문단 구분:** 문단이 시각적으로 잘 나누어져 있는가? (들여쓰기)
    13. **논설문 짜임:** 서론(문제상황/전략)-본론(타당한 근거)-결론(요약/재확인/전망)의 3단 구성이 완벽한가? (결론 3단계 전략)

    [피드백 작성 지침 - 엄격 준수]
    1. **말투:** 정중하지만 냉철한 어조(하십시오체/해요체 혼용). 과한 칭찬 지양.
    2. **형식:** 1번부터 13번까지 순서대로 이모지(✅, 🔺, ❌)와 함께 평가.
    3. **구체적 수정 제안(필수):** 
       - 예: "13번 항목(결론)이 미흡합니다. 학습한 대로 '요약-주장 재확인-전망'의 3단계 흐름을 갖추어 이렇게 고쳐보세요: [수정 예시 문장]"
       - 예: "2번 항목(독자 고려)을 위해 서론에 '질문 던지기' 전략을 추가해 보세요."
    """

    messages = [{"role": "system", "content": system_prompt}]

    if input_type == "text":
        user_content = f"""
        [분석 대상]
        - 제목: {title}
        - 내용: {content}
        
        위 글을 13가지 기준에 맞춰 비판적으로 분석해주세요.
        """
        messages.append({"role": "user", "content": user_content})

    elif input_type == "image":
        content_list = [{"type": "text", "text": "이미지의 글을 읽고 먼저 **[추출된 텍스트]**를 보여준 뒤, [13가지 기준 정밀 첨삭]을 진행해주세요."}]
        for img_file in image_files:
            base64_image = encode_image(img_file)
            content_list.append({
                "type": "image_url", 
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
        messages.append({"role": "user", "content": content_list})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.6,
            max_tokens=3000
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
            with st.spinner("텍스트를 정밀 분석 중입니다..."):
                result = analyze_content("text", title=title_input, content=content_input)
                st.success("분석 완료!")
                st.markdown(result)

    if analyze_image_btn:
        if not uploaded_files:
            st.warning("사진을 먼저 올려주세요.")
        else:
            with st.spinner("비서 AI가 사진을 읽고 분석 중입니다... (시간이 조금 걸려요 ⏳)"):
                result = analyze_content("image", image_files=uploaded_files)
                st.success("분석 완료!")
                st.markdown(result)
