import streamlit as st
from streamlit_mic_recorder import mic_recorder

# 1. 网页基础配置（必须写在最前面）
st.set_page_config(page_title="AI口语教练", layout="wide")

# 2. 网页左侧：控制面板
with st.sidebar:
    st.title("🛠️ 教学控制台")
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

# 4. 网页底部的录音按钮
st.write("👇 请在网页端点击并开始练习吧：")
audio = mic_recorder(
    start_prompt="🎵 开始录音",
    stop_prompt="🛑 停止录音",
    key='web_recorder'
)

# 5. 录音成功后的前端交互测试
if audio:
    st.success("✅ 前端已成功监听到录音，音频字节大小：" + str(len(audio['bytes'])))
