from database import get_db_connection

def seed_courses():
    """Insert pre-defined courses"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if courses already exist
    cursor.execute("SELECT COUNT(*) as count FROM courses")
    if cursor.fetchone()['count'] > 0:
        print("Courses already exist in database")
        conn.close()
        return

    courses = [
        {
            'title': 'Python Programming',
            'category': 'programming',
            'description': 'Learn Python from basics to advanced concepts including OOP, file handling, and popular libraries',
            'content': 'Variables, Data Types, Control Flow, Functions, OOP, File I/O, Exception Handling, Libraries',
            'duration_hours': 40
        },
        {
            'title': 'Java Programming',
            'category': 'programming',
            'description': 'Master Java programming with focus on OOP, collections, exception handling, and multithreading',
            'content': 'Java Syntax, OOP Principles, Collections Framework, Exceptions, Multithreading, File I/O',
            'duration_hours': 45
        },
        {
            'title': 'C/C++ Programming',
            'category': 'programming',
            'description': 'Deep dive into C/C++ including pointers, memory management, and STL',
            'content': 'Pointers, Memory Management, Data Structures, STL, File Handling, Advanced Concepts',
            'duration_hours': 35
        },
        {
            'title': 'Quantitative Aptitude',
            'category': 'aptitude',
            'description': 'Master quantitative aptitude for placement tests including arithmetic, algebra, and data interpretation',
            'content': 'Arithmetic, Percentages, Ratios, Algebra, Geometry, Data Interpretation, Speed & Distance',
            'duration_hours': 30
        },
        {
            'title': 'Logical Reasoning',
            'category': 'aptitude',
            'description': 'Develop logical reasoning skills for placement tests with puzzles, patterns, and analytical questions',
            'content': 'Patterns, Sequences, Blood Relations, Puzzles, Syllogisms, Statement Analysis',
            'duration_hours': 25
        },
        {
            'title': 'Verbal Ability',
            'category': 'aptitude',
            'description': 'Enhance English language skills including grammar, vocabulary, and comprehension',
            'content': 'Vocabulary, Grammar, Sentence Correction, Reading Comprehension, Verbal Analogies',
            'duration_hours': 20
        }
    ]

    for course in courses:
        cursor.execute('''
            INSERT INTO courses (title, category, description, content, duration_hours)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            course['title'],
            course['category'],
            course['description'],
            course['content'],
            course['duration_hours']
        ))

    conn.commit()
    conn.close()

    print(f"✓ Successfully seeded {len(courses)} courses:")
    for course in courses:
        print(f"  - {course['title']} ({course['category']}, {course['duration_hours']} hours)")

if __name__ == '__main__':
    seed_courses()
