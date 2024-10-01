import streamlit as st
import git
from datetime import datetime, time
import shutil
import tempfile
import math
import os
import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
from zipfile import ZipFile
import fitz


def get_last_push_time(repo_url):
    repo_dir = tempfile.mkdtemp()
    repo = None

    try:
        # Clone the repository using the provided username and token for authentication
        repo = git.Repo.clone_from(
            repo_url, 
            repo_dir, 
            # env={'GIT_ASKPASS': 'echo', 'GIT_USERNAME': GITHUB_USERNAME, 'GIT_PASSWORD': GITHUB_TOKEN}
        )
        tree = repo.tree()
        latest_commit_time = None
        for blob in tree:
            commit = next(repo.iter_commits(paths=blob.path, max_count=1))
            commit_time = datetime.fromtimestamp(commit.committed_date)
            if latest_commit_time is None or commit_time > latest_commit_time:
                latest_commit_time = commit_time

        return latest_commit_time if latest_commit_time else None

    except git.exc.GitCommandError as e:
        if 'Repository not found' in str(e):
            return "Invalid URL, please try again."
        else:
            return f"An error occurred: {e}"

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        if repo:
            repo.close()
        try:
            shutil.rmtree(repo_dir, ignore_errors=True)
        except Exception as cleanup_error:
            print(f"Failed to delete temporary directory: {cleanup_error}")

def penalty_points(diff_hrs):
    if diff_hrs < 24 and diff_hrs > 0:
        late_point_penalty = math.ceil(diff_hrs)
        return late_point_penalty
    elif diff_hrs < 0:
        return 0
    elif diff_hrs > 24 and diff_hrs < 72:
        return 24
    else:
        return "Full Grade Cut"

def parse_date_time(date_str, time_str, date_format="%Y-%m-%d", time_format="%H:%M"):
    date = datetime.strptime(date_str, date_format).date()
    time = datetime.strptime(time_str, time_format).time()
    return datetime.combine(date, time)

def get_last_push(github_url, due_date, due_time):
    due_datetime = parse_date_time(date_str=due_date, time_str=due_time)
    last_push_time = get_last_push_time(github_url)
    if isinstance(last_push_time, datetime):
        time_difference = last_push_time - due_datetime
        hours_difference = time_difference.total_seconds() / 3600
        points_deducted = penalty_points(hours_difference)
        return last_push_time, points_deducted
    else:
        return last_push_time, "Error in processing URL"

