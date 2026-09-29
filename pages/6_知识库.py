import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content.knowledge import KNOWLEDGE

st.set_page_config(page_title="知识库", page_icon="📚", layout="wide")
from core.session import require_login
require_login()
st.title("📚 知识库")
st.caption("飞机总体设计的基本公式和概念")

titles = list(KNOWLEDGE.keys())
selected = st.sidebar.radio("选择章节", titles)

st.subheader(selected)
st.markdown(KNOWLEDGE[selected])

st.divider()
st.caption("💡 阅读完公式后，去对应的计算页面动手验证。")