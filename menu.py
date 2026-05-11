from uuid import uuid4
from app import app, db, Menuitem


def add_menu_item(navn, beskrivelse, pris, billede_sti=None):
    with app.app_context():
        item = Menuitem(
            item_id=str(uuid4()),
            navn=navn,
            beskrivelse=beskrivelse,
            pris=pris,
            billede_sti=billede_sti
        )
        db.session.add(item)
        db.session.commit()
        print(f"Added menu item: {navn}")


def clear_menu_items():
    with app.app_context():
        count = db.session.query(Menuitem).delete()
        db.session.commit()
        print(f"Cleared {count} menu items")


if __name__ == "__main__":
    clear_menu_items()
