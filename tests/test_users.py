from app.core.security import bcrypt_context
from app.models import User
from tests.conftest import client


def test_get_me(test_user):
    response = client.get("/users/me")
    data = response.json()

    assert response.status_code == 200
    assert data.get("id") == test_user.id
    assert data.get("username") == test_user.username
    assert data.get("email") == test_user.email
    assert data.get("role") == test_user.role


def test_get_all_users(test_user):
    response = client.get("/users/")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0].get("id") == test_user.id


def test_get_user_by_id(test_user):
    response = client.get(f"/users/{test_user.id}")

    assert response.status_code == 200
    assert response.json().get("id") == test_user.id


def test_get_user_by_id_not_found():
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "The specified user could not be found."}


def test_update_user_password(db_session, test_user):
    request_data = {"old_password": "12345", "new_password": "54321"}
    response = client.put("/users/password", json=request_data)
    data = response.json()

    assert response.status_code == 200
    assert data == {
        "status": "success",
        "message": "Password has been updated successfully.",
    }

    updated_user = db_session.get(User, test_user.id)
    assert bcrypt_context.verify(
        request_data.get("new_password"), updated_user.hashed_password
    )


def test_update_user_password_incorrect():
    request_data = {"old_password": "wrongpassword", "new_password": "54321"}
    response = client.put("/users/password", json=request_data)
    data = response.json()

    assert response.status_code == 403
    assert data == {"detail": "The old password you entered is incorrect."}


def test_update_user_role(test_user):
    request_data = {"role": "driver"}
    response = client.put(f"/users/{test_user.id}/role", json=request_data)

    assert response.status_code == 200
    assert response.json().get("role") == request_data.get("role")


def test_update_user_role_unauthorized(db_session, test_user):
    test_user.role = "driver"
    db_session.commit()

    request_data = {"role": "admin"}
    response = client.put(f"/users/{test_user.id}/role", json=request_data)

    assert response.status_code == 403
    assert response.json() == {
        "detail": "You are not authorized to perform this action."
    }


def test_delete_me():
    request_data = {"password": "12345"}
    response = client.request("DELETE", "/users/me", json=request_data)

    assert response.status_code == 204


def test_delete_me_incorrect_password():
    request_data = {"password": "wrongpassword"}
    response = client.request("DELETE", "/users/me", json=request_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "The password you entered is incorrect."}


def test_delete_user_by_id(db_session):
    new_user = User(
        username="new_user",
        email="new_user@email.com",
        role="admin",
        hashed_password=bcrypt_context.hash("12345"),
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    response = client.delete(f"/users/{new_user.id}")
    assert response.status_code == 204

    deleted_user = db_session.query(User).filter(User.id == new_user.id).first()
    assert deleted_user is None


def test_user_response_serialization():
    response = client.get("/users/me")
    data = response.json()
    expected_keys = {"id", "username", "email", "role"}

    assert set(data.keys()) == expected_keys
