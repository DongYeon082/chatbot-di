import streamlit as st
from openai import OpenAI

# Show title and description.
st.set_page_config(page_title="🎓 사칙연산 퀴즈", layout="wide")
st.title("🎓 사칙연산 퀴즈 챗봇")
st.write(
    "반가워! 👋 나는 너의 친구이자 선생님이야. "
    "재미있는 사칙연산 문제를 함께 풀어보자! 화이팅! 💪"
)

# Sidebar configuration
with st.sidebar:
    st.title("⚙️ 모델 설정")
    
    # Model settings expander
    with st.expander("🤖 모델 설정", expanded=True):
        # OpenAI API Key input
        openai_api_key = st.text_input("OpenAI API Key", type="password", key="api_key_input")
        
        # Model selection
        available_models = [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]
        selected_model = st.selectbox(
            "모델 선택",
            available_models,
            index=0,
            help="테스트할 모델을 선택하세요"
        )
        
        # System prompt configuration
        default_system_prompt = """당신은 초등학생을 위한 사칙연산 퀴즈 챗봇입니다.
역할: 문제 출제자 + 응원 친구

규칙:
1. 덧셈, 뺄셈, 곱셈, 나눗셈 문제를 학생 수준에 맞게 낸다.
2. 한 번에 문제는 1개만 낸다.
3. 학생이 답을 말하기 전까지 답을 말하지 않는다.
4. 정답이면:
   - 반드시 칭찬한다. (예: "대단해! 🌟", "완벽해! ⭐️", "정답입니다! 🎉" 등 긍정적인 말)
   - "다음 문제로 넘어갈까?"라고 질문한다.
5. 오답이면:
   - 혼내지 말고 짧은 힌트를 준다. (예: "다시 한 번 생각해 봐!", "비슷해, 거의 다 왔어!")
   - 피드백을 명확하게 제공한다. (예: "조금 커요" 또는 "조금 작아요")
   - "다시 한번 시도해볼까?"라고 질문한다.
6. 학생이 숫자만 입력해도 정답을 확인하고 판정한다. (예: 문제가 "5 + 3 = ?"이면 학생이 "8"만 입력해도 정답 판정)
7. 항상 명확하게 정답인지 오답인지 판정해야 한다. 모호하지 않게!

친절하고 밝은 톤으로 대화하세요. 이모지를 적절히 사용하세요.
처음 시작할 때는 문제를 내기 전에 반가움을 표현하세요."""
        system_prompt = st.text_area(
            "시스템 프롬프트",
            value=default_system_prompt,
            height=180,
            help="챗봇의 역할과 행동을 정의하는 프롬프트입니다"
        )
        
        # Temperature slider
        temperature = st.slider(
            "Temperature (창의성)",
            min_value=0.0,
            max_value=2.0,
            value=0.5,
            step=0.1,
            help="낮을수록 일관성 있고, 높을수록 창의적인 응답을 생성합니다"
        )
        
        # Max tokens input
        max_tokens = st.number_input(
            "Max Tokens (최대 토큰 수)",
            min_value=1,
            max_value=4096,
            value=1024,
            step=100,
            help="한 번의 응답에서 생성할 최대 토큰 수입니다"
        )
    
    # Clear chat button
    if st.button("💬 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not openai_api_key:
    st.info("왼쪽 사이드바에서 OpenAI API 키를 입력하고 모델을 설정하세요. 🗝️", icon="ℹ️")
else:
    try:
        # Create an OpenAI client.
        client = OpenAI(api_key=openai_api_key)

        # Initialize session state variables
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "operation_type" not in st.session_state:
            st.session_state.operation_type = None
        if "difficulty_level" not in st.session_state:
            st.session_state.difficulty_level = None
        if "quiz_started" not in st.session_state:
            st.session_state.quiz_started = False

        # Show operation and difficulty selection screen if quiz hasn't started
        if not st.session_state.quiz_started:
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📚 연산 유형 선택")
                operation_choice = st.radio(
                    "어떤 연산을 공부하고 싶니?",
                    ["➕ 덧셈", "➖ 뺄셈", "✖️ 곱셈", "➗ 나눗셈", "🎲 섞어서!"],
                    label_visibility="collapsed"
                )
            
            with col2:
                st.subheader("⭐️ 난이도 선택")
                difficulty_choice = st.radio(
                    "난이도를 선택해 줄래?",
                    ["🟢 쉬움 (1~20)", "🟡 보통 (1~100)", "🔴 어려움 (1~1000)"],
                    label_visibility="collapsed"
                )
            
            if st.button("🚀 시작하기!", use_container_width=True, type="primary"):
                st.session_state.operation_type = operation_choice
                st.session_state.difficulty_level = difficulty_choice
                st.session_state.quiz_started = True
                # Initialize messages
                st.session_state.messages = []
                st.rerun()
        
        else:
            # Quiz has started, show chat interface
            st.divider()
            
            # Display selected options
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**연산 유형**: {st.session_state.operation_type}")
            with col2:
                st.info(f"**난이도**: {st.session_state.difficulty_level}")
            
            # Update system prompt with selected operation and difficulty
            operation_info = f"선택된 연산 유형: {st.session_state.operation_type}\n선택된 난이도: {st.session_state.difficulty_level}"
            
            enhanced_system_prompt = system_prompt + f"\n\n{operation_info}"
            
            # If this is the first message, generate initial greeting from bot
            if len(st.session_state.messages) == 0:
                try:
                    initial_prompt = "퀴즈를 시작할까?"
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": enhanced_system_prompt},
                            {"role": "user", "content": initial_prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                    )
                    
                    with st.chat_message("assistant"):
                        response = st.write_stream(stream)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"초기 메시지 생성 중 오류가 발생했습니다: {str(e)}")
            
            else:
                # Display the existing chat messages via `st.chat_message`.
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Create a chat input field to allow the user to enter a message.
            if prompt := st.chat_input("답을 입력하세요..."):

                # Store and display the current prompt.
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                try:
                    # Generate a response using the OpenAI API.
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": enhanced_system_prompt},
                            *[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages[:-1]
                            ]
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                    )

                    # Stream the response to the chat using `st.write_stream`, then store it in 
                    # session state.
                    with st.chat_message("assistant"):
                        response = st.write_stream(stream)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"응답 생성 중 오류가 발생했습니다: {str(e)}")
    
    except Exception as e:
        st.error(f"API 키가 유효하지 않거나 오류가 발생했습니다: {str(e)}")
