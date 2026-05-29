import requests

BASE_URL = "http://localhost:5000"

USER_A = {"brugernavn": "thomedak", "adgangskode": "Jakob18aar"}
USER_B = {"brugernavn": "anders", "adgangskode": "Jakob18aar"}

AUTHORIZED_USER_ID = "0d87e46c-0b91-4f5d-b7e9-8768125af65a"

BOOKING_PAYLOAD = {
    "computer_id": "1",
    "booking_start": "2027-01-01T10:00:00",
    "booking_end": "2027-01-01T12:00:00",
}

def login(session, credentials):
    resp = session.post(f"{BASE_URL}/api/login", json=credentials)
    assert resp.status_code == 200, f"Login fejlede: {resp.text}"
    return resp.json()["user_id"]


def test_authorized_booking():
    s = requests.Session()
    login(s, USER_A)

    payload = {**BOOKING_PAYLOAD, "userid": AUTHORIZED_USER_ID}
    resp = s.post(f"{BASE_URL}/api/bookings/add", json=payload)

    assert resp.status_code == 201, f"Forventede 201, fik {resp.status_code}: {resp.text}"
    print(f"[PASS] Autoriseret booking oprettet: {resp.json()}")


def test_unauthorized_booking_other_user_id():
    session_b = requests.Session()
    login(session_b, USER_B)

    payload = {**BOOKING_PAYLOAD, "userid": AUTHORIZED_USER_ID}
    resp = session_b.post(f"{BASE_URL}/api/bookings/add", json=payload)

    assert resp.status_code == 401, (
        f"Forventede 401 Unauthorized, fik {resp.status_code}: {resp.text}"
    )
    print(f"[PASS] Server afviste booking med anden brugers ID: {resp.json()}")


def test_unauthenticated_booking():
    s = requests.Session()
    payload = {**BOOKING_PAYLOAD, "userid": AUTHORIZED_USER_ID}
    resp = s.post(f"{BASE_URL}/api/bookings/add", json=payload)

    assert resp.status_code == 401, f"Forventede 401, fik {resp.status_code}: {resp.text}"
    print(f"[PASS] Uautoriseret request uden session afvist: {resp.json()}")


if __name__ == "__main__":
    print("Kører API-tests...\n")
    try:
        test_authorized_booking()
    except AssertionError as e:
        print(f"[FAIL] test_authorized_booking: {e}")

    try:
        test_unauthorized_booking_other_user_id()
    except AssertionError as e:
        print(f"[FAIL] test_unauthorized_booking_other_user_id: {e}")

    try:
        test_unauthenticated_booking()
    except AssertionError as e:
        print(f"[FAIL] test_unauthenticated_booking: {e}")