def load_excel_data():
    # Load student names and generate an id-to-name mapping
    names_list = [
    "Abam, Brianna",
    "Ali, Jonathan",
    "Allen, Michael",
    "Alrayes, Ibrahim",
    "Atkuri, Venkata",
    "Baldonado, Micah",
    "Barkley, Jesse",
    "Baron, William",
    "Bobde, Yash Bobde",
    "Botcha, Suraj",
    "Chavarkar, Bhargavee",
    "Chen, Chi-yeh",
    "Chen, Phyllis",
    "Chen, Ruike",
    "Chermak, Nick",
    "Dai, Ruiyang",
    "Desai, Aadesh",
    "Dhanwal, Akanksha",
    "Dughyala, Nimisha",
    "Durham, Virginia",
    "Fan, Yuxiang",
    "Gauchat, Peter",
    "Graves, Reid",
    "Guo, Justin",
    "Guo, Yutong",
    "He, Jonathan",
    "He, Kristy",
    "He, Lyuxing",
    "Huang, Lenka",
    "Hung, Ya-En",
    "Jain, Arav",
    "Jangabyl, Janbol",
    "Joshi, Anirudh",
    "Joshi, Rutvik",
    "Karthikeyakannan, Madhav",
    "Krishnan, Shawn",
    "Kulkarni, Eesha",
    "Kumar, Prajwal",
    "Lai, Cheng-kai",
    "Li, Yi",
    "Li, Yue",
    "Li, Yuxiao",
    "Lin, Cheng-De",
    "Liu, Jiayi",
    "Liu, Wei",
    "Long, Feiyang",
    "Luo, Yinyi",
    "Lyu, Naixin",
    "Madan Gopal, Anusha",
    "Mahavir Prasad, .",
    "Malreddy, Abhishek Reddy",
    "Mandyam, Rishi",
    "Manheimer, Hannah",
    "Modh, Jainam",
    "Molugu, Gaurav",
    "Mu, Rong",
    "Naito, Katsuhiko",
    "Nemala, Vaisnavi",
    "Ni, Yichen",
    "Pagaria, Shreya",
    "Pang, Yuyang",
    "Park, Jonathan",
    "Qin, Cheng",
    "Ramadasan, Manigandan",
    "Ren, Yifei",
    "Roberts, Jonathan",
    "Robinson, Myles",
    "Rosario, Jason",
    "Sakhale, Yash",
    "Samanta, Ritarka",
    "Sarac, Pelinsu",
    "Shandilya, Aryaman",
    "Sharma, Jayant",
    "Shen, Anthony",
    "Shen, Jiyun",
    "Singh, Rohan",
    "Smayra, Sami",
    "Song, Leiran",
    "Srinivasan, Samhitha",
    "Stack, Trevor",
    "Su, Yue",
    "Suresh, Saadhikha Shree",
    "Takham, Kitiyaporn",
    "Tan, Eric",
    "Tan, Rolian",
    "Tang, Jonathan",
    "Thammineni, Swaroop",
    "Vigano, Andrea",
    "Vijaywargi, Jeet",
    "Villavicencio Garduno, Nicole",
    "Wang, An",
    "Wang, Yifan",
    "Wicklund, Dani",
    "Wu, Eric",
    "Wu, Timothy",
    "Wu, Yunhuan",
    "Xu, Junyi",
    "Xu, Lixin",
    "Xu, Yuan",
    "Xu, Zach",
    "Yang, Jieling",
    "Yang, Mengchu",
    "Yao, Daren",
    "Yu, Helen",
    "Yu, Junpu",
    "Yu, Yue",
    "Yuan, Enze",
    "Yuan, Jinsong",
    "Zeng, Tong",
    "Zhang, Shibo",
    "Zhang, Zane",
    "Zhang, Zeyang",
    "Zhao, Eric",
    "Zhao, Tunan",
    "Zheng, Zero",
    "Zhou, Zhexian",
    "Zhuang, Shiao"
]
    id_to_name = {}
    for name in names_list:
        file_name = re.sub(r'[^a-zA-Z]', '', name).lower()
        id_to_name[file_name] = name
    return id_to_name

def is_valid_url(url):
    return isinstance(url, str) and (url.startswith("http://") or url.startswith("https://"))

def search_in_html(html_path):
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            meta_url = soup.find('meta', attrs={'http-equiv': 'Refresh'})
            if meta_url:
                content = meta_url.get('content', '')
                match = re.search(r'url=([^"]+)', content)
                if match:
                    return match.group(1)

            anchor_tag = soup.find('a', href=True)
            if anchor_tag and 'github.com' in anchor_tag['href']:
                return anchor_tag['href']
    except Exception as e:
        print(f"Error processing HTML {html_path}: {e}")
        return "Error in HTML extraction"
    return "No URL Present"

def assign_tas_to_questions(questions, TAs):
    ta_assignments = {}
    ta_count = len(TAs)
    idx = 0
    
    for q_num, subs in questions.items():
        for sub in subs:
            question_key = f"Q{sub} - ({TAs[idx % ta_count]})"
            ta_assignments[f"Q{sub}"] = question_key
            idx += 1
            
    return ta_assignments

