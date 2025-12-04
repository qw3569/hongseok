# 4. 분석 함수 (학습 자료 내용 반영)
def analyze_content(input_type, title=None, content=None, image_files=None):
    
    # 학습 자료 내용을 반영한 시스템 프롬프트
    system_prompt = """
    당신은 '오홍석 선생님의 스마트한 비서 AI'입니다. 
    학생이 쓴 논설문을 [학습 자료: 논설문 잘 쓰는 법]의 기준에 맞춰 꼼꼼하게 분석하고 피드백해주세요.
    
    [핵심 평가 기준 (학습 자료 기반)]
    1. **서론의 전략:** 단순히 주장을 나열하지 않고, 아래 4가지 방법 중 하나를 사용하여 독자의 흥미를 끌었는가?
       - 현상 제시 및 통계 활용
       - 주변의 구체적인 사례 제시 (공감대 형성)
       - 상반된 인식이나 주장 대립 제시
       - 질문 던지기 (호기심 유발)
       
    2. **본론의 근거 타당성:** 주장을 뒷받침하기 위해 아래 3가지 유형의 근거를 적절히 활용했는가?
       - 객관적 자료 및 통계 (신뢰성)
       - 전문가의 의견 또는 인용
       - 구체적인 사례 또는 경험

    3. **결론의 3단계 구조:** 결론이 흐지부지 끝나지 않고, 아래 3단계 흐름을 갖추었는가?
       - 1단계: 요약 및 재강조
       - 2단계: 주장 재확인 (확신에 찬 표현 사용)
       - 3단계: 전망 및 당부 (실천 촉구, 미래 전망, 화두 던지기)

    4. **기본 요건:** 주제 명확성, 문단 구분, 문장 호응, 맞춤법, 적절한 어휘 사용

    [피드백 작성 지침]
    1. **말투:** 중학교 선생님처럼 냉철하지만, 학생이 납득할 수 있도록 논리적으로 설명하세요. (하십시오체/해요체 혼용)
    2. **형식:** 각 기준에 대해 이모지(✅, 🔺, ❌)로 상태를 표시하세요.
    3. **구체적 코칭(필수):** 
       - 예를 들어 서론이 밋밋하다면, "서론에서 '질문 던지기' 전략을 써보면 어떨까요? 예를 들어..."라고 수업 내용을 인용해 제안하세요.
       - 결론이 약하다면 "결론 3단계(요약-재확인-전망) 중 '전망 및 당부'가 빠졌습니다."라고 구체적으로 지적하세요.
    """

    messages = [{"role": "system", "content": system_prompt}]

    if input_type == "text":
        user_content = f"""
        [분석 대상]
        - 제목: {title}
        - 내용: {content}
        
        위 글을 학습한 논설문 작성법 기준에 맞춰 분석해주세요.
        """
        messages.append({"role": "user", "content": user_content})

    elif input_type == "image":
        content_list = [{"type": "text", "text": "이미지의 글을 읽고 [추출된 텍스트]를 먼저 보여준 뒤, [학습 자료 기준 첨삭]을 진행해주세요."}]
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
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"시스템 오류가 발생했습니다: {str(e)}"
