import re
import json

# ─── Skill Databases ────────────────────────────────────────────────────────

TECH_SKILLS = [
    "python","java","javascript","typescript","c++","c#","go","rust","kotlin","swift",
    "react","angular","vue","nextjs","nodejs","django","flask","fastapi","spring boot",
    "html","css","tailwind","bootstrap","sass",
    "sql","mysql","postgresql","mongodb","redis","firebase","sqlite","oracle",
    "aws","azure","gcp","docker","kubernetes","terraform","jenkins","github actions","ci/cd",
    "machine learning","deep learning","nlp","computer vision","tensorflow","pytorch","scikit-learn",
    "pandas","numpy","matplotlib","seaborn","opencv",
    "git","linux","bash","rest api","graphql","microservices","agile","scrum"
]

SOFT_SKILLS = [
    "leadership","communication","teamwork","problem solving","critical thinking",
    "time management","adaptability","creativity","collaboration","project management",
    "analytical","detail-oriented","self-motivated","organized","multitasking"
]

JOB_ROLE_SKILLS = {
    "software engineer": ["python","java","javascript","git","data structures","algorithms","oop","rest api","sql","docker"],
    "data scientist": ["python","machine learning","deep learning","pandas","numpy","scikit-learn","sql","tensorflow","pytorch","statistics"],
    "web developer": ["html","css","javascript","react","nodejs","bootstrap","tailwind","git","rest api","mongodb"],
    "devops engineer": ["docker","kubernetes","aws","ci/cd","linux","bash","terraform","jenkins","git","monitoring"],
    "ai/ml engineer": ["python","machine learning","deep learning","nlp","tensorflow","pytorch","opencv","pandas","numpy","transformers"],
    "data analyst": ["sql","python","excel","pandas","tableau","power bi","statistics","matplotlib","seaborn","data visualization"],
    "backend developer": ["python","java","nodejs","sql","rest api","docker","postgresql","redis","microservices","git"],
    "frontend developer": ["html","css","javascript","react","vue","angular","tailwind","typescript","git","figma"],
    "full stack developer": ["html","css","javascript","react","nodejs","python","sql","git","rest api","docker"],
    "mobile developer": ["kotlin","swift","react native","flutter","firebase","rest api","git","android","ios","ui/ux"],
}

SECTION_KEYWORDS = {
    "education": ["education","academic","university","college","degree","bachelor","master","phd","school","institution","cgpa","gpa","10th","12th"],
    "experience": ["experience","work","employment","internship","job","position","role","company","organization","worked","developed","built","led"],
    "skills": ["skills","technologies","tools","frameworks","languages","proficiencies","expertise","competencies"],
    "projects": ["projects","portfolio","built","developed","created","implemented","designed","deployed"],
    "certifications": ["certification","certificate","certified","course","training","bootcamp","credential","license"],
    "achievements": ["award","achievement","honor","recognition","winner","rank","topper","scholarship","merit"],
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def clean_text(text):
    return re.sub(r'\s+', ' ', text.lower())

def extract_email(text):
    match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'(\+?\d[\d\s\-().]{8,14}\d)', text)
    return match.group(0).strip() if match else None

def extract_name(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            if not any(kw in line.lower() for kw in ["resume","curriculum","vitae","profile","summary"]):
                return line
    return lines[0] if lines else "Unknown"

def detect_sections(text_lower):
    found = {}
    for section, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                found[section] = True
                break
    return found

def find_skills(text_lower, skill_list):
    found = []
    for skill in skill_list:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return found

def extract_years_experience(text_lower):
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience\s*(?:of\s*)?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
    ]
    for p in patterns:
        m = re.search(p, text_lower)
        if m:
            return int(m.group(1))
    return None

