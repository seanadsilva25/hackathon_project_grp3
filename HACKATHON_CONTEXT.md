# Hackathon Context

## Current Status

The hackathon starts at 2:00 PM.

The initial full-stack boilerplate is already complete and tested.

### Frontend
- React + Vite
- JavaScript
- ESLint
- react-router-dom installed
- Runs with `npm run dev`
- Frontend runs on http://localhost:5173

### Backend
- Flask
- Python 3.11.9
- Virtual environment: `backend/venv`
- Flask, flask-cors, Flask-SQLAlchemy and python-dotenv installed
- Backend runs with `python run.py`
- Backend runs on http://127.0.0.1:5000

### Working API
GET `/api/health`

Response:

{
  "message": "Backend is running",
  "status": "ok"
}

### Frontend ↔ Backend
React successfully calls the Flask `/api/health` endpoint using `fetch()`.

The browser successfully displays:

Backend Status: Backend is running

Therefore the basic full-stack connection is verified.

---

## Current Structure

hackathon_project_grp3/

frontend/
- React/Vite application
- src/components/
- src/pages/
- src/layouts/
- src/services/
- src/hooks/
- src/utils/
- src/App.jsx
- src/main.jsx
- src/index.css

backend/
- app/
  - __init__.py
  - routes.py
  - models.py
- venv/
- .env
- .gitignore
- requirements.txt
- run.py

Do not recreate the project or virtual environment.

Do not change Python version unless there is a specific technical reason.

---

# Hackathon Development Strategy

The actual problem statement will be provided at 2:00 PM.

DO NOT build problem-specific features before seeing the problem statement.

Once the problem statement is available, follow this process:

1. Understand the problem.
2. Identify the target users.
3. Identify the core problem that must be solved.
4. Extract the required features.
5. Separate essential MVP features from optional features.
6. Decide what can realistically be completed within the remaining hackathon time.
7. Design the application flow.
8. Decide whether a database is required.
9. Design only the necessary database models.
10. Design Flask API endpoints.
11. Design React pages and components.
12. Decide whether AI/ML is genuinely useful or required.
13. Choose the simplest reliable implementation.
14. Build the backend.
15. Build the frontend.
16. Integrate frontend and backend.
17. Test the complete user flow.
18. Fix critical bugs.
19. Improve UI only after functionality works.
20. Prepare a clean demo flow and presentation.

---

# Important Hackathon Rules

Prioritize a WORKING END-TO-END MVP over having many unfinished features.

Do not overengineer.

Do not add libraries unless they solve an actual requirement.

Do not create unnecessary authentication, database tables, AI models, dashboards, or APIs before they are justified by the problem.

If AI/ML is required, choose the simplest reliable approach that can be demonstrated during the hackathon.

Keep the existing React ↔ Flask connection working.

Make incremental changes and test after major changes.

Before making a major architectural change, explain why it is needed.

Never hardcode API keys, passwords, or secrets.

Use `.env` for secrets and environment-specific configuration.

Do not commit `venv/`, `node_modules/`, `.env`, or other generated files to GitHub.

---

# Preferred Architecture

React frontend
        ↓
      HTTP
        ↓
Flask REST API
        ↓
Application logic
        ↓
Database / external API / AI service
only when required by the problem

Keep frontend and backend separated.

Keep backend API routes under `/api`.

---

# Time Strategy

The hackathon is only 18 hours.

Recommended priority:

1. Core functionality
2. End-to-end integration
3. Reliability/testing
4. Good UI
5. Demo/presentation
6. Optional features only if time remains

If time becomes limited, cut optional features rather than leaving the core flow incomplete.

The final demo should tell one clear user story from beginning to end.

We are preparing a reusable frontend boilerplate for an 18-hour hackathon.

Current project structure:
- frontend: React + Vite + JavaScript
- Tailwind CSS v4 is installed and working using @tailwindcss/vite
- react-router-dom is installed
- backend: Flask
- Python 3.11 virtual environment
- Flask backend currently has a working GET /api/health endpoint
- React → Flask connection has already been tested successfully

IMPORTANT:
Do NOT change or break the existing React → Flask /api/health functionality.
Do NOT introduce a database yet.
Do NOT implement real authentication/JWT/password hashing yet.
We MAY use Supabase later, so avoid creating authentication/database architecture that could become unnecessary.

TASK:
Create a clean, reusable frontend boilerplate for the hackathon.

Create this structure:

frontend/src/
├── components/
│   ├── Button.jsx
│   ├── Input.jsx
│   ├── Navbar.jsx
│   ├── Loading.jsx
│   └── ProtectedRoute.jsx
│
├── layouts/
│   ├── AuthLayout.jsx
│   └── DashboardLayout.jsx
│
├── pages/
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── ForgotPassword.jsx
│   ├── ResetPassword.jsx
│   ├── Dashboard.jsx
│   ├── Profile.jsx
│   ├── NotFound.jsx
│   └── Unauthorized.jsx
│
├── services/
│   └── api.js
│
├── hooks/
├── utils/
├── App.jsx
└── index.css

Requirements:

1. Set up React Router properly.

Routes:
- /login
- /register
- /forgot-password
- /reset-password
- /dashboard
- /profile
- /unauthorized
- fallback route for NotFound

2. Create clean, functional Login and Register forms.
They do NOT need to connect to a real database or authentication provider yet.

For now:
- Login form should accept email and password.
- Register form should accept name, email and password.
- Include basic frontend validation.
- Show appropriate validation/error messages.
- Include loading states where appropriate.
- Use reusable Input and Button components.

3. Create ForgotPassword and ResetPassword UI pages.
These are only frontend placeholders/forms for now. Do not implement real password reset.

4. Create AuthLayout for authentication pages.

5. Create DashboardLayout for authenticated/application pages.

6. Create a basic Navbar component with navigation links.

7. Create Dashboard and Profile placeholder pages with clean Tailwind styling.

8. Create ProtectedRoute.jsx as a reusable structure for protecting routes.
For now, do NOT implement actual authentication.
Use a simple placeholder mechanism or clearly marked TODO so it can later be connected to Supabase Auth or another authentication system.

9. Create services/api.js.

It should contain a reusable API request helper using:
http://127.0.0.1:5000/api

It must support GET, POST, PUT/PATCH and DELETE through a generic function.

Do not hardcode API calls throughout individual components.

10. Preserve the existing Flask health-check test.
The application should still be able to verify:
GET /api/health

11. Use Tailwind CSS for styling.
Keep the UI clean, modern, simple and professional.
Do not spend excessive time on visual animations or unnecessary design complexity.

12. Do NOT install unnecessary packages.
Use the packages already installed wherever possible.

13. Do not modify the Flask backend except if absolutely necessary for the existing health-check connection.

14. Do not create database models, migrations, JWT authentication, Supabase configuration, OAuth, email services, or password hashing yet.

15. Keep the code simple and easy to modify once the actual hackathon problem statement is revealed.

Before making changes:
- Inspect the existing frontend files.
- Preserve working code where possible.
- Do not blindly overwrite files that already contain working functionality.

After making changes:
- Check for import errors.
- Make sure npm run dev works.
- Make sure all routes render correctly.
- Make sure the existing Flask /api/health connection still works.
- Tell me exactly which files you created/modified and summarize any important decisions.

## Current Development Rule

This file describes the intended reusable boilerplate and current project state.

Before making changes:
- Read this file.
- Inspect the existing code.
- Preserve working functionality.
- Do not make architectural decisions that depend on the unknown hackathon problem statement.
- Ask before introducing major new dependencies or changing the backend architecture.

After major changes, update this file if the project structure, technology choices, or verified functionality changes.