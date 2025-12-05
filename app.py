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
        uploaded_file.seek(0)
        return base64.b64encode(uploaded_file.read()).decode('utf-8')
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
        return f"Error: {str(e)}"

# [기능 2] 최종 분석 함수 (심층 사고 로직 강화)
def analyze_final_text(title, content):
    system_prompt = """
    당신은 '오홍석 선생님의 스마트한 비서 AI'이자, 날카로운 분석력을 가진 중학교 국어 교사입니다.
    학생의 글을 13가지 평가 기준에 맞춰 분석하고, 부족한 부분은 **'더 나은 표현'으로 수정 예시**를 제공해야 합니다.

    [⚠️ 수정 예시(Rewrite) 작성 시 심층 사고 가이드라인 - 매우 중요]
    수정 예시를 제시하기 전에 반드시 **내부적으로 다음 3가지를 검증**한 후 출력하세요.
    1. **맥락 유지:** 학생이 원래 말하려던 의도가 왜곡되지 않았는가?
    2. **확실한 개선:** 내가 제안하는 문장이 원문보다 **확실히 더 논리적이거나 간결한가?** (별 차이가 없거나 더 어색하면 고치지 마세요.)
    3. **수준 적절성:** 중학생 수준에서 너무 현학적이거나 어려운 단어를 쓰지 않았는가?

    [상세 평가 가이드라인 (13가지 기준 + 학습 자료)]
    1. **주제 명확성:** 주제 일관성 확인.
    2. **독자 고려:** 서론 전략(질문/통계 등) 및 높임말 사용 여부.
    3. **문단 중심생각:** 한 문단 일물일어(一物一語) 원칙 준수 여부.
    4. **문장 호응:** 주어-서술어 호응 등 비문 분석.
    5. **표현의 적절성:** 모호하거나 과격한 표현 지양.
    6. **문단 순서:** 논리 전개 순서.
    7. **제목:** 호기심 자극 여부.
    8. **어휘:** 문맥에 맞는 적절한 어휘 사용.
    9. **통일성:** 통일성을 해치는 문장 삭제 권고.
    10. **맞춤법:** 오탈자 정밀 체크.
    11. **근거 및 출처:** 근거 유형 다양화 및 출처 명기.
    12. **문단 구분:** 들여쓰기 확인.
    13. **논설문 짜임:** 서론-본론-결론(요약/재확인/전망) 구조 완결성.

    [피드백 작성 규칙]
    1. **말투:** 정중하지만 냉철한 분석조(하십시오체/해요체).
    2. **형식:** 각 번호마다 이모지(✅, 🔺, ❌) 표시.
    3. **수정 제안 (Deep Thinking 적용):** 
       - 🔺나 ❌ 항목은 반드시 **"수정 제안"**을 포함하세요.
       - 단순히 문장을 바꾸는 게 아니라 **"왜 이렇게 바꾸는 게 더 좋은지" 이유를 짧게 설명**하고 예시를 보여주세요.
       - (예시) "이 문장은 주어와 서술어가 멀어서 의미가 불분명합니다. 다음과 같이 문장을 나누어 쓰면 훨씬 명확해집니다."
         👉 **수정 제안:** "..."
    """

    user_content = f"""
    [분석 대상]
    - 제목: {title}
    - 내용: {content}
    
    위 글을 분석해주세요. 수정 예시를 들 때는 그 예시가 문맥상 정말 적절한지 깊게 생각하고 작성해주세요.
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
                    result_text = extract_text_from_images(uploaded_files)
                    
                    if result_text.startswith("Error"):
                        st.error(f"이미지 읽기 실패: {result_text}")
                    else:
                        st.session_state['extracted_text'] = result_text
                        st.success("글자를 읽어왔습니다! 아래에서 확인해주세요.")
                        st.rerun()

        if st.session_state['extracted_text']:
            st.markdown("---")
            st.subheader("🧐 텍스트 확인 및 수정")
            st.caption("AI가 사진을 잘못 읽은 부분이 있다면 직접 고쳐주세요.")
            
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
            with st.spinner("예시의 적절성을 검토하며 분석 중입니다..."):
                result = analyze_final_text(title_input_1, content_input_1)
                st.success("분석 완료!")
                st.markdown(result)

    try:
        if 'analyze_btn_2' in locals() and analyze_btn_2:
            if not title_input_2 or not content_input_2:
                st.warning("제목과 본문을 확인해주세요.")
            else:
                with st.spinner("예시의 적절성을 검토하며 분석 중입니다..."):
                    result = analyze_final_text(title_input_2, content_input_2)
                    st.success("분석 완료!")
                    st.markdown(result)
    except NameError:
        pass