def extract_education_level(text_lower):
    if any(k in text_lower for k in ["phd","doctorate","doctor of"]):
        return "PhD"
    if any(k in text_lower for k in ["master","m.tech","msc","m.e","mba","m.s"]):
        return "Master's"
    if any(k in text_lower for k in ["bachelor","b.tech","b.e","bsc","b.s","undergraduate","ug"]):
        return "Bachelor's"
    if any(k in text_lower for k in ["diploma","polytechnic"]):
        return "Diploma"
    if any(k in text_lower for k in ["12th","hsc","higher secondary","plus two"]):
        return "12th/HSC"
    return "Not Detected"

def extract_cgpa(text_lower):
    m = re.search(r'(?:cgpa|gpa)[:\s]*([0-9.]+)', text_lower)
    if m:
        return m.group(1)
    m = re.search(r'([0-9.]+)\s*/\s*10(?:\s|$)', text_lower)
    if m:
        return m.group(1) + "/10"
    m = re.search(r'([0-9.]+)\s*/\s*4(?:\s|$)', text_lower)
    if m:
        return m.group(1) + "/4"
    return None

def count_projects(text_lower):
    lines = text_lower.split('\n')
    project_count = 0
    in_projects = False
    for line in lines:
        if any(kw in line for kw in ["projects","portfolio"]):
            in_projects = True
        elif in_projects and any(kw in line for kw in ["experience","education","skills","certifications","achievements"]):
            in_projects = False
        elif in_projects and line.strip() and len(line.strip()) > 10:
            if any(c in line for c in ['•','-','*','1.','2.','3.']):
                project_count += 1
    return max(project_count, text_lower.count('project'))

def calculate_score(sections, tech_skills_found, soft_skills_found, years_exp, education, role_match_pct, text_lower):
    score = 0
    breakdown = {}

    # Contact info (10 pts)
    contact_score = 0
    if extract_email(text_lower): contact_score += 5
    if extract_phone(text_lower): contact_score += 5
    breakdown['contact'] = contact_score
    score += contact_score

    # Sections completeness (20 pts)
    section_score = min(len(sections) * 4, 20)
    breakdown['sections'] = section_score
    score += section_score

    # Technical skills (25 pts)
    ts = min(len(tech_skills_found) * 2, 25)
    breakdown['technical_skills'] = ts
    score += ts

    # Soft skills (10 pts)
    ss = min(len(soft_skills_found) * 2, 10)
    breakdown['soft_skills'] = ss
    score += ss

    # Experience (15 pts)
    if years_exp:
        exp_score = min(years_exp * 3, 15)
    elif 'experience' in sections:
        exp_score = 8
    else:
        exp_score = 0
    breakdown['experience'] = exp_score
    score += exp_score

    # Education (10 pts)
    edu_map = {"PhD": 10, "Master's": 9, "Bachelor's": 7, "Diploma": 5, "12th/HSC": 3, "Not Detected": 0}
    edu_score = edu_map.get(education, 0)
    breakdown['education'] = edu_score
    score += edu_score

    # Role match (10 pts)
    role_score = int(role_match_pct / 10)
    breakdown['role_match'] = role_score
    score += role_score

    return min(score, 100), breakdown

def generate_recommendations(sections, tech_skills_found, soft_skills_found, years_exp, education, score, role, missing_role_skills):
    tips = []

    if 'summary' not in ' '.join(sections.keys()):
        tips.append("➕ Add a strong Professional Summary at the top (2-3 lines about yourself).")
    if 'experience' not in sections:
        tips.append("➕ Add Work Experience or Internship section with bullet points.")
    if 'projects' not in sections:
        tips.append("➕ Add a Projects section with at least 2-3 real projects.")
    if 'certifications' not in sections:
        tips.append("➕ Include Certifications or Online Courses (Coursera, Udemy, etc.).")
    if 'achievements' not in sections:
        tips.append("➕ Add Achievements, Awards, or Extracurricular activities.")
    if len(tech_skills_found) < 8:
        tips.append("➕ Expand your Technical Skills — list more tools, languages, and frameworks.")
    if len(soft_skills_found) < 3:
        tips.append("➕ Add Soft Skills like Leadership, Communication, Teamwork.")
    if missing_role_skills:
        tips.append(f"🎯 For '{role}' role, consider learning: {', '.join(missing_role_skills[:5])}.")
    if score < 50:
        tips.append("⚠️ Resume needs significant improvement — add more details to all sections.")
    elif score < 70:
        tips.append("✅ Good start! Add more projects and technical skills to strengthen it.")
    else:
        tips.append("🌟 Strong resume! Fine-tune formatting and tailor it for each job application.")

    tips.append("📄 Use action verbs: Built, Developed, Designed, Implemented, Led, Optimized.")
    tips.append("📏 Keep resume to 1 page (fresher) or max 2 pages (experienced).")
    return tips

