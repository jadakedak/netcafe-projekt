from app import app, db, User

with app.app_context():
    deleted = User.query.filter(User.brugernavn != "thomedak").delete()
    db.session.commit()
    print(f"Deleted {deleted} user(s)")
