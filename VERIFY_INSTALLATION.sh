#!/bin/bash

echo "=========================================="
echo "SkillSpark Pro - Installation Verification"
echo "=========================================="
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 installed: $(python3 --version)"
else
    echo "✗ Python 3 not found"
fi

# Check file structure
echo ""
echo "Checking file structure..."

files=(
    "backend/app.py"
    "backend/database.py"
    "backend/auth.py"
    "backend/students.py"
    "backend/jobs.py"
    "backend/exams.py"
    "backend/proctoring.py"
    "backend/admin.py"
    "frontend/index.html"
    "frontend/css/styles.css"
    "frontend/js/common.js"
    "frontend/js/auth.js"
    "frontend/js/student.js"
    "frontend/js/exam.js"
    "frontend/js/proctoring.js"
    "frontend/js/admin.js"
    "requirements.txt"
    "README.md"
)

missing=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file MISSING"
        ((missing++))
    fi
done

echo ""
echo "=========================================="
if [ $missing -eq 0 ]; then
    echo "✓ ALL FILES PRESENT - Installation Complete!"
else
    echo "✗ $missing files missing"
fi
echo "=========================================="
echo ""
echo "File counts:"
echo "- Backend Python: $(find backend -name "*.py" | wc -l) files"
echo "- Frontend HTML: $(find frontend -name "*.html" | wc -l) files"
echo "- Frontend JS: $(find frontend/js -name "*.js" | wc -l) files"
echo "- Total Files: $(find . -type f \( -name "*.html" -o -name "*.js" -o -name "*.css" -o -name "*.py" -o -name "*.md" \) | grep -v __pycache__ | wc -l)"
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Create .env file (see .env.example)"
echo "3. Initialize database: python backend/database.py"
echo "4. Seed data: python backend/seed_admin.py && python backend/seed_courses.py"
echo "5. Start server: python backend/app.py"
echo "6. Open frontend/index.html in browser"
echo ""
