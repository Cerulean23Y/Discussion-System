import streamlit as st
import random
import json
import os
from datetime import datetime

# 获取当前日期，格式为 YYYY-MM-DD
current_date = datetime.now().strftime("%Y-%m-%d")

# 初始化问题存储文件路径
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)  # 创建 data 文件夹（如果不存在）
questions_file = os.path.join(data_dir, f"questions_{current_date}.json")

# 如果文件不存在，初始化为空字典
if not os.path.exists(questions_file):
    with open(questions_file, "w") as f:
        json.dump({}, f)

# 读取问题存储
def load_questions(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

# 保存问题
def save_questions(data, file_name):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)  # 添加缩进以便阅读
        
# 主页面
def main():
    st.title("EEPS小组讨论系统")
    st.write("欢迎使用EEPS小组讨论系统！")

    # 用户输入
    user_name = st.text_input("请输入你的名字：")
    progress = st.text_area("本周进展：")
    question = st.text_area("问题：")

    # 提交问题
    if st.button("提交进展和问题"):
        if user_name and progress and question:
            questions = load_questions(questions_file)
            questions[user_name] = {"progress": progress, "question": question}  # 覆盖该用户之前的内容
            save_questions(questions, questions_file)
            st.success("提交成功！")
        else:
            st.warning("请填写所有信息！")

    # 管理者模式
    if "manager_mode" not in st.session_state:
        st.session_state.manager_mode = False

    if st.sidebar.checkbox("管理模式", key="manager_mode_checkbox"):
        st.session_state.manager_mode = True
        password = st.sidebar.text_input("请输入密码：", type="password")
        if password == "eepstest":  # 简单的密码验证，实际使用中应更安全
            manager_page = st.sidebar.selectbox("选择页面", ["随机抽取讨论问题", "问题汇总"])
            
            if manager_page == "随机抽取讨论问题":
                st.subheader("随机抽取讨论问题")
                questions = load_questions(questions_file)
                if st.button("随机抽取讨论问题"):
                    if questions:
                        user = random.choice(list(questions.keys()))
                        st.success(f"随机抽取的讨论问题是 **{user}**！")
                        st.write(f"**{user}** 的进展和问题：")
                        st.write(f"进展：{questions[user]['progress']}")
                        st.write(f"问题：{questions[user]['question']}")
                    else:
                        st.warning("还没有人提交进展和问题！")
            
            elif manager_page == "问题汇总":
                st.subheader("问题汇总")
                all_dates = get_all_dates()
                selected_date = st.selectbox("选择日期", all_dates)
                selected_file = f"questions_{selected_date}.json"
                if os.path.exists(selected_file):
                    questions = load_questions(selected_file)
                    st.write(f"**{selected_date} 的进展和问题**：")
                    for user, data in questions.items():
                        st.write(f"**{user}**")
                        st.write(f"进展：{data['progress']}")
                        st.write(f"问题：{data['question']}")
                else:
                    st.warning("没有找到该日期的数据！")
        else:
            st.warning("密码错误！")
    else:
        st.session_state.manager_mode = False

if __name__ == "__main__":
    main()
