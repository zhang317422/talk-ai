import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests  # 导入网络请求库，用来连接后端

# 1. 网页基础配置（必须写在最前面）
st.set_page_config(page_title="AI口语教练", layout="wide")

# 配置后端接口地址
BACKEND_URL = "http://localhost:8000/api/tutor"

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

# 4. 网页底部的录音按钮（保留作为前端界面展示）
st.write("👇 可以通过下方按钮录音，或在最底部输入框直接打字：")
audio = mic_recorder(
    start_prompt="🎵 开始录音",
    stop_prompt="🛑 停止录音",
    key='web_recorder'
)

# 录音成功后的前端交互测试
if audio:
    st.success("✅ 前端已成功监听到录音，音频字节大小：" + str(len(audio['bytes'])))
    st.info("提示：语音识别（STT）接口对接中，请先在下方输入框打字进行对话测试哦！")


# 5. 核心融合：聊天输入框与后端请求
# st.chat_input 会在网页最底部生成一个标准的聊天输入框
if user_input := st.chat_input("Say something in English..."):
    
    # 5.1 把用户说的话存入历史记录，并在前端渲染出来
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    # 5.2 向搭档的 FastAPI 后端发送请求
    with st.chat_message("assistant"):
        with st.spinner("AI 正在思考中..."):
            try:
                # 发送 POST 请求，把用户的话传给后端
                response = requests.post(
                    BACKEND_URL,
                    json={"message": user_input},  # 这里对应的键名 "message" 要看搭档后端的定义
                    timeout=10 # 设置10秒超时
                )
                
                if response.status_code == 200:
                    # 5.3 解析后端返回的 AI 回复
                    # 注意：如果搭档返回的 JSON 格式不是 {"reply": "..."}, 
                    # 比如是 {"response": "..."}，需要把下面的 "reply" 换掉
                    ai_reply = response.json().get("reply", "未能在后端返回中找到 reply 字段")
                    
                    # 展示 AI 回复并存入历史记录
                    st.write(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                else:
                    st.error(f"后端服务器报错，状态码: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务器！请确保运行后端的那个终端窗口没关，且运行在 8000 端口。")
            except Exception as e:
                st.error(f"发生未知错误: {e}")