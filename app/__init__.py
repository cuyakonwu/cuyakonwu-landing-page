import os
import csv
import io
from datetime import datetime
import numpy as np
from scipy.stats import chi2
from scipy.optimize import minimize
from flask import Flask, render_template, request
from dotenv import load_dotenv

def huber_loss(residual, epsilon=1.35):
    abs_r = np.abs(residual)
    return np.where(abs_r <= epsilon, 0.5 * residual**2, epsilon * abs_r - 0.5 * epsilon**2)

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
            unit = request.form.get('unit', 'kg')
            age = float(request.form.get('age', 21))
            weight_class = request.form.get('weight_class', '120')
            squat = float(request.form.get('squat', 0))
            bench = float(request.form.get('bench', 0))
            deadlift = float(request.form.get('deadlift', 0))
            total = squat + bench + deadlift

            # Convert to kg for database calculations
            kg_mult = 1.0 if unit == 'kg' else 0.45359237
            lbs_mult = 1.0 if unit == 'kg' else 2.20462262

            squat_kg = squat * kg_mult
            bench_kg = bench * kg_mult
            deadlift_kg = deadlift * kg_mult
            total_kg = total * kg_mult

            form_state = {
                'sex': sex,
                'unit': unit,
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

            def convert_goals(goals_dict):
                return {k: v * lbs_mult for k, v in goals_dict.items()}

            # Format data
            results = {
                'unit': unit,
                'squat': {
                    'val': squat,
                    'global_pct': calculate_percentile(squat_kg, global_squat_data),
                    'age_pct': calculate_percentile(squat_kg, age_squat_data),
                    'goals': convert_goals(get_clean_goals(calculate_percentile(squat_kg, age_squat_data), age_squat_data))
                },
                'bench': {
                    'val': bench,
                    'global_pct': calculate_percentile(bench_kg, global_bench_data),
                    'age_pct': calculate_percentile(bench_kg, age_bench_data),
                    'goals': convert_goals(get_clean_goals(calculate_percentile(bench_kg, age_bench_data), age_bench_data))
                },
                'deadlift': {
                    'val': deadlift,
                    'global_pct': calculate_percentile(deadlift_kg, global_deadlift_data),
                    'age_pct': calculate_percentile(deadlift_kg, age_deadlift_data),
                    'goals': convert_goals(get_clean_goals(calculate_percentile(deadlift_kg, age_deadlift_data), age_deadlift_data))
                },
                'total': {
                    'val': total,
                    'global_pct': calculate_percentile(total_kg, global_total_data),
                    'age_pct': calculate_percentile(total_kg, age_total_data),
                    'goals': convert_goals(get_clean_goals(calculate_percentile(total_kg, age_total_data), age_total_data))
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
from flask import jsonify
import io, csv


# Standard Tuchscherer/RTS RPE percentage table
# Maps (reps, RPE) -> fraction of 1RM
# Source: Mike Tuchscherer's Reactive Training Systems
STANDARD_RPE_PCT = {}
_rpe_base = {
    # Reps: {RPE: %1RM}
    1:  {10: 1.000, 9.5: 0.978, 9: 0.955, 8.5: 0.939, 8: 0.922, 7.5: 0.907, 7: 0.892, 6.5: 0.878, 6: 0.863, 5.5: 0.849, 5: 0.834},
    2:  {10: 0.955, 9.5: 0.939, 9: 0.922, 8.5: 0.907, 8: 0.892, 7.5: 0.878, 7: 0.863, 6.5: 0.849, 6: 0.834, 5.5: 0.820, 5: 0.807},
    3:  {10: 0.922, 9.5: 0.907, 9: 0.892, 8.5: 0.878, 8: 0.863, 7.5: 0.849, 7: 0.834, 6.5: 0.820, 6: 0.807, 5.5: 0.793, 5: 0.780},
    4:  {10: 0.892, 9.5: 0.878, 9: 0.863, 8.5: 0.849, 8: 0.834, 7.5: 0.820, 7: 0.807, 6.5: 0.793, 6: 0.780, 5.5: 0.766, 5: 0.753},
    5:  {10: 0.863, 9.5: 0.849, 9: 0.834, 8.5: 0.820, 8: 0.807, 7.5: 0.793, 7: 0.780, 6.5: 0.766, 6: 0.753, 5.5: 0.739, 5: 0.726},
    6:  {10: 0.834, 9.5: 0.820, 9: 0.807, 8.5: 0.793, 8: 0.780, 7.5: 0.766, 7: 0.753, 6.5: 0.739, 6: 0.726, 5.5: 0.707, 5: 0.694},
    7:  {10: 0.807, 9.5: 0.793, 9: 0.780, 8.5: 0.766, 8: 0.753, 7.5: 0.739, 7: 0.726, 6.5: 0.707, 6: 0.694, 5.5: 0.681, 5: 0.668},
    8:  {10: 0.780, 9.5: 0.766, 9: 0.753, 8.5: 0.739, 8: 0.726, 7.5: 0.707, 7: 0.694, 6.5: 0.681, 6: 0.668, 5.5: 0.655, 5: 0.642},
    9:  {10: 0.753, 9.5: 0.739, 9: 0.726, 8.5: 0.707, 8: 0.694, 7.5: 0.681, 7: 0.668, 6.5: 0.655, 6: 0.642, 5.5: 0.629, 5: 0.618},
    10: {10: 0.726, 9.5: 0.707, 9: 0.694, 8.5: 0.681, 8: 0.668, 7.5: 0.655, 7: 0.642, 6.5: 0.629, 6: 0.618, 5.5: 0.605, 5: 0.590},
}
for reps, rpe_dict in _rpe_base.items():
    for rpe, pct in rpe_dict.items():
        STANDARD_RPE_PCT[(reps, rpe)] = pct

def _get_rpe_pct(reps, rpe):
    """Look up the standard %1RM for a given (reps, RPE) combo, with interpolation."""
    reps_clamped = max(1, min(10, int(round(reps))))
    rpe_clamped = max(5.0, min(10.0, rpe))
    # Snap RPE to nearest 0.5
    rpe_snapped = round(rpe_clamped * 2) / 2
    return STANDARD_RPE_PCT.get((reps_clamped, rpe_snapped), 0.75)

def generate_rpe_table(data):
    if not data or len(data) < 2: return None
    
    # Step 1: Back-calculate each set's implied e1RM using standard RPE percentages
    e1rm_estimates = []
    for d in data:
        reps = d['reps']
        rpe = d['rpe']
        weight = d['weight']
        pct = _get_rpe_pct(reps, rpe)
        if pct > 0:
            implied_e1rm = weight / pct
            # Weight heavier toward low-rep sets (more reliable for 1RM estimation)
            reliability_weight = 1.0 / max(reps, 1)
            e1rm_estimates.append((implied_e1rm, reliability_weight))
    
    if not e1rm_estimates:
        return None
    
    # Step 2: Compute weighted average e1RM
    total_weight = sum(w for _, w in e1rm_estimates)
    projected_1rm = sum(e * w for e, w in e1rm_estimates) / total_weight
    
    # Step 3: Generate RPE table using standard percentages applied to the averaged e1RM
    rpe_range = [round(10.0 - 0.5 * i, 1) for i in range(11)]  # [10.0, 9.5, ..., 5.0]
    
    rpe_table = []
    for reps in range(1, 11):
        row_data = {'reps': reps, 'rpe_values': {}, 'weights': {}, 'is_estimated': {}}
        for rpe in rpe_range:
            rpe_key = str(rpe)
            pct = _get_rpe_pct(reps, rpe)
            estimated_weight = projected_1rm * pct
            percentage = pct * 100

            row_data['rpe_values'][rpe_key] = percentage
            row_data['weights'][rpe_key] = estimated_weight
            
            # Mark cells where the user had an exact (reps, RPE) match
            # but always show the model's predicted weight to ensure monotonicity
            matching_actuals = [d['weight'] for d in data if d['reps'] == reps and d['rpe'] == rpe]
            row_data['is_estimated'][rpe_key] = len(matching_actuals) == 0
                
        rpe_table.append(row_data)

    return {
        'data_points': len(data),
        'estimated_1rm': projected_1rm,
        'rpe_table': rpe_table,
        'original_data': data,
    }


@app.route('/parse_csv', methods=['POST'])
def parse_csv():
    if 'csvFile' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    file = request.files['csvFile']
    if not file:
        return jsonify({'error': 'Empty file'})

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        lifts_data = {'squat': [], 'bench': [], 'deadlift': []}
        
        for row in reader:
            exercise = row.get('Exercise Name', row.get('Nombre del ejercicio', '')).lower()
            w_str = row.get('Weight', row.get('Peso', ''))
            r_str = row.get('Reps', row.get('Rep.', ''))
            rpe_str = row.get('RPE', '')
            
            target_lift = None
            if ('squat' in exercise or 'sentadilla' in exercise) and 'split' not in exercise and 'goblet' not in exercise and 'bulgarian' not in exercise and 'hack' not in exercise and 'smith' not in exercise and 'front' not in exercise:
                target_lift = 'squat'
            elif ('bench' in exercise or 'press de banca' in exercise) and 'dumbbell' not in exercise and 'close grip' not in exercise and 'incline' not in exercise:
                target_lift = 'bench'
            elif ('deadlift' in exercise or 'peso muerto' in exercise) and 'romanian' not in exercise and 'stiff' not in exercise and 'dumbbell' not in exercise:
                target_lift = 'deadlift'
                
            if target_lift and w_str and r_str and rpe_str:
                try:
                    w = float(w_str)
                    r = float(r_str)
                    rpe = float(rpe_str)
                    if r > 0 and rpe <= 10:
                        lifts_data[target_lift].append({
                            'weight': round(w, 2), 
                            'reps': round(r, 2), 
                            'rpe': round(rpe, 2)
                        })
                except ValueError:
                    pass
                    
        for lift in lifts_data:
            for d in lifts_data[lift]:
                d['temp_e1rm'] = d['weight'] * (1 + d['reps'] / 30.0) if d['reps'] > 1 else d['weight']
            lifts_data[lift].sort(key=lambda x: x['temp_e1rm'], reverse=True)
            for d in lifts_data[lift]:
                del d['temp_e1rm']
            lifts_data[lift] = lifts_data[lift][:10]
            
        return jsonify(lifts_data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/e1rm_tracker', methods=['GET', 'POST'])
def e1rm_tracker():
    results = None
    error = None
    
    if request.method == 'POST':
        lifts = ['squat', 'bench', 'deadlift']
        all_results = {}
        has_any_data = False
        
        try:
            for lift in lifts:
                data = []
                for i in range(1, 11):
                    w_str = request.form.get(f'{lift}_weight_{i}')
                    r_str = request.form.get(f'{lift}_reps_{i}')
                    rpe_str = request.form.get(f'{lift}_rpe_{i}')
                    
                    if w_str and r_str and rpe_str:
                        w = float(w_str)
                        r = float(r_str)
                        rpe = float(rpe_str)
                        if r > 0 and rpe <= 10:
                            data.append({'weight': w, 'reps': r, 'rpe': rpe})
                            
                if len(data) >= 2:
                    has_any_data = True
                    all_results[lift] = generate_rpe_table(data)
                elif len(data) == 1:
                    error = f"Not enough data to calculate {lift} (need at least 2 sets)."
                    
            if has_any_data:
                results = all_results
            elif not error:
                error = "No valid data provided. Fill out at least 2 sets for one lift."
                
            # DEBUG LOG
            with open('/tmp/debug_form_payload.txt', 'w') as f:
                f.write(f"Has data: {has_any_data}\n")
                f.write(f"Results keys: {results.keys() if results else None}\n")
                f.write(f"Error: {error}\n")
                f.write(str(dict(request.form)))
                
        except ValueError as e:
            print("ValueError encountered:", e)
            error = "Invalid numerical input found."
        except Exception as e:
            print("Exception encountered during regression:", e)
            import traceback
            traceback.print_exc()
            error = f"Error computing regression: {str(e)}"
            
    return render_template(
        'e1rm_tracker.html',
        title="e1RM Tracker",
        results=results,
        error=error,
        form_data=request.form if request.method == 'POST' else None
    )


