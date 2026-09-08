import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pypdf import PdfReader
app = Flask(__name__)
app.secret_key = "placemate_ai_secret_2026"
# ==========================================
# RESUME UPLOAD CONFIGURATION
# ==========================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )
# ==========================================
# RESUME TEXT EXTRACTION
# ==========================================

def extract_resume_text(file_path):

    text = ""

    try:
        reader = PdfReader(file_path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:
        print("Resume reading error:", e)

    return text
# ==========================================
# AUTOMATIC SKILL DETECTION FROM RESUME
# ==========================================

def extract_skills_from_resume(resume_text):

    detected_skills = []

    known_skills = [

        "python",
        "java",
        "c++",
        "c",
        "html",
        "css",
        "javascript",
        "sql",
        "mysql",
        "mongodb",
        "react",
        "node.js",
        "flask",
        "django",
        "spring",
        "git",
        "github",
        "dsa",
        "oops",
        "machine learning",
        "artificial intelligence",
        "excel",
        "power bi"
    ]

    resume_text = resume_text.lower()

    for skill in known_skills:

        if skill in resume_text:
            detected_skills.append(skill.title())

    return detected_skills
# ==========================================
# STEP 8.7 - AI RESUME QUALITY SCORE
# ==========================================

def calculate_resume_score(resume_text, skills, projects):

    score = 0

    # 1. Resume content length - Maximum 20
    if len(resume_text) >= 2000:
        score += 20
    elif len(resume_text) >= 1000:
        score += 15
    elif len(resume_text) >= 500:
        score += 10
    elif len(resume_text) > 0:
        score += 5

    # 2. Skills score - Maximum 30
    skill_list = [
        skill.strip()
        for skill in skills.split(",")
        if skill.strip()
    ]

    score += min(len(skill_list) * 5, 30)

    # 3. Projects score - Maximum 25
    project_list = [
        project.strip()
        for project in projects.splitlines()
        if project.strip()
    ]

    score += min(len(project_list) * 10, 25)

    # 4. Important resume keywords - Maximum 25
    keywords = [
        "education",
        "project",
        "skills",
        "experience",
        "github",
        "linkedin",
        "internship",
        "certification"
    ]

    resume_lower = resume_text.lower()

    keyword_count = sum(
        1
        for keyword in keywords
        if keyword in resume_lower
    )

    score += min(keyword_count * 3, 25)

    return min(score, 100)
# ==========================================
# STEP 8.8 - AI RESUME IMPROVEMENT SUGGESTIONS
# ==========================================

def get_resume_suggestions(resume_text, skills, projects):

    suggestions = []

    resume_lower = resume_text.lower()

    # Resume content length
    if len(resume_text) < 500:
        suggestions.append(
            "Your resume content is too short. Add more details about education, skills and achievements."
        )

    # Skills check
    skill_list = [
        skill.strip()
        for skill in skills.split(",")
        if skill.strip()
    ]

    if len(skill_list) < 5:
        suggestions.append(
            "Add more relevant technical skills to strengthen your resume."
        )

    # Projects check
    project_list = [
        project.strip()
        for project in projects.splitlines()
        if project.strip()
    ]

    if len(project_list) < 2:
        suggestions.append(
            "Add at least 2-3 strong projects with proper descriptions."
        )

    # Important resume sections
    keywords = {
        "education": "Add a proper Education section.",
        "experience": "Add internship or work experience if available.",
        "github": "Add your GitHub profile link.",
        "linkedin": "Add your LinkedIn profile link.",
        "certification": "Add relevant certifications."
    }

    for keyword, message in keywords.items():

        if keyword not in resume_lower:
            suggestions.append(message)

    # If resume is strong
    if not suggestions:
        suggestions.append(
            "Excellent resume! Your resume contains most important sections."
        )

    return suggestions

# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_db():

    conn = sqlite3.connect("placemate.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT,
            college TEXT NOT NULL,
            branch TEXT NOT NULL,
            year TEXT NOT NULL,
            cgpa REAL NOT NULL,
            skills TEXT,
            projects TEXT,
            resume_text TEXT
        )
    """)
        # Interview Results Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            question TEXT,
            user_answer TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# STEP 4.1 - PLACEMENT READINESS SCORE
# ==========================================

def calculate_score(student):

    cgpa = float(student["cgpa"])

    skills = student["skills"] or ""
    projects = student["projects"] or ""

    # CGPA Score - Maximum 30
    cgpa_score = (cgpa / 10) * 30

    # Skills Score - Maximum 40
    skill_list = [
        skill.strip()
        for skill in skills.split(",")
        if skill.strip()
    ]

    skills_score = min(len(skill_list) * 8, 40)

    # Projects Score - Maximum 30
    project_list = [
        project.strip()
        for project in projects.splitlines()
        if project.strip()
    ]

    projects_score = min(len(project_list) * 10, 30)

    # Total Score
    total_score = (
        cgpa_score +
        skills_score +
        projects_score
    )

    return round(total_score)


# ==========================================
# STEP 4.5 - AI IMPROVEMENT SUGGESTIONS
# ==========================================

def get_suggestions(student):

    suggestions = []

    cgpa = float(student["cgpa"])

    skills = student["skills"] or ""
    projects = student["projects"] or ""

    # Count Skills
    skill_list = [
        skill.strip()
        for skill in skills.split(",")
        if skill.strip()
    ]

    # Count Projects
    project_list = [
        project.strip()
        for project in projects.splitlines()
        if project.strip()
    ]

    # CGPA Suggestion
    if cgpa < 7:
        suggestions.append(
            "Improve your academic performance and try to maintain a CGPA above 7."
        )

    # Skills Suggestion
    if len(skill_list) < 3:
        suggestions.append(
            "Learn more technical skills such as Python, Java, SQL, HTML, CSS, or JavaScript."
        )

    # Projects Suggestion
    if len(project_list) < 2:
        suggestions.append(
            "Build at least 2-3 strong projects to improve your portfolio."
        )

    # DSA Suggestion
    if len(skill_list) < 5:
        suggestions.append(
            "Practice Data Structures and Algorithms (DSA) for technical interviews."
        )

    # Strong Profile
    if not suggestions:
        suggestions.append(
            "Great profile! Focus on mock interviews, advanced projects, and applying for internships."
        )

    return suggestions


# ==========================================
# STEP 5 - JOB ROLE RECOMMENDATION
# ==========================================

def get_job_roles(student):

    roles = []

    skills = student["skills"] or ""
    skills_lower = skills.lower()

    # Web Developer
    if (
        "html" in skills_lower or
        "css" in skills_lower or
        "javascript" in skills_lower
    ):
        roles.append("Web Developer")

    # Python Developer
    if "python" in skills_lower:
        roles.append("Python Developer")

    # Java Developer
    if "java" in skills_lower:
        roles.append("Java Developer")

    # Data Analyst
    if (
        "python" in skills_lower and
        (
            "sql" in skills_lower or
            "excel" in skills_lower
        )
    ):
        roles.append("Data Analyst")

    # Software Developer
    programming_languages = [
        "python",
        "java",
        "c++",
        "c",
        "javascript"
    ]

    language_count = sum(
        1
        for language in programming_languages
        if language in skills_lower
    )

    if language_count >= 2:
        roles.append("Software Developer")

    # Default Role
    if not roles:
        roles.append(
            "Explore programming skills to identify your suitable career path"
        )

    return roles


# ==========================================
# STEP 6 - SKILL GAP ANALYSIS
# ==========================================

def get_skill_gaps(student):

    # Get student skills
    skills = student["skills"] or ""

    # Convert skills to lowercase list
    student_skills = [
        skill.strip().lower()
        for skill in skills.split(",")
        if skill.strip()
    ]

    # Required skills for each role
    role_requirements = {

        "Web Developer": [
            "html",
            "css",
            "javascript",
            "react",
            "git"
        ],

        "Python Developer": [
            "python",
            "django",
            "flask",
            "sql",
            "git"
        ],

        "Java Developer": [
            "java",
            "spring",
            "sql",
            "git",
            "dsa"
        ],

        "Data Analyst": [
            "python",
            "sql",
            "excel",
            "power bi",
            "statistics"
        ],

        "Software Developer": [
            "dsa",
            "oops",
            "sql",
            "git",
            "problem solving"
        ]
    }

    # Get recommended roles
    job_roles = get_job_roles(student)

    # Store missing skills
    skill_gaps = {}

    # Check every role
    for role in job_roles:

        if role in role_requirements:

            required_skills = role_requirements[role]

            missing_skills = [
                skill
                for skill in required_skills
                if skill not in student_skills
            ]

            skill_gaps[role] = missing_skills

    return skill_gaps
# ==========================================
# STEP 13 - AI INTERVIEW QUESTION GENERATOR
# ==========================================

def generate_interview_questions(student):

    questions = []

    skills = student["skills"] or ""
    skills_lower = skills.lower()

    # Python Questions
    if "python" in skills_lower:
        questions.extend([
            "What is the difference between list and tuple in Python?",
            "Explain Python OOP concepts.",
            "What are Python decorators?"
        ])

    # Java Questions
    if "java" in skills_lower:
        questions.extend([
            "What is the difference between JDK, JRE and JVM?",
            "Explain OOP concepts in Java.",
            "What is the difference between ArrayList and LinkedList?"
        ])

    # HTML Questions
    if "html" in skills_lower:
        questions.extend([
            "What is the difference between HTML and HTML5?",
            "What are semantic HTML tags?"
        ])

    # CSS Questions
    if "css" in skills_lower:
        questions.extend([
            "Explain CSS Flexbox.",
            "What is the difference between Grid and Flexbox?"
        ])

    # JavaScript Questions
    if "javascript" in skills_lower:
        questions.extend([
            "What is the difference between var, let and const?",
            "Explain JavaScript closures.",
            "What is DOM?"
        ])

    # SQL Questions
    if "sql" in skills_lower:
        questions.extend([
            "What is the difference between WHERE and HAVING?",
            "Explain SQL JOINs."
        ])

    # Default Questions
    if not questions:
        questions.extend([
            "Tell me about yourself.",
            "What are your strengths?",
            "Describe one of your projects."
        ])

    return questions[:10]

# ==========================================
# STEP 10 - AI CAREER ROADMAP GENERATOR
# ==========================================

def get_career_roadmap(job_roles):

    roadmaps = {

        "Web Developer": [
            "Learn HTML fundamentals",
            "Learn CSS and Responsive Design",
            "Learn JavaScript",
            "Learn Git and GitHub",
            "Learn React",
            "Build 3 Web Development Projects",
            "Create Portfolio Website",
            "Prepare for Interviews"
        ],

        "Python Developer": [
            "Learn Python Fundamentals",
            "Master Object Oriented Programming",
            "Practice Data Structures and Algorithms",
            "Learn SQL and Databases",
            "Learn Flask or Django",
            "Build Python Projects",
            "Learn Git and GitHub",
            "Prepare for Technical Interviews"
        ],

        "Java Developer": [
            "Learn Core Java",
            "Master OOP Concepts",
            "Learn Collections Framework",
            "Practice Data Structures and Algorithms",
            "Learn SQL and JDBC",
            "Learn Spring Boot",
            "Build Java Projects",
            "Prepare for Technical Interviews"
        ],

        "Data Analyst": [
            "Learn Excel",
            "Learn SQL",
            "Learn Python",
            "Learn Pandas and NumPy",
            "Learn Statistics",
            "Learn Power BI",
            "Build Data Analysis Projects",
            "Create Portfolio"
        ],

        "Software Developer": [
            "Master Programming Fundamentals",
            "Practice Data Structures and Algorithms",
            "Learn OOP Concepts",
            "Learn Database Management",
            "Practice Problem Solving",
            "Build Strong Projects",
            "Learn System Design Basics",
            "Prepare for Interviews"
        ]
    }

    career_roadmap = {}

    for role in job_roles:

        if role in roadmaps:
            career_roadmap[role] = roadmaps[role]

    return career_roadmap
# ==========================================
# STEP 12 - AI INTERVIEW QUESTION GENERATOR
# ==========================================

def generate_interview_questions(student):

    skills = student["skills"] or ""

    skills_list = [
        skill.strip().lower()
        for skill in skills.split(",")
        if skill.strip()
    ]

    questions = []

    question_bank = {

        "python": [
            "What is the difference between a list and a tuple in Python?",
            "Explain Python decorators.",
            "What are Python dictionaries?",
            "Explain OOP concepts in Python."
        ],

        "java": [
            "What is the difference between JDK, JRE and JVM?",
            "Explain OOP concepts in Java.",
            "What is the difference between ArrayList and LinkedList?",
            "Explain exception handling in Java."
        ],

        "html": [
            "What is semantic HTML?",
            "What is the difference between div and span?",
            "What are HTML forms?"
        ],

        "css": [
            "What is the difference between Flexbox and Grid?",
            "Explain CSS positioning.",
            "What are media queries?"
        ],

        "javascript": [
            "What is the difference between var, let and const?",
            "Explain JavaScript closures.",
            "What is DOM manipulation?",
            "Explain promises and async/await."
        ],

        "sql": [
            "What is the difference between WHERE and HAVING?",
            "Explain SQL JOINs.",
            "What is normalization in databases?"
        ],

        "dsa": [
            "What is the difference between Stack and Queue?",
            "Explain Binary Search.",
            "What is time complexity?",
            "Explain Linked List."
        ]
    }

    for skill in skills_list:

        if skill in question_bank:

            for question in question_bank[skill]:

                questions.append({
                    "skill": skill.title(),
                    "question": question
                })

    # Limit questions
    return questions[:10]
# ==========================================
# STEP 24 - SMART ADAPTIVE QUESTION SYSTEM
# DUPLICATE QUESTION PREVENTION
# ==========================================

def generate_adaptive_questions(student_id, student):

    conn = sqlite3.connect("placemate.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Previous interview questions
    cursor.execute("""
        SELECT question, score
        FROM interview_results
        WHERE student_id = ?
    """, (student_id,))

    results = cursor.fetchall()

    conn.close()

    # ==========================================
    # PREVIOUSLY ASKED QUESTIONS
    # ==========================================

    asked_questions = set()

    for row in results:
        asked_questions.add(row["question"].strip().lower())

    # ==========================================
    # QUESTION BANK
    # ==========================================

    question_bank = {

        "python": [
            "What is the difference between a list and a tuple in Python?",
            "Explain Python decorators.",
            "What are Python dictionaries?",
            "Explain OOP concepts in Python."
        ],

        "java": [
            "What is the difference between JDK, JRE and JVM?",
            "Explain OOP concepts in Java.",
            "What is the difference between ArrayList and LinkedList?",
            "Explain exception handling in Java.",
            "What is method overloading and method overriding?",
            "What is inheritance in Java?"
        ],

        "html": [
            "What is semantic HTML?",
            "What is the difference between div and span?",
            "What are HTML forms?",
            "What is the difference between HTML and HTML5?"
        ],

        "css": [
            "What is the difference between Flexbox and Grid?",
            "Explain CSS positioning.",
            "What are media queries?",
            "What is CSS box model?"
        ],

        "javascript": [
            "What is the difference between var, let and const?",
            "Explain JavaScript closures.",
            "What is DOM manipulation?",
            "What is event bubbling in JavaScript?"
        ],

        "sql": [
            "What is the difference between WHERE and HAVING?",
            "Explain SQL JOINs.",
            "What is normalization?",
            "What is a primary key and foreign key?"
        ],

        "dsa": [
            "What is the difference between Stack and Queue?",
            "Explain Binary Search.",
            "What is time complexity?",
            "Explain Linked List.",
            "What is recursion?"
        ]
    }

    # ==========================================
    # FIRST INTERVIEW
    # ==========================================

    if not results:

        fresh_questions = []

        for topic, questions in question_bank.items():

            for question in questions[:2]:

                fresh_questions.append({
                    "skill": topic.title(),
                    "question": question
                })

        return fresh_questions[:10]

    # ==========================================
    # ANALYZE TOPIC PERFORMANCE
    # ==========================================

    topic_performance = analyze_topic_performance(results)

    weak_topics = []

    for topic, data in topic_performance.items():

        if data["average"] < 60:
            weak_topics.append(topic.lower())

    # ==========================================
    # ADAPTIVE QUESTION GENERATION
    # ==========================================

    adaptive_questions = []
    added_questions = set()

    # Weak topics get highest priority
    for topic in weak_topics:

        if topic in question_bank:

            for question in question_bank[topic]:

                normalized_question = question.strip().lower()

                # Skip already attempted questions
                if normalized_question in asked_questions:
                    continue

                # Skip duplicate questions
                if normalized_question in added_questions:
                    continue

                adaptive_questions.append({
                    "skill": topic.title(),
                    "question": question
                })

                added_questions.add(normalized_question)

                # Maximum 10 questions
                if len(adaptive_questions) >= 10:
                    return adaptive_questions

    # ==========================================
    # ADD QUESTIONS FROM OTHER TOPICS
    # ==========================================

    for topic, questions in question_bank.items():

        for question in questions:

            normalized_question = question.strip().lower()

            if normalized_question in asked_questions:
                continue

            if normalized_question in added_questions:
                continue

            adaptive_questions.append({
                "skill": topic.title(),
                "question": question
            })

            added_questions.add(normalized_question)

            if len(adaptive_questions) >= 10:
                return adaptive_questions

    return adaptive_questions
# ==========================================
# STEP 13 - AI INTERVIEW ANSWER GENERATOR
# ==========================================

def get_interview_answer(question):

    answers = {

        "What is the difference between a list and a tuple in Python?":
        "A list is mutable, which means its elements can be changed after creation. A tuple is immutable, meaning its elements cannot be modified after creation.",

        "Explain Python decorators.":
        "Python decorators are functions that modify or extend the behavior of another function without changing its original source code.",

        "What are Python dictionaries?":
        "A Python dictionary stores data in key-value pairs. Keys are unique and allow fast access to corresponding values.",

        "Explain OOP concepts in Python.":
        "The four main OOP concepts are Encapsulation, Inheritance, Polymorphism and Abstraction. They help organize programs using classes and objects.",

        "What is the difference between JDK, JRE and JVM?":
        "JDK is used for developing Java applications. JRE provides the environment to run Java applications. JVM executes Java bytecode.",

        "Explain OOP concepts in Java.":
        "The main OOP concepts in Java are Encapsulation, Inheritance, Polymorphism and Abstraction.",

        "What is semantic HTML?":
        "Semantic HTML uses meaningful tags such as header, nav, section, article and footer to clearly describe the structure of web content.",

        "What is the difference between Flexbox and Grid?":
        "Flexbox is mainly designed for one-dimensional layouts, either rows or columns. CSS Grid is designed for two-dimensional layouts with rows and columns.",

        "What is the difference between var, let and const?":
        "Var is function scoped, while let and const are block scoped. Let can be reassigned, but const cannot be reassigned after declaration.",

        "What is the difference between WHERE and HAVING?":
        "WHERE filters individual rows before grouping, while HAVING filters groups after the GROUP BY operation.",

        "What is the difference between Stack and Queue?":
        "A Stack follows LIFO, Last In First Out. A Queue follows FIFO, First In First Out.",

        "Explain Binary Search.":
        "Binary Search is an efficient searching algorithm that repeatedly divides a sorted array into halves until the target element is found.",

        "What is time complexity?":
        "Time complexity measures how the execution time of an algorithm grows as the input size increases. It is commonly expressed using Big O notation."
    }

    return answers.get(
        question,
        "Practice answering this question by explaining the definition, important concepts, example and a real-world use case."
    )


# ==========================================
# STEP 16 - SMART AI ANSWER EVALUATION
# ==========================================

def evaluate_interview_answer(question, user_answer):

    user_answer = (user_answer or "").strip()

    if not user_answer:
        return {
            "score": 0,
            "feedback": "Please write an answer before submitting.",
            "strength": "No answer provided.",
            "improvement": "Try explaining the concept in your own words."
        }

    answer_lower = user_answer.lower()

    # Important keywords for questions
    keyword_bank = {

        "Explain OOP concepts in Java.": [
            "encapsulation",
            "inheritance",
            "polymorphism",
            "abstraction"
        ],

        "What is the difference between Flexbox and Grid?": [
            "one-dimensional",
            "one dimensional",
            "two-dimensional",
            "two dimensional",
            "rows",
            "columns"
        ],

        "What is the difference between JDK, JRE and JVM?": [
            "jdk",
            "jre",
            "jvm",
            "development",
            "runtime",
            "bytecode"
        ],

        "What is the difference between a list and a tuple in Python?": [
            "mutable",
            "immutable",
            "list",
            "tuple"
        ],

        "What is the difference between Stack and Queue?": [
            "lifo",
            "fifo",
            "stack",
            "queue"
        ],

        "What is Binary Search?": [
            "sorted",
            "divide",
            "half",
            "search"
        ],

        "What is time complexity?": [
            "big o",
            "execution",
            "input size",
            "algorithm"
        ]
    }

    keywords = keyword_bank.get(question, [])

    # Count matched keywords
    matched_keywords = []

    for keyword in keywords:
        if keyword in answer_lower:
            matched_keywords.append(keyword)

    # Keyword score
    if keywords:
        keyword_percentage = (
            len(matched_keywords) / len(keywords)
        ) * 70
    else:
        keyword_percentage = 30

    # Length score
    word_count = len(user_answer.split())

    if word_count >= 50:
        length_score = 30
    elif word_count >= 30:
        length_score = 25
    elif word_count >= 15:
        length_score = 20
    elif word_count >= 8:
        length_score = 15
    else:
        length_score = 5

    # Final Score
    score = round(keyword_percentage + length_score)

    # Maximum 100
    score = min(score, 100)

    # Generate feedback
    if score >= 85:
        feedback = "Excellent! Your answer covers most important concepts."
        strength = "Strong technical understanding and relevant keywords."
        improvement = "Add a practical example to make your answer even better."

    elif score >= 65:
        feedback = "Good answer! You understand the main concept."
        strength = "You included several important technical concepts."
        improvement = "Add more explanation and cover missing concepts."

    elif score >= 40:
        feedback = "Average answer. Some important concepts are missing."
        strength = "You attempted the question and mentioned relevant ideas."
        improvement = "Explain the topic in more detail and include important keywords."

    else:
        feedback = "Your answer needs improvement."
        strength = "You attempted the question."
        improvement = "Review the concept and include the important technical points."

    # Add missing keyword information
    missing_keywords = [
        keyword
        for keyword in keywords
        if keyword not in matched_keywords
    ]

    if missing_keywords:
        improvement += (
            " Missing concepts: "
            + ", ".join(missing_keywords[:5])
        )

    return {
        "score": score,
        "feedback": feedback,
        "strength": strength,
        "improvement": improvement
    }
# ==========================================
# STEP 17 - TOPIC WISE PERFORMANCE ANALYSIS
# ==========================================

def analyze_topic_performance(results):

    topics = {
        "Java": [],
        "Python": [],
        "HTML": [],
        "CSS": [],
        "JavaScript": [],
        "SQL": [],
        "DSA": []
    }

    for result in results:

        question = result["question"].lower()
        score = result["score"]

        if any(word in question for word in [
            "java", "jdk", "jre", "jvm",
            "arraylist", "linkedlist"
        ]):
            topics["Java"].append(score)

        elif any(word in question for word in [
            "python", "list", "tuple",
            "dictionary", "decorator"
        ]):
            topics["Python"].append(score)

        elif any(word in question for word in [
            "html", "semantic", "div", "span"
        ]):
            topics["HTML"].append(score)

        elif any(word in question for word in [
            "css", "flexbox", "grid"
        ]):
            topics["CSS"].append(score)

        elif any(word in question for word in [
            "javascript", "dom",
            "closure", "promise"
        ]):
            topics["JavaScript"].append(score)

        elif any(word in question for word in [
            "sql", "join", "where",
            "having", "normalization"
        ]):
            topics["SQL"].append(score)

        elif any(word in question for word in [
            "stack", "queue",
            "binary search",
            "time complexity",
            "linked list"
        ]):
            topics["DSA"].append(score)

    topic_analysis = {}

    for topic, scores in topics.items():

        if scores:

            average = round(sum(scores) / len(scores))

            topic_analysis[topic] = {
                "average": average,
                "attempts": len(scores)
            }

    return topic_analysis
# ==========================================
# STEP 11 - AI 30 DAY PLACEMENT PLAN
# ==========================================

def get_30_day_plan(job_roles):

    plan = []

    # Common plan for all students
    common_plan = [
        "Day 1: Analyze your current skills and placement readiness",
        "Day 2: Improve programming fundamentals",
        "Day 3: Practice basic problem solving",
        "Day 4: Learn Object Oriented Programming concepts",
        "Day 5: Practice Arrays and Strings",
        "Day 6: Learn Linked Lists",
        "Day 7: Practice Stack and Queue",
        "Day 8: Learn Trees and Binary Search Trees",
        "Day 9: Practice Sorting Algorithms",
        "Day 10: Practice Searching Algorithms",
        "Day 11: Learn Recursion and Backtracking",
        "Day 12: Practice Dynamic Programming basics",
        "Day 13: Solve coding problems",
        "Day 14: Revise DSA concepts",
        "Day 15: Build or improve a technical project",
        "Day 16: Improve your GitHub profile",
        "Day 17: Update your Resume",
        "Day 18: Create or improve LinkedIn profile",
        "Day 19: Learn DBMS basics",
        "Day 20: Practice SQL queries",
        "Day 21: Learn Operating System basics",
        "Day 22: Learn Computer Networks basics",
        "Day 23: Practice HR interview questions",
        "Day 24: Practice Technical interview questions",
        "Day 25: Give a mock interview",
        "Day 26: Improve weak technical areas",
        "Day 27: Solve medium level coding problems",
        "Day 28: Final Resume Review",
        "Day 29: Apply for internships and jobs",
        "Day 30: Complete placement readiness assessment"
    ]

    # Role-specific focus
    if "Web Developer" in job_roles:
        focus = "Focus Area: HTML, CSS, JavaScript, React and Web Projects"

    elif "Python Developer" in job_roles:
        focus = "Focus Area: Python, Flask/Django and Backend Projects"

    elif "Java Developer" in job_roles:
        focus = "Focus Area: Core Java, OOP, Spring Boot and DSA"

    elif "Data Analyst" in job_roles:
        focus = "Focus Area: Python, SQL, Excel, Power BI and Statistics"

    else:
        focus = "Focus Area: Programming, DSA, Projects and Interview Preparation"

    return focus, common_plan
# ==========================================
# STEP 25 - SMART AI RECOMMENDATION ENGINE
# ==========================================

def get_smart_recommendations(
    placement_score,
    resume_score,
    average_interview_score,
    skill_gaps,
    improvement_plan
):

    recommendations = []

    # ======================================
    # PLACEMENT READINESS
    # ======================================

    if placement_score < 50:

        recommendations.append({
            "priority": "High",
            "title": "Improve Placement Readiness",
            "message":
            "Your placement readiness score is low. Focus on technical skills and projects."
        })

    elif placement_score < 75:

        recommendations.append({
            "priority": "Medium",
            "title": "Improve Placement Profile",
            "message":
            "Your profile is developing. Add stronger projects and improve technical skills."
        })

    else:

        recommendations.append({
            "priority": "Low",
            "title": "Maintain Strong Profile",
            "message":
            "Your placement profile is strong. Focus on advanced projects and interviews."
        })


    # ======================================
    # RESUME ANALYSIS
    # ======================================

    if resume_score < 60:

        recommendations.append({
            "priority": "High",
            "title": "Improve Your Resume",
            "message":
            "Add better project descriptions, technical skills, GitHub, LinkedIn and certifications."
        })

    elif resume_score < 80:

        recommendations.append({
            "priority": "Medium",
            "title": "Strengthen Resume",
            "message":
            "Your resume is good but can be improved with achievements and stronger project descriptions."
        })


    # ======================================
    # INTERVIEW PERFORMANCE
    # ======================================

    if average_interview_score < 40:

        recommendations.append({
            "priority": "High",
            "title": "Practice Interview Fundamentals",
            "message":
            "Your interview performance needs improvement. Practice fundamental concepts daily."
        })

    elif average_interview_score < 70:

        recommendations.append({
            "priority": "Medium",
            "title": "Improve Interview Performance",
            "message":
            "Practice explaining technical concepts with examples."
        })

    else:

        recommendations.append({
            "priority": "Low",
            "title": "Practice Advanced Interviews",
            "message":
            "Try scenario-based and advanced technical interview questions."
        })


    # ======================================
    # SKILL GAP ANALYSIS
    # ======================================

    missing_skills = []

    for role, gaps in skill_gaps.items():

        for skill in gaps:

            if skill not in missing_skills:
                missing_skills.append(skill)

    if missing_skills:

        recommendations.append({
            "priority": "High",
            "title": "Close Important Skill Gaps",
            "message":
            "Focus on learning: " + ", ".join(missing_skills[:5])
        })


    # ======================================
    # WEAKEST TOPIC
    # ======================================

    if improvement_plan:

        weak_topic = improvement_plan[0]

        if weak_topic.get("priority") == "High Priority":

            recommendations.append({
                "priority": "High",
                "title": "Focus on Weakest Topic",
                "message":
                f"Your weakest area is {weak_topic.get('topic')}. Practice this topic daily."
            })


    # ======================================
    # SORT PRIORITY
    # ======================================

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    recommendations.sort(
        key=lambda item: priority_order[item["priority"]]
    )

    return recommendations
        # ==========================================
# STEP 21 - AI PLACEMENT PREDICTION ENGINE
# ==========================================

def predict_placement_probability(
    student,
    resume_score,
    average_interview_score,
    skill_gaps
):

    probability = 0

    strengths = []
    risk_areas = []


    # ======================================
    # 1. CGPA ANALYSIS - MAX 20 POINTS
    # ======================================

    cgpa = float(student["cgpa"])

    if cgpa >= 9:

        probability += 20

        strengths.append(
            "Excellent academic performance"
        )

    elif cgpa >= 8:

        probability += 17

        strengths.append(
            "Strong academic performance"
        )

    elif cgpa >= 7:

        probability += 14

        strengths.append(
            "Good academic performance"
        )

    elif cgpa >= 6:

        probability += 10

        risk_areas.append(
            "CGPA can be improved"
        )

    else:

        probability += 5

        risk_areas.append(
            "Low academic score may affect eligibility"
        )


    # ======================================
    # 2. TECHNICAL SKILLS - MAX 20 POINTS
    # ======================================

    skills = student["skills"] or ""

    skill_list = [
        skill.strip()
        for skill in skills.split(",")
        if skill.strip()
    ]

    skill_count = len(skill_list)

    if skill_count >= 8:

        probability += 20

        strengths.append(
            "Strong technical skill portfolio"
        )

    elif skill_count >= 5:

        probability += 15

        strengths.append(
            "Good technical skills"
        )

    elif skill_count >= 3:

        probability += 10

        risk_areas.append(
            "Need more technical skills"
        )

    else:

        probability += 5

        risk_areas.append(
            "Limited technical skill set"
        )


    # ======================================
    # 3. PROJECTS - MAX 15 POINTS
    # ======================================

    projects = student["projects"] or ""

    project_list = [
        project.strip()
        for project in projects.splitlines()
        if project.strip()
    ]

    project_count = len(project_list)

    if project_count >= 3:

        probability += 15

        strengths.append(
            "Strong project portfolio"
        )

    elif project_count >= 2:

        probability += 10

        strengths.append(
            "Good practical project experience"
        )

    elif project_count >= 1:

        probability += 5

        risk_areas.append(
            "Build more practical projects"
        )

    else:

        risk_areas.append(
            "No projects found in profile"
        )


    # ======================================
    # 4. RESUME QUALITY - MAX 15 POINTS
    # ======================================

    if resume_score >= 80:

        probability += 15

        strengths.append(
            "Strong and well-structured resume"
        )

    elif resume_score >= 60:

        probability += 10

        strengths.append(
            "Good resume quality"
        )

    elif resume_score >= 40:

        probability += 6

        risk_areas.append(
            "Resume needs improvement"
        )

    else:

        probability += 2

        risk_areas.append(
            "Weak resume may affect shortlisting"
        )


    # ======================================
    # 5. INTERVIEW PERFORMANCE - MAX 20
    # ======================================

    if average_interview_score >= 80:

        probability += 20

        strengths.append(
            "Excellent interview performance"
        )

    elif average_interview_score >= 60:

        probability += 15

        strengths.append(
            "Good interview performance"
        )

    elif average_interview_score >= 40:

        probability += 10

        risk_areas.append(
            "Interview performance needs improvement"
        )

    else:

        probability += 5

        risk_areas.append(
            "Practice more mock interviews"
        )


    # ======================================
    # 6. SKILL GAPS - MAX 10
    # ======================================

    missing_skills = []

    for role, gaps in skill_gaps.items():

        for skill in gaps:

            if skill not in missing_skills:

                missing_skills.append(skill)

    gap_count = len(missing_skills)

    if gap_count == 0:

        probability += 10

        strengths.append(
            "No major technical skill gaps"
        )

    elif gap_count <= 2:

        probability += 7

        risk_areas.append(
            "Minor skill gaps detected"
        )

    elif gap_count <= 5:

        probability += 4

        risk_areas.append(
            "Several technical skill gaps detected"
        )

    else:

        probability += 1

        risk_areas.append(
            "Important technical skill gaps need attention"
        )


    # ======================================
    # FINAL PREDICTION
    # ======================================

    probability = min(probability, 100)

    if probability >= 80:

        prediction = "High Chance of Getting Placed"

        level = "Excellent"

    elif probability >= 65:

        prediction = "Good Chance of Getting Placed"

        level = "Good"

    elif probability >= 45:

        prediction = "Moderate Chance - Improvement Needed"

        level = "Average"

    else:

        prediction = "Low Chance - Strong Preparation Needed"

        level = "Needs Improvement"


    return {
        "probability": probability,
        "prediction": prediction,
        "level": level,
        "strengths": strengths,
        "risk_areas": risk_areas
    }


    # ======================================
    # SORT PRIORITIES
    # ======================================

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    recommendations.sort(
        key=lambda item:
        priority_order[item["priority"]]
    )

    return recommendations

# ==========================================
# HOMEPAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")
# ==========================================
# LOGIN PAGE
# ==========================================



# ==========================================
# STUDENT REGISTRATION + RESUME UPLOAD
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)
        college = request.form.get("college")
        branch = request.form.get("branch")
        year = request.form.get("year")
        cgpa = request.form.get("cgpa")
        skills = request.form.get("skills")
        projects = request.form.get("projects")
        resume_text = ""

        # ==========================================
        # GET RESUME FILE
        # ==========================================

        resume = request.files.get("resume")

        resume_filename = None

        # Check if resume is uploaded
        if resume and resume.filename != "":

            # Check PDF extension
            if allowed_file(resume.filename):

                # Make filename safe
                filename = secure_filename(resume.filename)

                # Create unique filename
                resume_filename = (
                    email.replace("@", "_")
                    .replace(".", "_")
                    + "_"
                    + filename
                )

                # Create uploads folder if not exists
                os.makedirs(
                    app.config["UPLOAD_FOLDER"],
                    exist_ok=True
                )

                # Full file path
                resume_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    resume_filename
                )

                                # Save resume
                resume.save(resume_path)

                print("✅ Resume saved successfully!")
                print("📁 Resume Path:", resume_path)

                                # Extract text from uploaded resume
                resume_text = extract_resume_text(resume_path)

                print("========== RESUME TEXT ==========")
                print(resume_text[:1000])
                print("=================================")

                # Detect skills from resume
                resume_skills = extract_skills_from_resume(resume_text)
                               # Combine manual skills and resume detected skills
                manual_skills = [
                    skill.strip()
                    for skill in skills.split(",")
                    if skill.strip()
                ]

                all_skills = list(
                    set(manual_skills + resume_skills)
                )

                skills = ", ".join(all_skills)

                print("========== FINAL SKILLS ==========")
                print(skills)
                print("=================================")

            else:
                return "❌ Only PDF files are allowed!"

        else:
            print("⚠️ No resume uploaded")
        # ==========================================
        # DATABASE CONNECTION
        # ==========================================

        conn = sqlite3.connect("placemate.db")
        cursor = conn.cursor()

        # Insert student data
        cursor.execute("""
            INSERT INTO students
            (
                name,
                email,
                password,
                college,
                branch,
                year,
                cgpa,
                skills,
                projects,
                resume_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?)
        """, (
            name,
            email,
            hashed_password,
            college,
            branch,
            year,
            cgpa,
            skills,
            projects,
            resume_text
        ))

        # Get student ID
        student_id = cursor.lastrowid

        # Save database
        conn.commit()
        conn.close()

        # Redirect to profile
        return redirect(
            url_for(
                "profile",
                student_id=student_id
            )
        )

    return render_template("register.html")

# ==========================================
# LOGIN SYSTEM
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("placemate.db")
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email = ?",
            (email,)
        )

        student = cursor.fetchone()

        conn.close()

        # Check student exists
        if student is None:

            flash("Email not found. Please register first.")

            return redirect(
                url_for("login")
            )

        # Check password
        if not check_password_hash(
            student["password"],
            password
        ):

            flash("Incorrect password.")

            return redirect(
                url_for("login")
            )

        # Create login session
        session["student_id"] = student["id"]
        session["student_name"] = student["name"]

        flash("Login successful!")

        return redirect(
            url_for(
                "profile",
                student_id=student["id"]
            )
        )

    return render_template("login.html")
# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect(
        url_for("home")
    )
# ==========================================
# STEP 21 - PLACEMENT PREDICTION SYSTEM
# ==========================================

def predict_placement(student, placement_score, resume_score):

    cgpa = float(student["cgpa"])

    skills = student["skills"] or ""
    projects = student["projects"] or ""

    skill_count = len([
        skill.strip()
        for skill in skills.split(",")
        if skill.strip()
    ])

    project_count = len([
        project.strip()
        for project in projects.splitlines()
        if project.strip()
    ])

    probability = 0

    # CGPA contribution
    probability += (cgpa / 10) * 25

    # Skills contribution
    probability += min(skill_count * 5, 25)

    # Projects contribution
    probability += min(project_count * 10, 20)

    # Placement readiness contribution
    probability += placement_score * 0.15

    # Resume contribution
    probability += resume_score * 0.15

    probability = round(min(probability, 100))

    if probability >= 75:
        prediction = "High Chance"
        message = "You have a strong placement profile."

    elif probability >= 50:
        prediction = "Moderate Chance"
        message = "Improve your skills and projects for better placement chances."

    else:
        prediction = "Low Chance"
        message = "Focus on technical skills, projects and interview preparation."

    return {
        "probability": probability,
        "prediction": prediction,
        "message": message
    }
# ==========================================
# STEP 27 - OVERALL PLACEMENT PROGRESS
# ==========================================

def calculate_overall_progress(
    placement_score,
    resume_score,
    interview_score,
    skill_gaps
):

    # ======================================
    # SKILL GAP SCORE
    # ======================================

    missing_skills = []

    for role, gaps in skill_gaps.items():

        for skill in gaps:

            if skill not in missing_skills:

                missing_skills.append(skill)


    # Count missing skills
    gap_count = len(missing_skills)


    # ======================================
    # CALCULATE SKILL SCORE
    # ======================================

    if gap_count == 0:

        skill_score = 100

    elif gap_count <= 2:

        skill_score = 80

    elif gap_count <= 4:

        skill_score = 60

    elif gap_count <= 6:

        skill_score = 40

    else:

        skill_score = 20


    # ======================================
    # OVERALL WEIGHTED PROGRESS SCORE
    # ======================================

    overall_progress = (

        placement_score * 0.30 +

        resume_score * 0.25 +

        interview_score * 0.30 +

        skill_score * 0.15

    )


    # Round score
    overall_progress = round(overall_progress)


    # ======================================
    # DETERMINE PROGRESS LEVEL
    # ======================================

    if overall_progress >= 80:

        level = "Excellent"

    elif overall_progress >= 65:

        level = "Good"

    elif overall_progress >= 45:

        level = "Developing"

    else:

        level = "Needs Improvement"


    # ======================================
    # RETURN ANALYSIS DATA
    # ======================================

    return {

        "progress": overall_progress,

        "level": level,

        "skill_score": skill_score,

        "missing_skills": missing_skills,

        "gap_count": gap_count

    }

# ==========================================
# STUDENT PROFILE + AI ANALYSIS
# ==========================================

@app.route("/profile/<int:student_id>")
def profile(student_id):

    conn = sqlite3.connect("placemate.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()
    conn.close()

    if student is None:
        return "Student not found", 404


    # ==========================================
    # PLACEMENT SCORE
    # ==========================================

    score = calculate_score(student)


    # ==========================================
    # RESUME SCORE
    # ==========================================

    resume_score = calculate_resume_score(
        student["resume_text"] or "",
        student["skills"] or "",
        student["projects"] or ""
    )


    # ==========================================
    # GET INTERVIEW PERFORMANCE
    # ==========================================

    conn = sqlite3.connect("placemate.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT score
        FROM interview_results
        WHERE student_id = ?
    """, (student_id,))

    interview_results = cursor.fetchall()

    conn.close()


    if interview_results:

        interview_scores = [
            row["score"]
            for row in interview_results
        ]

        average_interview_score = round(
            sum(interview_scores)
            / len(interview_scores)
        )

    else:

        average_interview_score = 0


    # ==========================================
    # SKILL GAP ANALYSIS
    # IMPORTANT: BEFORE PREDICTION
    # ==========================================

    skill_gaps = get_skill_gaps(student)


    # ==========================================
    # PLACEMENT PREDICTION
    # ==========================================

    placement_prediction = predict_placement_probability(
        student,
        resume_score,
        average_interview_score,
        skill_gaps
    )


    # ==========================================
    # AI SUGGESTIONS
    # ==========================================

    suggestions = get_suggestions(student)


    # ==========================================
    # RESUME SUGGESTIONS
    # ==========================================

    resume_suggestions = get_resume_suggestions(
        student["resume_text"] or "",
        student["skills"] or "",
        student["projects"] or ""
    )


    # ==========================================
    # JOB ROLES
    # ==========================================

    job_roles = get_job_roles(student)


    # ==========================================
    # CAREER ROADMAP
    # ==========================================

    career_roadmap = get_career_roadmap(
        job_roles
    )


    # ==========================================
    # 30 DAY PLAN
    # ==========================================

    plan_focus, placement_plan = get_30_day_plan(
        job_roles
    )


    # ==========================================
    # INTERVIEW QUESTIONS
    # ==========================================

    interview_questions = generate_interview_questions(
        student
    )


    # ==========================================
    # READINESS STATUS
    # ==========================================

    if score <= 40:

        readiness = "Needs Improvement"

    elif score <= 70:

        readiness = "Developing"

    else:

        readiness = "Placement Ready"


    # ==========================================
    # RENDER PROFILE
    # ==========================================

    return render_template(

        "profile.html",

        student=student,

        score=score,

        resume_score=resume_score,

        placement_prediction=placement_prediction,

        average_interview_score=average_interview_score,

        readiness=readiness,

        suggestions=suggestions,

        resume_suggestions=resume_suggestions,

        job_roles=job_roles,

        skill_gaps=skill_gaps,

        career_roadmap=career_roadmap,

        plan_focus=plan_focus,

        placement_plan=placement_plan,

        interview_questions=interview_questions
    )
