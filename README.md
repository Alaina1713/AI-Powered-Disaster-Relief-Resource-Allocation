# AI-Powered-Disaster-Relief-Resource-Allocation
Full-stack AI-powered disaster relief resource allocation system. Predicts region-wise needs (food, medical, shelter) using Flask, React, and SQLite with CSV uploads and ~83% heuristic accuracy.\

# Accuracy (demo heuristic): ~83%
Input: Region name or CSV of past disasters  
Output: Predicted resources required + confidence score  

# Features
- Upload disaster event data via CSV 📂  
- Predict resource requirements for regions 🌍  
- SQL-backed database for regions and past disasters 🗄️  
- Clean React dashboard styled with Tailwind 🎨  
- Sample dataset included for quick testing  

# Quick Start

### Backend (Flask)
bash
cd backend
python -m venv venv
# mac/linux
source venv/bin/activate
# windows
venv\Scripts\activate

pip install -r requirements.txt
python app.py