# ─── Main Analyser ────────────────────────────────────────────────────────────

def analyse_resume(text, job_role=""):
    text_lower = clean_text(text)

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    education = extract_education_level(text_lower)
    cgpa = extract_cgpa(text_lower)
    years_exp = extract_years_experience(text_lower)
    sections = detect_sections(text_lower)

    tech_skills_found = find_skills(text_lower, TECH_SKILLS)
    soft_skills_found = find_skills(text_lower, SOFT_SKILLS)

    # Role matching
    role_match_pct = 0
    missing_role_skills = []
    matched_role_skills = []
    role_key = job_role.lower().strip() if job_role else ""
    best_role = role_key

    if not role_key:
        # Auto-detect best role
        best_score = 0
        for role, skills in JOB_ROLE_SKILLS.items():
            matches = sum(1 for s in skills if s in text_lower)
            if matches > best_score:
                best_score = matches
                best_role = role
        role_key = best_role

    if role_key in JOB_ROLE_SKILLS:
        required = JOB_ROLE_SKILLS[role_key]
        matched_role_skills = [s for s in required if s in text_lower]
        missing_role_skills = [s for s in required if s not in text_lower]
        role_match_pct = int((len(matched_role_skills) / len(required)) * 100)
    else:
        # Fuzzy match
        for role, skills in JOB_ROLE_SKILLS.items():
            if any(word in role for word in role_key.split()):
                required = skills
                matched_role_skills = [s for s in required if s in text_lower]
                missing_role_skills = [s for s in required if s not in text_lower]
                role_match_pct = int((len(matched_role_skills) / len(required)) * 100)
                best_role = role
                break

    # Scoring
    score, breakdown = calculate_score(sections, tech_skills_found, soft_skills_found, years_exp, education, role_match_pct, text_lower)

    # Grade
    if score >= 85: grade, grade_label = "A+", "Excellent"
    elif score >= 75: grade, grade_label = "A", "Very Good"
    elif score >= 65: grade, grade_label = "B+", "Good"
    elif score >= 55: grade, grade_label = "B", "Average"
    elif score >= 40: grade, grade_label = "C", "Needs Improvement"
    else: grade, grade_label = "D", "Poor"

    recommendations = generate_recommendations(sections, tech_skills_found, soft_skills_found, years_exp, education, score, best_role, missing_role_skills)

    return {
        "name": name,
        "email": email or "Not found",
        "phone": phone or "Not found",
        "education": education,
        "cgpa": cgpa or "Not mentioned",
        "years_experience": years_exp or "Not mentioned",
        "sections_found": list(sections.keys()),
        "technical_skills": tech_skills_found,
        "soft_skills": soft_skills_found,
        "detected_role": best_role.title(),
        "role_match_percent": role_match_pct,
        "matched_role_skills": matched_role_skills,
        "missing_role_skills": missing_role_skills,
        "overall_score": score,
        "grade": grade,
        "grade_label": grade_label,
        "score_breakdown": breakdown,
        "recommendations": recommendations,
        "word_count": len(text.split()),
    }
