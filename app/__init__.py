import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

if __name__ == "__main__":
    app.run()

@app.route('/')
def index():
    hobbies = [
       {
        "description" : "I have been powerlifting since 2022 and had my first competition in April 2024. I held 3 state records for my weight class. Since then I have been steadily increasing my total. Check out my page on openpowerlifting.com.",
        "img" : "/static/img/meet.jpg",
       },
       {
        "description" : "I enjoy playing video games, most notably platform or 2D fighting games, I've always enjoyed learning combos and picking up tendencies to adapt.",
        "img" : "/static/img/game.jpeg",
       },
       {
        "description" : "I am also an avid music enjoyer, I listen to R&B, different variations of Pop, and more recently Samba.",
        "img" : "/static/img/spotify.png",
       }
    ]
    return render_template('index.html', title="Conrad's Portfolio", url=os.getenv("URL"), hobbies=hobbies)

@app.route('/experience')
def experience():
    title = "Conrad Uyakonwu's Portfolio"
    work_experiences = [
        {
            "title": "System Administrator & AI/ML Co-Manager",
            "company": "Computer Science Instructional Lab (CSIL)",
            "description": "Co-managed a 6-member internal AI/ML team, planned sprints in Trello and maintained project docs on our wiki. Developed AI/ML infrastructure using Python and Vector Databases; integrated APIs for real-time natural language processing. Built dashboards to visualize 8 years of equipment-checkout logs, uncovering peak demand hours and trained a model to predict late returns.",
            "duration": "March 2024 - Present"
        },
        {
            "title": "Software Engineer Intern",
            "company": "BILL",
            "description": "Engineered scalable backend data infrastructure using AWS Glue and Airflow; optimized distributed systems processing to reduce incident latency by 50%. Architected a generative AI-powered anomaly detection system using AWS Bedrock, which automatically identified and flagged critical issues, projecting a savings of over 1,000 engineering hours annually (valued at >$100,000). Reduced incident response time by 66% and eliminated manual reporting errors by automating report generation and delivery every 3-4 hours, increasing data platform team efficiency.",
            "duration": "June 2025 - August 2025"
        },
        {
            "title": "Production Engineer Intern",
            "company": "Meta x Major League Hacking Fellowship",
            "description": "Selected as 1 of 44 fellows from over 4,000 applicants (< top 1.1%) to work with Meta. Executed Site Reliability Engineering (SRE) protocols, diagnosing Linux kernel and networking bottlenecks to ensure system stability. Engineered an open-source web app using Python, Flask, and MySQL, to manage back-end website development. Designed microservices architecture and CI/CD pipelines in Docker; automated QA/testing workflows to cut deployment time by 80%.",
            "duration": "June 2024 - September 2024"
        },
        {
            "title": "Command Data Handler",
            "company": "NASA L'Space MCA",
            "description": "Acquired mission development skills under guidance of NASA engineers to contribute and present a rover design. Led the CDH design for an exploration mission, collaborating with a multidisciplinary team for lunar data handling. Conducted critical research for a rover, identifying optimal parts to withstand the extreme conditions of the Moon. Authored key sections of the team's final report, synthesizing foundational data for further mission planning. Authored and contributed to the team’s final technical report and presentation.",
            "duration": "May 2024 - August 2024"
        },
        {
            "title": "Curriculum Development Engineer",
            "company": "Code Your Dreams",
            "description": "Led the creation of an AI curriculum on WhatsApp Integration, managing a team of 3 interns to deliver content. Created a comprehensive 15-hour AI development course, which was successfully delivered to 25+ Teachers. Developed a WhatsApp Chatbot in Python to bypass regional ChatGPT blocks, improving global accessibility.",
            "duration": "June 2023 - August 2023"
        }
    ]

    education = [
        {
            "degree": "B.A. and M.S. in Computer Science",
            "institution": "University of Chicago",
            "description": "Questbridge and Odyssey Scholar. Specializing in Machine Learning.",
            "year": "Expected August 2026"
        },
        {
            "degree": "IB Career Program in Computer Science",
            "institution": "Watkins Mill High School",
            "description": "Unweighted GPA: 3.93",
            "year": "2018 - 2022"
        }
    ]
    return render_template('experience.html', title=title, work_experiences=work_experiences, education=education,)



import sqlite3
import numpy as np

def get_age_class(age):
    if 14 <= age <= 18: return 'Sub-Junior'
    elif 19 <= age <= 23: return 'Junior'
    elif 24 <= age <= 39: return 'Open'
    elif 40 <= age <= 49: return 'Master 1'
    elif 50 <= age <= 59: return 'Master 2'
    elif 60 <= age <= 69: return 'Master 3'
    elif age >= 70: return 'Master 4'
    else: return 'Guest'

def calculate_percentile(user_val, data_list):
    clean_data = [x[0] for x in data_list if x[0] is not None and x[0] > 0]
    if not clean_data: return 0.0
    return sum(1 for x in clean_data if x < user_val) / len(clean_data) * 100

