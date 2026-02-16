from werkzeug.security import generate_password_hash
from database import get_db_connection

def seed_admin():
    """Create default admin account"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE usn='ADMIN001'")
    if cursor.fetchone():
        print("Admin account already exists (USN: ADMIN001)")
        conn.close()
        return

    # Create admin
    hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')

    cursor.execute('''
        INSERT INTO users (usn, name, email, password, role)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        'ADMIN001',
        'System Administrator',
        'admin@skillspark.com',
        hashed_password,
        'admin'
    ))

    conn.commit()
    conn.close()

    print("✓ Default admin account created successfully")
    print("  USN: ADMIN001")
    print("  Password: admin123")
    print("  IMPORTANT: Change password after first login!")

if __name__ == '__main__':
    seed_admin()