def process_files(directory, due_date, due_time, doc_type, excel_mapping, questions, ta_assignments):
    data = []
    andrew_id_list = []

    # Initialize columns with None for each question and subquestion using formatted headers
    columns = ['Name', 'GitHub URL', 'Last Push Time', 'Points Deducted'] + [ta_assignments[f"Q{sub}"] for i, subs in questions.items() for sub in subs]

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            andrew_id = filename.split('_')[0]
            andrew_id_list.append(andrew_id)
            if andrew_id in excel_mapping.keys():
                github_url = search_in_html(file_path)

                if github_url == "No URL Present" or not is_valid_url(github_url):
                    last_push_time = "Invalid or Missing URL"
                    points_deducted = ""
                else:
                    try:
                        last_push_time, points_deducted = get_last_push(github_url, due_date, due_time)
                    except:
                        last_push_time = "Not able to find"
                        points_deducted = "Recheck"

                row_data = {col: None for col in columns}
                row_data.update({
                    "Name": excel_mapping[andrew_id],
                    "GitHub URL": github_url,
                    "Last Push Time": last_push_time,
                    "Points Deducted": points_deducted
                })

                data.append(row_data)

    for i in excel_mapping.keys():
        if i not in andrew_id_list:
            row_data = {col: None for col in columns}
            row_data.update({
                "Name": excel_mapping[i],
                "GitHub URL": "",
                "Last Push Time": "",
                "Points Deducted": ""
            })
            data.append(row_data)

    df = pd.DataFrame(data)

    # Sort the DataFrame by the 'Name' column in ascending order
    df = df.sort_values(by='Name', ascending=True)

    # Assign formatted headers directly
    df.columns = ['Name', 'GitHub URL', 'Last Push Time', 'Points Deducted'] + [ta_assignments[f"Q{sub}"] for i, subs in questions.items() for sub in subs]

    return df

def main():
    st.title("Submissions Tracker - 14763/18763")

    st.sidebar.header("Manual Penalty Checker")
    github_url = st.sidebar.text_input("Enter GitHub URL")
    due_date_sidebar = st.sidebar.date_input("Enter Due Date", key="sidebar_due_date")
    due_time_sidebar = st.sidebar.time_input("Enter Due Time", value=time(0, 0), key="sidebar_due_time")

    if st.sidebar.button("Check Penalty"):
        if github_url:
            last_push_time, points_deducted = get_last_push(
                github_url, 
                due_date_sidebar.strftime("%Y-%m-%d"), 
                due_time_sidebar.strftime("%H:%M")
            )
            st.sidebar.write(f"Last Push Time: {last_push_time}")
            st.sidebar.write(f"Points Deducted: {points_deducted}")

    if st.sidebar.button("Rerun"):
        st.experimental_rerun()

    due_date = st.date_input("Enter Due Date", key="main_due_date")
    due_time = st.time_input("Enter Due Time", value=time(0, 0), key="main_due_time")

    num_questions = st.number_input("Enter the number of questions in the assignment", min_value=1, step=1)
    questions = {}
    for i in range(1, num_questions + 1):
        subquestions = st.text_input(f"Enter subquestions for question {i} (e.g., 1a,1b,1c):", value="", key=f"subquestion_{i}")
        subquestions_list = [sq.strip() for sq in subquestions.split(',') if sq.strip()]
        questions[i] = subquestions_list if subquestions_list else [str(i)]

    TAs = ['Shweta', 'Sreenidhi', 'Akshay', 'Kevin', 'Sai']
    ta_assignments = assign_tas_to_questions(questions, TAs)

    doc_type = st.selectbox("Select Document Type in Zip", ["pdf", "html"])
    uploaded_file = st.file_uploader("Upload a zip file containing submissions", type="zip")
    #excel_file = st.file_uploader("Upload Excel file with student data", type=["xlsx", "xls"])

    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            excel_mapping = load_excel_data()
            df = process_files(temp_dir, due_date.strftime("%Y-%m-%d"), due_time.strftime("%H:%M"), doc_type, excel_mapping, questions, ta_assignments)

            st.dataframe(df.style.hide(axis="index"))

            output_path = os.path.join(temp_dir, "output.xlsx")
            df.to_excel(output_path, index=False)  # Ensure index is excluded

            with open(output_path, "rb") as file:
                st.download_button(
                    label="Download Excel file",
                    data=file,
                    file_name="output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()
