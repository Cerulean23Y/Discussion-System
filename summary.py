import streamlit as st
import os
from datetime import datetime

# 初始化文件路径
submissions_dir = "submissions"

# 获取文件名列表
def get_file_list(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

# 解析文件名中的日期
def parse_date_from_filename(filename, year):
    try:
        # 假设文件名格式为 "0307.md"，即两位数日期
        date_str = filename.split('.')[0]
        return datetime.strptime(f"{year}-{date_str}", "%Y-%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return None

# 读取文件内容
def read_submission_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 解析文件内容
def parse_submissions(content):
    submissions = []
    lines = content.split('\n')
    current_student = None
    progress = []
    questions = []
    for line in lines:
        if line.startswith("同学: "):
            if current_student:
                submissions.append({"name": current_student, "progress": progress, "questions": questions})
            current_student = line.split(": ")[1]
            progress = []
            questions = []
        elif line.startswith("*进度: "):
            progress.append(line[4:].strip())
        elif line.startswith("*问题: "):
            questions.append(line[4:].strip())
    if current_student:
        submissions.append({"name": current_student, "progress": progress, "questions": questions})
    return submissions

# 主页面
def main():
    st.title("EEPS小组讨论系统 - 周汇总")
    
    # 获取文件列表并解析日期
    files = get_file_list(submissions_dir)
    current_year = datetime.now().year
    file_dates = {parse_date_from_filename(f, current_year): f for f in files if parse_date_from_filename(f, current_year)}
    
    # 检查是否有可展示的文件
    if not file_dates:
        st.error("未找到任何提交文件。")
        return
    
    # 用户选择日期
    selected_date = st.selectbox("选择日期", list(file_dates.keys()))
    
    # 读取并展示选定日期的文件内容
    file_name = file_dates.get(selected_date)
    if file_name:
        file_path = os.path.join(submissions_dir, file_name)
        content = read_submission_file(file_path)
        submissions = parse_submissions(content)

        # 展示每个同学的进度和问题
        for submission in submissions:
            st.markdown(f"### **同学: {submission['name']}**")
            if submission["progress"]:
                st.markdown(" **进度**:")
                for progress in submission["progress"]:
                    st.markdown(f"- {progress}")
            else:
                st.markdown(" **进度**: 无")
            if submission["questions"]:
                st.markdown(" **问题**:")
                for question in submission["questions"]:
                    st.markdown(f"- {question}")
            else:
                st.markdown(" **问题**: 无")
    else:
        st.warning("未找到所选日期的文件。")

if __name__ == "__main__":
    main()
