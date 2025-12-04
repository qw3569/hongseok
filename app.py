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

# 세션 상태 초기화 (텍스트 수정 기능을 위해 필요)
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

# 이미지 파일을 base64로 변환하는 함수
def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# [기능 1] 이미지에서 텍스트만 추출하는 함수
def extract_text_from_images(image_files):
    content_list = [{"type": "text", "text": "이 이미지들에 적힌 '손글씨'를 그대로 읽어서 텍스트로만 바꿔주세요. 분석이나 평가는 하지 말고, 오직 글자만 추출해서 보여주세요."}]
    
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

# [기능 2] 텍스트를 분석하는 함수 (심층 분석)
def analyze_final_text(title, content):
    system_prompt = """
    당신은 '오홍석 선생님의 스마트한 비서 AI'이자, 날카로운 분석력을 가진 중학교 국어 교사입니다.
    학생의 글을 **아래 13가지 평가 기준**에 맞춰 분석하되, **[학습 자료: 논설문 잘 쓰는 법]의 세부 전략들을 기준마다 적용**하여 다각도로 평가해야 합니다.
    
    [상세 평가 가이드라인 (13가지 기준 + 학습 자료)]
    1. **주제 명확성:** 글 전체가 하나의 주제를 향해 일관되게 나아가고 있는가?
    2. **독자 고려:** 서론에서 '현상 제시', '사례', '상반된 인식', '질문 던지기' 중 어떤 전략을 썼는가?
    3. **문단 중심생각:** 각 문단이 소주제 하나씩만 명확히 다루고 있는가?
    4. **문장 호응:** 주어-서술어, 목적어-서술어 호응이 자연스러운가? (비문 지적)
    5. **표현의 적절성:** 모호하거나 지나치게 단호한 표현은 없는가?
    6. **문단 순서:** 논리 전개(주장-근거-요약)가 자연스러운가?
    7. **제목:** 독자의 호기심을 자극하는 제목인가?
    8. **어휘:** 문맥에 맞는 적절하고 정확한 어휘인가?
    9. **통일성:** 군더더기 문장은 없는가?
    10. **맞춤법:** 띄어쓰기, 철자 오류 체크 (3개 이상 사례 제시)
    11. **근거 및 출처:** 근거 유형(통계/전문가/사례)을 다양하게 썼는가? 출처는 명확한가?
    12. **문단 구분:** 문단이 시각적으로 잘 나누어져 있는가?
    13. **논설문 짜임:** 서론-본론-결론 구조가 완벽한가? 특히 결론이 [요약-재확인-전망]의 3단계를 갖추었는가?

    [피드백 작성 지침 - 엄격 준수]
    1. **말투:** 정중하지만 비판적인 어조(하십시오체/해요체 혼용).
    2. **형식:** 이모지(✅, 🔺, ❌)와 함께 상세 분석.
    3. **내용:** 한 기준당 2~3줄 이상 깊이 있게 분석할 것.
    4. **수정 제안(필수):** 문제점은 반드시 "이 문장은 [ ~ ]라고 고치는 것이 좋습니다."라고 직접 수정해 줄 것.
    """

    user_content = f"""
    [분석 대상]
    - 제목: {title}
    - 내용: {content}
    
    위 글을 13가지 기준과 학습 자료의 전략을 바탕으로 '매우 상세하게' 비판적으로 분석해주세요.
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
    
    # [탭 1] 직접 입력
    with tab1:
        title_input_1 = st.text_input("제목 (직접 입력)", placeholder="제목을 입력하세요", key="t1")
        content_input_1 = st.text_area("본문 내용 (직접 입력)", height=500, placeholder="내용을 입력하세요", key="c1")
        analyze_btn_1 = st.button("📝 입력한 내용으로 검토받기", type="primary", use_container_width=True)

    # [탭 2] 사진 업로드 -> 텍스트 추출 -> 수정 -> 분석
    with tab2:
        uploaded_files = st.file_uploader(
            "공책을 찍은 사진을 올려주세요 (최대 2장)", 
            type=['png', 'jpg', 'jpeg'], 
            accept_multiple_files=True
        )
        
        # 사진이 올라오면 '추출' 버튼 보여주기
        if uploaded_files:
            if len(uploaded_files) > 2:
                st.warning("⚠️ 사진은 최대 2장까지만 선택해주세요. (앞의 2장만 사용합니다)")
                uploaded_files = uploaded_files[:2]
            
            # 사진 미리보기
            cols = st.columns(len(uploaded_files))
            for idx, file in enumerate(uploaded_files):
                with cols[idx]:
                    st.image(file, caption=f"사진 {idx+1}", use_container_width=True)
            
            if st.button("🔍 사진에서 글자 추출하기 (클릭)", type="secondary", use_container_width=True):
                with st.spinner("사진을 읽고 있습니다... 잠시만 기다려주세요 ⏳"):
                    extracted_text = extract_text_from_images(uploaded_files)
                    st.session_state['extracted_text'] = extracted_text
                    st.success("글자를 읽어왔습니다! 아래에서 내용을 확인하고 틀린 글자가 있으면 고쳐주세요.")

        # 추출된 텍스트가 있으면 편집창 보여주기
        if st.session_state['extracted_text']:
            st.markdown("---")
            st.subheader("🧐 텍스트 확인 및 수정")
            st.caption("AI가 사진을 잘못 읽은 부분이 있다면 직접 고쳐주세요.")
            
            # 제목 입력 (사진에는 제목 구분 기능이 없으므로 따로 입력받음)
            title_input_2 = st.text_input("글의 제목을 적어주세요", placeholder="제목 입력", key="t2")
            
            # 본문 수정 창 (추출된 텍스트가 기본값으로 들어감)
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
    
    # [경우 1] 탭 1에서 직접 입력하고 버튼 누름
    if analyze_btn_1:
        if not title_input_1 or not content_input_1:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner("정밀 분석 중입니다..."):
                result = analyze_final_text(title_input_1, content_input_1)
                st.success("분석 완료!")
                st.markdown(result)

    # [경우 2] 탭 2에서 추출된 텍스트 수정 후 버튼 누름
    # (주의: analyze_btn_2 변수가 정의되지 않았을 수 있으므로 try-except나 조건문 처리)
    try:
        if 'analyze_btn_2' in locals() and analyze_btn_2:
            if not title_input_2 or not content_input_2:
                st.warning("제목과 본문 내용을 모두 확인해주세요.")
            else:
                with st.spinner("수정된 내용을 바탕으로 정밀 분석 중입니다..."):
                    result = analyze_final_text(title_input_2, content_input_2)
                    st.success("분석 완료!")
                    st.markdown(result)
    except NameError:
        pass
