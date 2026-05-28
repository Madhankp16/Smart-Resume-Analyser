# ⚡ Smart Resume Analyser — AI Powered

## Features
- 📄 Upload PDF, DOCX, or TXT resume
- 🤖 AI-based skill extraction and scoring
- 🎯 Job role matching (10 roles supported)
- 📊 Detailed score breakdown with visual charts
- 💡 Personalized recommendations
- 🎨 Beautiful dark-themed UI

## Setup & Run

### Step 1 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run the app
```bash
python app.py
```

### Step 3 — Open in browser
```
http://localhost:5000
```

## Project Structure
```
smart_resume_analyser/
├── app.py                  ← Flask backend (main server)
├── requirements.txt        ← Python dependencies
├── README.md
├── utils/
│   ├── __init__.py
│   └── analyser.py         ← AI resume analysis logic
├── templates/
│   └── index.html          ← Frontend HTML
├── static/
│   ├── css/
│   │   └── style.css       ← Styling
│   └── js/
│       └── main.js         ← Frontend JS
└── uploads/                ← Temp folder (auto-created)
```

## Supported Job Roles
- Software Engineer
- Data Scientist
- Web Developer
- Full Stack Developer
- Frontend Developer
- Backend Developer
- DevOps Engineer
- AI/ML Engineer
- Data Analyst
- Mobile Developer

## How Scoring Works
| Category        | Max Points |
|-----------------|-----------|
| Contact Info    | 10        |
| Sections        | 20        |
| Tech Skills     | 25        |
| Soft Skills     | 10        |
| Experience      | 15        |
| Education       | 10        |
| Role Match      | 10        |
| **Total**       | **100**   |

## Grades
| Score | Grade | Label          |
|-------|-------|----------------|
| 85+   | A+    | Excellent       |
| 75+   | A     | Very Good       |
| 65+   | B+    | Good            |
| 55+   | B     | Average         |
| 40+   | C     | Needs Work      |
| <40   | D     | Poor            |