# ==========================================
# STEP 13.4 - INTERVIEW ANSWER PAGE
# ==========================================

@app.route("/interview-answer")
def interview_answer():

    question = request.args.get("question")

    if not question:
        return "Question not found"

    answer = get_interview_answer(question)

    return render_template(
        "interview_answer.html",
        question=question,
        answer=answer
    )
# ==========================================
# STEP 14.1 - AI MOCK INTERVIEW PAGE
# ==========================================

# ==========================================
# STEP 14.1 - AI ADAPTIVE MOCK INTERVIEW
# ==========================================

@app.route("/mock-interview/<int:student_id>")
def mock_interview(student_id):

    conn = sqlite3.connect("placemate.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    # AI Adaptive Questions
    # Previous interview performance ke according
    # weak topics ko priority milegi
    interview_questions = generate_adaptive_questions(
        student_id,
        student
    )

    return render_template(
        "mock_interview.html",
        student=student,
        interview_questions=interview_questions
    )
# ==========================================
# STEP 14.5 - SUBMIT INTERVIEW ANSWER
# ==========================================

@app.route("/submit-answer/<int:student_id>", methods=["POST"])
def submit_answer(student_id):

    question = request.form.get("question", "")
    user_answer = request.form.get("student_answer", "")

    print("QUESTION:", question)
    print("USER ANSWER:", user_answer)
    print("FORM DATA:", request.form)

    result = evaluate_interview_answer(
        question,
        user_answer
    )

    expected_answer = get_interview_answer(question)

    conn = sqlite3.connect("placemate.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interview_results
        (
            student_id,
            question,
            user_answer,
            score
        )
        VALUES (?, ?, ?, ?)
    """, (
        student_id,
        question,
        user_answer,
        result["score"]
    ))

    conn.commit()
    conn.close()

    return render_template(
        "answer_feedback.html",
        student_id=student_id,
        question=question,
        user_answer=user_answer,
        result=result,
        expected_answer=expected_answer
    )
# ==========================================
# STEP 16.3 - AI WEAK TOPIC ANALYSIS
# ==========================================

def analyze_weak_topics(results):

    topic_scores = {}

    # Keywords to identify topics
    topic_keywords = {

        "Java": [
            "java",
            "jdk",
            "jre",
            "jvm",
            "arraylist",
            "linkedlist"
        ],

        "Python": [
            "python",
            "tuple",
            "list",
            "dictionary",
            "decorator"
        ],

        "HTML": [
            "html",
            "semantic",
            "div",
            "span"
        ],

        "CSS": [
            "css",
            "flexbox",
            "grid",
            "media"
        ],

        "JavaScript": [
            "javascript",
            "dom",
            "closure",
            "promise",
            "async"
        ],

        "SQL": [
            "sql",
            "where",
            "having",
            "join",
            "normalization"
        ],

        "DSA": [
            "stack",
            "queue",
            "binary search",
            "time complexity",
            "linked list"
        ]
    }

    # Analyze every interview result
    for result in results:

        question = result["question"].lower()
        score = result["score"]

        detected_topic = "General"

        for topic, keywords in topic_keywords.items():

            if any(keyword in question for keyword in keywords):

                detected_topic = topic
                break

        # Store scores topic-wise
        if detected_topic not in topic_scores:
            topic_scores[detected_topic] = []

        topic_scores[detected_topic].append(score)

    # Calculate topic averages
    topic_analysis = []

    for topic, scores in topic_scores.items():

        average = round(sum(scores) / len(scores))

        if average < 40:
            level = "Weak"
            recommendation = (
                f"Focus more on {topic} fundamentals "
                "and practice basic interview questions."
            )

        elif average < 70:
            level = "Needs Improvement"
            recommendation = (
                f"Practice more {topic} interview questions "
                "and improve conceptual understanding."
            )

        else:
            level = "Strong"
            recommendation = (
                f"Good performance in {topic}. "
                "Continue practicing advanced concepts."
            )

        topic_analysis.append({
            "topic": topic,
            "average": average,
            "level": level,
            "recommendation": recommendation
        })

    # Sort weak topics first
    topic_analysis.sort(
        key=lambda item: item["average"]
    )

    return topic_analysis
# ==========================================
# STEP 20.2 - PERSONALIZED IMPROVEMENT PLAN
# ==========================================

def generate_improvement_plan(topic_performance):

    improvement_plan = []

    # If no performance data
    if not topic_performance:
        return improvement_plan

    # ==========================================
    # CASE 1: topic_performance is DICTIONARY
    # Example:
    # {
    #   "Python": {"average": 50, "attempts": 2}
    # }
    # ==========================================

    if isinstance(topic_performance, dict):

        sorted_topics = sorted(
            topic_performance.items(),
            key=lambda item: item[1]["average"]
        )

        for topic, data in sorted_topics:

            average = data.get("average", 0)
            attempts = data.get("attempts", 0)

            if average < 40:

                priority = "High Priority"

                recommendation = (
                    f"Focus strongly on {topic} fundamentals. "
                    f"Revise core concepts and practice at least "
                    f"10 interview questions daily."
                )

            elif average < 70:

                priority = "Medium Priority"

                recommendation = (
                    f"Improve your {topic} concepts and practice "
                    f"more interview questions with examples."
                )

            else:

                priority = "Low Priority"

                recommendation = (
                    f"You are performing well in {topic}. "
                    f"Continue practicing advanced questions."
                )

            improvement_plan.append({
                "topic": topic,
                "score": average,
                "attempts": attempts,
                "priority": priority,
                "recommendation": recommendation
            })

    # ==========================================
    # CASE 2: topic_performance is LIST
    # Example:
    # [
    #   {
    #     "topic": "Python",
    #     "average": 50,
    #     "level": "Needs Improvement"
    #   }
    # ]
    # ==========================================

    elif isinstance(topic_performance, list):

        sorted_topics = sorted(
            topic_performance,
            key=lambda item: item.get("average", 0)
        )

        for data in sorted_topics:

            topic = data.get("topic", "General")
            average = data.get("average", 0)
            attempts = data.get("attempts", 0)

            if average < 40:

                priority = "High Priority"

                recommendation = (
                    f"Focus strongly on {topic} fundamentals. "
                    f"Revise concepts and solve basic questions daily."
                )

            elif average < 70:

                priority = "Medium Priority"

                recommendation = (
                    f"Improve your {topic} concepts and practice "
                    f"more interview questions."
                )

            else:

                priority = "Low Priority"

                recommendation = (
                    f"Good performance in {topic}. "
                    f"Practice advanced questions to become stronger."
                )

            improvement_plan.append({
                "topic": topic,
                "score": average,
                "attempts": attempts,
                "priority": priority,
                "recommendation": recommendation
            })

    return improvement_plan
# ==========================================
# STEP 16.1 - INTERVIEW PERFORMANCE DASHBOARD
# ==========================================
@app.route("/interview-performance/<int:student_id>")
def interview_performance(student_id):

    conn = sqlite3.connect("placemate.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # ==========================================
    # GET INTERVIEW RESULTS
    # ==========================================

    cursor.execute("""
        SELECT *
        FROM interview_results
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (student_id,))

    results = cursor.fetchall()


    # ==========================================
    # STEP 20.2 - GET STUDENT DATA
    # ==========================================

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if student is None:

        conn.close()

        return "Student not found", 404


    # ==========================================
    # CALCULATE PLACEMENT SCORE
    # ==========================================

    placement_score = calculate_score(student)


    # ==========================================
    # CALCULATE RESUME SCORE
    # ==========================================

    resume_score = calculate_resume_score(
        student["resume_text"] or "",
        student["skills"] or "",
        student["projects"] or ""
    )


    # ==========================================
    # GET SKILL GAPS
    # ==========================================

    skill_gaps = get_skill_gaps(student)


    # ==========================================
    # INTERVIEW STATISTICS
    # ==========================================

    total_attempted = len(results)

    if total_attempted > 0:

        scores = [
            result["score"]
            for result in results
        ]

        average_score = round(
            sum(scores) / total_attempted
        )

        highest_score = max(scores)

        lowest_score = min(scores)

        strong_answers = [
            result
            for result in results
            if result["score"] >= 75
        ]

        weak_answers = [
            result
            for result in results
            if result["score"] < 60
        ]

    else:

        average_score = 0
        highest_score = 0
        lowest_score = 0

        strong_answers = []
        weak_answers = []


    # ==========================================
    # AI TOPIC ANALYSIS
    # ==========================================

    topic_analysis = analyze_weak_topics(results)


    # ==========================================
    # PERSONALIZED IMPROVEMENT PLAN
    # ==========================================

    improvement_plan = generate_improvement_plan(
        topic_analysis
    )


    # ==========================================
    # TOPIC-WISE PERFORMANCE
    # ==========================================

    topic_performance = analyze_topic_performance(results)

    weakest_topic = None
    strongest_topic = None

    if topic_performance:

        weakest_topic = min(
            topic_performance,
            key=lambda topic:
            topic_performance[topic]["average"]
        )

        strongest_topic = max(
            topic_performance,
            key=lambda topic:
            topic_performance[topic]["average"]
        )


    # ==========================================
    # STEP 20.2 - SMART AI RECOMMENDATIONS
    # ==========================================

    smart_recommendations = get_smart_recommendations(
        placement_score,
        resume_score,
        average_score,
        skill_gaps,
        improvement_plan
    )


    # ==========================================
    # PERFORMANCE LEVEL
    # ==========================================

    if average_score >= 80:

        performance = "Excellent"

    elif average_score >= 60:

        performance = "Good"

    elif average_score >= 40:

        performance = "Average"

    else:

        performance = "Needs Improvement"


    # ==========================================
    # PREPARE CHART DATA
    # ==========================================

    chart_labels = []
    chart_scores = []

    for index, result in enumerate(
        reversed(results),
        start=1
    ):

        chart_labels.append(
            f"Question {index}"
        )

        chart_scores.append(
            result["score"]
        )


    # Close database
    conn.close()


    # ==========================================
    # SEND DATA TO HTML
    # ==========================================

    return render_template(
        "interview_performance.html",

        student_id=student_id,

        results=results,

        total_attempted=total_attempted,

        average_score=average_score,

        highest_score=highest_score,

        lowest_score=lowest_score,

        performance=performance,

        strong_answers=strong_answers,

        weak_answers=weak_answers,

        chart_labels=chart_labels,

        chart_scores=chart_scores,

        topic_analysis=topic_analysis,

        topic_performance=topic_performance,

        weakest_topic=weakest_topic,

        strongest_topic=strongest_topic,

        improvement_plan=improvement_plan,

        # STEP 20.2 DATA
        placement_score=placement_score,

        resume_score=resume_score,

        smart_recommendations=smart_recommendations
    )


# ==========================================
# START APPLICATION
# ==========================================

init_db()


if __name__ == "__main__":
    app.run(debug=True)