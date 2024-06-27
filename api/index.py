import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title="Conrad's Portfolio", url=os.getenv("URL"))

@app.route('/experience')
def experience():
    title = "Conrad Uyakonwu's Portfolio"
    work_experiences = [
        {
            "title": "System Administrator and Technical Support",
            "company": "Computer Science Instructional Lab (CSIL)",

            "description": "As part of my role, I conducted a mini-course on AI \
             and data science, educating patrons on various methodologies. I \
             spearheaded a CSIL-wide wiki audit, ensuring the accuracy and \
             relevance of documentation, which resulted in streamlined access \
             to critical information for all users. Additionally, I coordinated \
             with the education instruction team to organize and facilitate \
             inter-departmental courses, significantly enhancing the overall \
             technical proficiency of CSIL staff.",

            "duration": "March 2024 - Present"
        },
        {
            "title": "Software Reliability Engineer (SRE)",
            "company": "Meta x Major League Hacking Fellowship",

            "description": "Selected as one of 44 fellows from over 4,000 \
            applicants (99th percentile) to work with Meta, I completed a 12-week \
            Site Reliability Engineering (SRE) curriculum supplemented with events \
            and workshops led by Meta engineers. During this program, I developed \
            an open-source web app using Python Flask, MySQL, and unittest, achieving \
            95% test coverage. I implemented automated CI/CD pipelines using Docker, \
            cutting manual deployment time by 80% through script automation and \
            containerization, while also using Nginx to handle over 10,000 requests \
            per minute with 40% faster response times. Additionally, I initiated \
            monitoring and alerting systems with Prometheus and Grafana, creating \
            over 20 custom dashboards and reducing incident response time by 50%.",

            "duration": "June 2024 - September 2024"
        },
        {
            "title": "Curriculum Development Intern",
            "company": "Code Your Dreams",

            "description": "I collaboratively designed and delivered a comprehensive \
            15-hour course on AI development, effectively imparting knowledge to \
            students. My work included developing and showcasing a fully functional \
             WhatsApp Chatbot, which demonstrated advanced coding skills and practical \
             applications of AI. Additionally, I presented an engaging AI curriculum \
             to an audience of over 25 teachers in Burundi, facilitating communication \
             by translating content into French to ensure clarity and comprehension. \
             Leading a team of three interns, I oversaw the development, organization, \
             and management of an AI curriculum, empowering students to create their \
             own AI projects through the Code Your Dreams initiative.",

             "duration" : "June 2023 - August 2023"
        }
    ]

    education = [
        {
            "degree": "Bachelor's in Computer Science",
            "institution": "University of Chicago",
            "description": "Specialized in Machine Learning",
            "year": "Expected 2026"
        },
        {
            "degree": "IB Career Program in Computer Science",
            "institution": "Watkins Mill High School",
            "description": "Unweighted GPA: 3.93",
            "year": "2018 - 2022"
        }
    ]
    return render_template('experience.html', title=title, work_experiences=work_experiences, education=education,)

@app.route('/about')
def about():
    hobbies = [
       {
        "description" : "I have been powerlifting since 2022 and had my first competition in April \
        2024. I am currently in contention for a state record for my 300kg deadlift.",

       "img" : "/static/img/meet.jpg",
       },

       {
        "description" : "I enjoy playing video games, most notably platform or 2D fighting games, \
        I've always enjoyed learning combos and picking up tendencies to adapt.",

        "img" : "/static/img/game.jpeg",
       },
       {
        "description" : "I am also an avid music enjoyer, I listen to R&B, different variations of Pop,\
        and more recently Samba.",

        "img" : "/static/img/spotify.png",
       }
    ]
    return render_template('about.html', hobbies=hobbies)
