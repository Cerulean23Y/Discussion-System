import streamlit as st
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
import hmac  # 修复 hmac 未导入问题

# ===== 系统配置 =====
DATA_DIR = Path(__file__).parent / "persistent_data"
SUBMISSION_FILE = DATA_DIR / "submissions.json"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

# ===== 数据管理层 =====
class DataManager:
    def __init__(self):
        self._init_storage()
        
    def _init_storage(self):
        """初始化存储目录"""
        try:
            DATA_DIR.mkdir(exist_ok=True)
            if not SUBMISSION_FILE.exists():
                with open(SUBMISSION_FILE, "w") as f:
                    json.dump({}, f)
        except PermissionError as e:
            st.error(f"🛑 存储初始化失败: {str(e)}")
            st.stop()

    def load_all(self):
        """加载全部数据"""
        try:
            with open(SUBMISSION_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("📄 数据格式错误，请检查存储文件")
            return {}
        except Exception as e:
            st.error(f"💔 操作失败: {str(e)}")
            return {}

    def save_all(self, data):
        """保存全部数据"""
        try:
            with open(SUBMISSION_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except json.JSONDecodeError:
            st.error("📄 数据格式错误，请检查存储文件")
            return {}
        except Exception as e:
            st.error(f"💔 操作失败: {str(e)}")
            return {}

    def get_recent_submissions(self, days=7):
        """获取近一周内的提交记录"""
        data = self.load_all()
        recent_dates = [date for date in data.keys() if datetime.strptime(date, DATE_FORMAT) >= datetime.now() - timedelta(days=days)]
        recent_submissions = {date: data[date] for date in recent_dates}
        return recent_submissions

    def update_submission(self, user, progress, question):
        """更新同学提交记录"""
        data = self.load_all()
        today = datetime.now().strftime(DATE_FORMAT)
        data.setdefault(today, {})
        
        cleaned_data = {
            "progress": progress.strip() if progress else "",
            "question": question.strip() if question else "",
            "timestamp": datetime.now().strftime(TIME_FORMAT)
        }
        
        data[today][user] = cleaned_data
        self.save_all(data)

# ===== 认证管理层 =====
class AuthManager:
    def __init__(self):
        self.admin_pwd = self._get_admin_password()
        
    def _get_admin_password(self):
        """获取管理员密码"""
        try:
            return st.secrets["server"]["ADMIN_PWD"]
        except (FileNotFoundError, KeyError):
            return os.getenv("ADMIN_PWD", "eepsadmin")

    def validate_password(self, input_pwd):
        """安全验证密码"""
        return hmac.compare_digest(input_pwd, self.admin_pwd)

# ===== 会话状态管理 =====
class SessionStateManager:
    def __init__(self):
        self._initialize_states()
        
    def _initialize_states(self):
        """初始化所有会话状态"""
        states = {
            "is_admin": False,
            "selected_user": None,
            "form_data": None,
            "submission_success": False
        }
        for state, default in states.items():
            if state not in st.session_state:
                st.session_state[state] = default

    def set_submission_success(self, success):
        """设置提交成功状态"""
        st.session_state.submission_success = success

    def clear_form_data(self):
        """清除表单数据"""
        st.session_state.form_data = None

# ===== 页面组件 =====
def render_login_form(auth_manager):
    """渲染管理员登录表单"""
    with st.sidebar:
        st.header("🔒 管理员登录")
        pwd_input = st.text_input("密码", type="password", key="admin_pwd")
        
        login_btn = st.button("登录", key="admin_login")
        if login_btn:
            if auth_manager.validate_password(pwd_input):
                st.session_state.is_admin = True
                st.success("✅ 登录成功！")
                st.rerun()
            else:
                st.error("❌ 密码错误！")

def render_submission_form(data_manager, session_manager):
    """渲染同学提交表单"""
    # 提交成功状态显示
    submission_success = st.session_state.submission_success
    if submission_success:
        st.header("📝 提交成功！")
        st.write("您的提交已成功接收！")
        
        # 操作按钮
        col1, col2 = st.columns([1, 1])
        with col1:
            st.button("🔄 重新提交", 
                       key="resubmit_btn",
                       on_click=lambda: session_manager.set_submission_success(False))
        with col2:
            st.button("🏠 返回首页", 
                       key="home_btn",
                       on_click=lambda: st.experimental_rerun())
        return
    
    # 表单提交
    st.header("📝 同学提交")
    with st.form("submission_form"):
        user = st.text_input("姓名", key="user_name").strip()
        progress = st.text_area("本周工作进展", height=150, key="progress_input")
        question = st.text_area("遇到的问题", height=150, key="question_input")
        
        submit_btn = st.form_submit_button("提交")
        if submit_btn:
            if user and progress and question:
                data_manager.update_submission(user, progress, question)
                session_manager.set_submission_success(True)  # 设置提交成功状态
            else:
                st.warning("⚠️ 请填写所有字段")

def render_admin_panel(data_manager):
    """渲染管理员控制台"""
    st.sidebar.button("退出管理", key="logout_btn", on_click=lambda: st.session_state.clear())
    
    tab1, tab2 = st.tabs(["🎲 随机抽检", "📅 历史查询"])
    
    # 随机抽检模块
    with tab1:
        recent_submissions = data_manager.get_recent_submissions(days=7)
        random_btn = st.button("随机抽取", key="random_pick")
        if random_btn:
            if not recent_submissions:
                st.warning("⚠️ 近一周内无提交记录")
                return
            selected_date = random.choice(list(recent_submissions.keys()))
            selected_user = random.choice(list(recent_submissions[selected_date].keys()))
            st.session_state.selected_user = (selected_date, selected_user)
            st.rerun()
        
        if st.session_state.get("selected_user"):
            selected_date, selected_user = st.session_state.selected_user
            user_data = recent_submissions[selected_date][selected_user]
            st.subheader(f"👤 {selected_user} 的提交")
            st.write(f"**日期**: {selected_date}")
            st.write(f"**进度*: {user_data['progress']}")
            st.write(f"**问题*: {user_data['question']}")

    # 历史查询模块
    with tab2:
        st.subheader("📅 近一周内的提交记录")
        recent_submissions = data_manager.get_recent_submissions(days=7)
        for date, submissions in recent_submissions.items():
            with st.expander(f"{date} 的提交"):
                for username, data in submissions.items():
                    st.write(f"**同学**: {username}")
                    st.write(f"**进度*: {data['progress']}")
                    st.write(f"**问题*: {data['question']}")
                    st.write("---")

# ===== 主程序 =====
def main():
    # 初始化页面配置
    st.set_page_config(
        page_title="🔬 EEPS科研讨论小程序",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 添加主页面标题
    st.title("EEPS科研讨论小程序")

    data_manager = DataManager()
    auth_manager = AuthManager()
    session_manager = SessionStateManager()
    
    # 路由控制
    if st.session_state.is_admin:
        render_admin_panel(data_manager)
    else:
        render_login_form(auth_manager)
        render_submission_form(data_manager, session_manager)

if __name__ == "__main__":
    main()