def get_clean_goals(current_percentile, data_list):
    clean_data = [x[0] for x in data_list if x[0] is not None and x[0] > 0]
    if not clean_data: return {}

    steps_5 = list(range(5, 100, 5))
    candidates = [p for p in steps_5 if p > current_percentile]
    if len(candidates) < 4:
        steps_2_5 = np.arange(0, 100, 2.5)
        candidates = [p for p in steps_2_5 if p > current_percentile]

    selected_percentiles = candidates[:4]
    if not selected_percentiles:
        return {"100% (WR)": max(clean_data)}

    values = np.percentile(clean_data, selected_percentiles)

    dist_dict = {}
    for p, v in zip(selected_percentiles, values):
        dist_dict[f"{p:g}th Percentile"] = v
    dist_dict["World Record"] = max(clean_data)
    return dist_dict

@app.route('/powerlifting', methods=['GET', 'POST'])
def powerlifting():
    results = None
    if request.method == 'POST':
        try:
            sex = request.form.get('sex', 'M')
            age = float(request.form.get('age', 21))
            weight_class = request.form.get('weight_class', '120')
            squat = float(request.form.get('squat', 0))
            bench = float(request.form.get('bench', 0))
            deadlift = float(request.form.get('deadlift', 0))
            total = squat + bench + deadlift

            form_state = {
                'sex': sex,
                'age': age,
                'weight_class': weight_class,
                'squat': squat,
                'bench': bench,
                'deadlift': deadlift
            }

            target_age_class = get_age_class(age)
            age_definitions = {
                'Sub-Junior': (14, 18), 'Junior': (19, 23), 'Open': (24, 39),
                'Master 1': (40, 49), 'Master 2': (50, 59), 'Master 3': (60, 69), 'Master 4': (70, 99)
            }

            min_age, max_age = age_definitions.get(target_age_class, (0, 999))

            # DB queries
            db_path = os.path.join(os.path.dirname(__file__), 'openpowerlifting.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Global
            cursor.execute("SELECT Best3SquatKg FROM lifters WHERE WeightClassKg = ? AND Sex = ?", (weight_class, sex))
            global_squat_data = cursor.fetchall()

            cursor.execute("SELECT Best3BenchKg FROM lifters WHERE WeightClassKg = ? AND Sex = ?", (weight_class, sex))
            global_bench_data = cursor.fetchall()

            cursor.execute("SELECT Best3DeadliftKg FROM lifters WHERE WeightClassKg = ? AND Sex = ?", (weight_class, sex))
            global_deadlift_data = cursor.fetchall()

            cursor.execute("SELECT TotalKg FROM lifters WHERE WeightClassKg = ? AND Sex = ?", (weight_class, sex))
            global_total_data = cursor.fetchall()

            # Age specific
            cursor.execute("SELECT Best3SquatKg FROM lifters WHERE WeightClassKg = ? AND Sex = ? AND Age >= ? AND Age <= ?", (weight_class, sex, min_age, max_age))
            age_squat_data = cursor.fetchall()

            cursor.execute("SELECT Best3BenchKg FROM lifters WHERE WeightClassKg = ? AND Sex = ? AND Age >= ? AND Age <= ?", (weight_class, sex, min_age, max_age))
            age_bench_data = cursor.fetchall()

            cursor.execute("SELECT Best3DeadliftKg FROM lifters WHERE WeightClassKg = ? AND Sex = ? AND Age >= ? AND Age <= ?", (weight_class, sex, min_age, max_age))
            age_deadlift_data = cursor.fetchall()

            cursor.execute("SELECT TotalKg FROM lifters WHERE WeightClassKg = ? AND Sex = ? AND Age >= ? AND Age <= ?", (weight_class, sex, min_age, max_age))
            age_total_data = cursor.fetchall()

            conn.close()

            # Format data
            results = {
                'squat': {
                    'val': squat,
                    'global_pct': calculate_percentile(squat, global_squat_data),
                    'age_pct': calculate_percentile(squat, age_squat_data),
                    'goals': get_clean_goals(calculate_percentile(squat, age_squat_data), age_squat_data)
                },
                'bench': {
                    'val': bench,
                    'global_pct': calculate_percentile(bench, global_bench_data),
                    'age_pct': calculate_percentile(bench, age_bench_data),
                    'goals': get_clean_goals(calculate_percentile(bench, age_bench_data), age_bench_data)
                },
                'deadlift': {
                    'val': deadlift,
                    'global_pct': calculate_percentile(deadlift, global_deadlift_data),
                    'age_pct': calculate_percentile(deadlift, age_deadlift_data),
                    'goals': get_clean_goals(calculate_percentile(deadlift, age_deadlift_data), age_deadlift_data)
                },
                'total': {
                    'val': total,
                    'global_pct': calculate_percentile(total, global_total_data),
                    'age_pct': calculate_percentile(total, age_total_data),
                    'goals': get_clean_goals(calculate_percentile(total, age_total_data), age_total_data)
                },
                'age_class': target_age_class
            }

        except Exception as e:
            results = {'error': str(e)}

    return render_template(
        'powerlifting.html',
        results=results,
        title="Live Project: IPF Percentile Calculator",
        form_state=form_state if request.method == 'POST' else None
    )
