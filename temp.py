from app import app, db, User

with app.app_context():
    user = User.query.filter_by(brugernavn="thomedak").first()
    user.admin = True
    db.session.commit()
    print("Done")
