from app import app, db, User, Bookings

with app.app_context():
    deleted_bookings = Bookings.query.delete()
    db.session.commit()
    print(f"Deleted {deleted_bookings} booking(s)")
