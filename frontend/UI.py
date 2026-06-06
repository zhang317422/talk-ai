import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests

# 1. 网页基础配置（必须写在最前面）
st.set_page_config(page_title="AI口语教练", layout="wide")

# 核心升级：对接搭档的流式输出接口路径！
BACKEND_STREAM_URL = "http://localhost:8000/api/tutor/stream"

# 2. 网页左侧：控制面板
with st.sidebar:
    st.title("🛠️ 教学控制台")
    # 场景选择优化：直接联动后端
    scene = st.selectbox("🎯 选择练习场景", ["外企职场抗压", "雅思口语模拟", "深夜酒馆闲聊"])
    st.markdown("---")
    st.subheader("💡 实时语法纠错卡片")
    st.info("💡 提示：如果你卡壳了，在网页上直接说中文就行，AI 会教你地道表达！")

# 3. 网页右侧主界面：标题
st.title("🗣️ 无压力 AI 英语口语陪练")

# 初始化聊天记录（防止刷新网页时聊天内容消失）
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi there! Welcome to our session. Let's chat!"}]

# 在网页上渲染出历史聊天气泡
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

st.markdown("---")

# 4. 优化：使用 Tabs 将文字和语音完全隔离，彻底断绝“录音按钮刷新导致文字重复发送”的 Bug
tab1, tab2 = st.tabs(["⌨️ 键盘打字练习", "🎵 语音输入练习"])

with tab1:
    # 键盘打字输入
    user_input = st.chat_input("Say something in English...", key="text_chat_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()  # 立即刷新让用户说的话先上屏

with tab2:
    st.write("👇 点击下方按钮开始录音练习：")
    audio = mic_recorder(
        start_prompt="🎵 开始录音",
        stop_prompt="🛑 停止录音",
        key='web_recorder'
    )
    # 优化：使用 st.toast 代替原先卡在中间的绿色大 banner，视觉降噪
    if audio:
        st.toast("✅ 前端已成功监听到音频！", icon="🎚️")
        st.info("提示：语音识别（STT）接口对接中，请先在『键盘打字练习』标签页测试丝滑流式对话！")


# 5. 统一处理发送请求与流式生成（当最新的一条消息是用户发的时候触发）
if st.session_state.messages[-1]["role"] == "user":
    last_user_message = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        # 定义一个流式生成器函数，用来实时抓取后端蹦出来的字
        def response_generator():
            try:
                # 联动 scene 参数，并以流式（stream=True）向后端发请求
                response = requests.post(
                    BACKEND_STREAM_URL,
                    json={
                        "message": last_user_message,
                        "scene": scene
                    },
                    stream=True,
                    timeout=20
                )
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            # 解码并清洗数据
                            decoded_line = line.decode('utf-8').strip()
                            
                            # 过滤 SSE 前缀和无意义的控制行
                            if decoded_line.startswith("data:"):
                                decoded_line = decoded_line[5:].strip()
                            
                            if not decoded_line or decoded_line in ["[DONE]", "{", "}", ":"]:
                                continue
                            
                            # 💡 终极过滤逻辑：直接清除历史截图里出现过的所有干扰格式标志
                            clean_chunk = decoded_line
                            
                            # 强行剥离所有多余的包裹标签与结构噪音
                            for noise in ['"content"', '"reply"', 'content:', 'reply:', 'corrections:', '{', '}', '[', ']', '"', '\\', ':']:
                                clean_chunk = clean_chunk.replace(noise, '')
                            
                            # 处理可能混入的换行符和特殊的 Unicode 编码（如 emoji 碎裂编码）
                            clean_chunk = clean_chunk.replace('n', '').replace('ud83dude0a', '😊').strip()
                            
                            # 过滤掉属于语法纠错字段的数据碎屑，防止干扰普通对话
                            if clean_chunk in ['cor', 're', 'ctions', '']:
                                continue
                                
                            # 💡 还原打字机间距：如果是常见标点直接紧跟，如果是单词则追加合理的空格补位
                            if clean_chunk:
                                if clean_chunk in [".", ",", "!", "?", "—", "'s", "'ve", "'ll", "'d", "'m"]:
                                    yield clean_chunk
                                else:
                                    yield " " + clean_chunk
                                    
                else:
                    yield f"❌ 后端服务器报错，状态码: {response.status_code}"
            except requests.exceptions.ConnectionError:
                yield "❌ 无法连接到后端服务器！请确保后端的那个终端窗口没关。"
            except Exception as e:
                yield f"❌ 发生未知错误: {e}"

        # 使用 Streamlit 炫酷的 write_stream 功能，直接实现流畅的打字机蹦字效果！
        full_response = st.write_stream(response_generator())
        
        # 裁剪掉首句可能多出的前导空格
        full_response = full_response.strip()
        
        # 将 AI 最终蹦出来的完整话语存入历史记录，确保刷新不丢失
        st.session_state.messages.append({"role": "assistant", "content": full_response})