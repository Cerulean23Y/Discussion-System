import streamlit as st
import json
import os
from datetime import datetime
import random
from pathlib import Path

# ===== 系统配置 =====
PERSISTENT_DIR = Path(__file__).parent / "persistent_data"  # 持久化目录
SUBMISSION_FILE = PERSISTENT_DIR / "submissions.json"      # 数据文件
ADMIN_PWD = "eepsadmin123"  # 建议部署时通过Streamlit Secrets设置

# ===== 初始化存储 =====
def init_storage():
    """创建持久化目录和文件"""
    PERSISTENT_DIR.mkdir(exist_ok=True)
    if not SUBMISSION_FILE.exists():
        with open(SUBMISSION_FILE, "w") as f:
            json.dump({}, f)

# ===== 数据操作 =====
def load_data():
    """加载全部数据"""
    with open(SUBMISSION_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """保存全部数据"""
    with open(SUBMISSION_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_today_submissions():
    """获取当日提交"""
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    return data.get(today, {})

def update_submission(user, progress, question):
    """更新用户提交"""
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today not in data:
        data[today] = {}
    
    data[today][user] = {
        "progress": progress,
        "question": question,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    
    save_data(data)

# ===== 页面组件 =====
def user_submission_page():
    """用户提交界面"""
    st.header("📝 每周进展提交")
    
    with st.form("submission_form"):
        user = st.text_input("姓名", key="user_name").strip()
        progress = st.text_area("本周工作进展", height=150)
        question = st.text_area("遇到的问题", height=150)
        
        if st.form_submit_button("提交"):
            if user and progress and question:
                update_submission(user, progress, question)
                st.success("✅ 提交成功！可重复提交更新内容")
            else:
                st.warning("⚠️ 请填写所有字段")

def admin_dashboard():
    """管理员控制台"""
    st.sidebar.button("退出管理", on_click=lambda: st.session_state.clear())
    
    # 功能导航
    tab1, tab2 = st.tabs(["🎲 随机抽取", "📅 历史查询"])
    
    with tab1:
        today_sub = get_today_submissions()
        if st.button("随机抽取"):
            if today_sub:
                user = random.choice(list(today_sub.keys()))
                st.session_state.selected_user = user
        if "selected_user" in st.session_state:
            data = today_sub[st.session_state.selected_user]
            st.subheader(f"{st.session_state.selected_user} 的提交")
            st.write("**进展**", data["progress"])
            st.write("**问题**", data["question"])
    
    with tab2:
        all_data = load_data()
        dates = sorted(all_data.keys(), reverse=True)
        selected_date = st.selectbox("选择日期", dates)
        
        if selected_date:
            st.write(f"### {selected_date} 提交情况")
            for user, data in all_data[selected_date].items():
                with st.expander(user):
                    st.write("进展：", data["progress"])
                    st.write("问题：", data["question"])

# ===== 主程序 =====
def main():
    init_storage()
    st.set_page_config(page_title="EEPS管理系统", layout="wide")
    st.title("🔬 课题组管理系统")
    
    # 管理员登录
    if not hasattr(st.session_state, "is_admin"):
        with st.sidebar:
            st.header("管理员登录")
            pwd = st.text_input("密码", type="password")
            if st.button("登录"):
                if pwd == ADMIN_PWD:
                    st.session_state.is_admin = True
                    st.experimental_rerun()
                else:
                    st.error("密码错误")
    
    # 页面路由
    if st.session_state.get("is_admin"):
        admin_dashboard()
    else:
        user_submission_page()

if __name__ == "__main__":
    main()