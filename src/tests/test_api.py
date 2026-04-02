from http.client import responses
from tkinter.font import names

import pytest
from unicodedata import category
from watchfiles import awatch

from src.models.models import AdType, UserRole, User, Ad, Category
from src.main import app
from src.auth.security import get_current_user
from src.api.ads import send_notification
from datetime import datetime


async def override_get_current_user():
    new_user = User(
        id=1,
        username="test_student",
        email="fake@test.com",
        hashed_password="fake_hashed_password_123",
        role=UserRole.USER,
        bio="Тестовый био",
        location="Тестовая локация",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return new_user


async def test_create_user_with_existing_email(client, db_session):
    new_user = User(
        username="piska",
        email="user@example.com",
        hashed_password="fake_hashed_password_123"
    )
    db_session.add(new_user)
    await db_session.commit()

    bad_user = {
        "username": "oiska",
        "email": "user@example.com",
        "password": "poh"
    }

    response = client.post("/auth/register", json=bad_user)

    assert response.status_code == 400

    assert response.json()["detail"] == "Email already exists"


async def test_update_title_of_ad(client, create_10_ads):
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.patch("/ads/1", json={"title": "test"})

    assert response.status_code == 200

    assert response.json()["message"] == "Updated successfully"

    del app.dependency_overrides[get_current_user]


async def test_delete_ad_with_no_access(client, create_10_ads):
    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.delete("/ads/5")

    assert response.status_code == 409
    assert response.json()["detail"] == "No access"

    del app.dependency_overrides[get_current_user]


async def test_get_ad_with_filtr(client, create_10_ads):
    query_params = {
        "category_id": 2,
        "limit": 15,
        "offset": 0
    }

    response = client.get("/ads", params=query_params)
    assert response.status_code == 200

    assert len(response.json()) == 1


async def test_select_id_with_wrong_cat(client, create_10_ads):
    query_params = {
        "category_id" : 9999999
    }

    response = client.get("/ads",params=query_params)

    assert response.status_code==200


async def test_creating_ad_with_wrong_category(client, create_10_ads):
    app.dependency_overrides[get_current_user] = override_get_current_user

    query = {
        "title": "superpuper",
        "description": "...",
        "type": AdType.OFFER,
        "category_id": 999999

    }

    response = client.post("/ads", json=query)

    assert response.status_code == 404

    del app.dependency_overrides[get_current_user]


async def test_ad_creating_with_mock(client,mocker, create_10_ads):
    app.dependency_overrides[get_current_user] = override_get_current_user

    mock = mocker.patch("src.api.ads.send_notification")
    mock.return_value = True

    query = {
        "title": "superpuper",
        "description": "...",
        "type": AdType.OFFER,
        "category_id": 1
    }

    response = client.post("/ads", json=query)

    assert response.status_code == 200
    mock.assert_called_once()

    del app.dependency_overrides[get_current_user]


@pytest.fixture()
async def create_10_user(db_session):
    for i in range(1, 11):
        new_user = User(
            id=i,
            username=f"test_student{i}",
            email=f"fake@test.com{i}",
            hashed_password="fake_hashed_password_123",
            role=UserRole.USER,
            bio="Тестовый био",
            location="Тестовая локация",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(new_user)
    await db_session.commit()


@pytest.fixture()
async def create_10_categories(db_session):
    for i in range(1, 11):
        new_cat = Category(
            id=i,
            name=f"test_student{i}",
        )
        db_session.add(new_cat)
    await db_session.commit()


@pytest.fixture()
async def create_10_ads(db_session, create_10_categories, create_10_user):
    for i in range(1, 11):
        new_ad = Ad(
            id=i,
            title=f"Объявление",
            description="...",
            user_id=i,
            category_id=i
        )
        db_session.add(new_ad)
    await db_session.commit()





# async def override_get_current_user():
#     fake_user = User(
#         id=1,
#         username="test_student",
#         email="fake@test.com",
#         hashed_password="fake_hashed_password_123",
#         role=UserRole.USER,
#         bio="Тестовый био",
#         location="Тестовая локация",
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow()
#     )
#     return fake_user
#
#
# def test_read_root(client):
#     response = client.get("/ads")
#     assert response.status_code == 200
#
#
# def test_create_ad_validation_error(client):
#     bad_payload = {
#         "title": "уроки питончика",
#         "description": "...",
#         "type": AdType.OFFER,
#         "category_id": "sasi"
#     }
#
#     app.dependency_overrides[get_current_user] = override_get_current_user
#
#     response = client.post("/ads", json=bad_payload)
#
#     assert response.status_code == 422
#
#     error_detail = response.json()["detail"]
#     assert error_detail[0]["loc"] == ["body", "category_id"]
#     assert error_detail[0]["type"] == "int_parsing"
#
#     app.dependency_overrides.clear()
#
#
# def test_get_ad_not_found(client):
#     app.dependency_overrides[get_current_user] = override_get_current_user
#
#     response = client.delete("/ads/999999")
#
#     assert response.status_code == 404
#
#
# def test_create_and_delete_ad(client):
#     app.dependency_overrides[get_current_user] = override_get_current_user
#
#     response = client.post("/ads", json={
#         "title": "уроки питончика",
#         "description": "...",
#         "type": AdType.OFFER,
#         "category_id": 1
#     })
#
#     assert response.status_code == 200
#
#     created_id = response.json()["id"]
#
#     response = client.delete(f"/ads/{created_id}")
#
#     assert response.status_code == 200
#
#     app.dependency_overrides.clear()
#
#
# @pytest.fixture
# async def create_15_ads(db_session):
#     test_user = User(
#         username="test_author",
#         email="author@test.com",
#         hashed_password="123",
#         role=UserRole.USER
#     )
#     db_session.add(test_user)
#
#     test_category = Category(name="IT Услуги")
#     db_session.add(test_category)
#
#     await db_session.flush()
#
#     for i in range(15):
#         new_ad = Ad(title=f"Объявление {i}", description="...", user_id=test_user.id, category_id=test_category.id)
#         db_session.add(new_ad)
#
#     await db_session.commit()
#
#
# @pytest.mark.nowtest
# @pytest.mark.parametrize("limit, offset", [
#     (100, 0),
#     (250, 0),
#     (15, 9)
# ])
# def test_get_ad_endpoint(client, create_15_ads, limit, offset):
#     query_params = {
#         "limit": limit,
#         "offset": offset
#     }
#     response = client.get("/ads", params=query_params)
#     if limit > 100:
#         assert response.status_code == 422
#         assert response.json()["detail"][0]["loc"] == ["query", "limit"]
#     else:
#         assert response.status_code == 200
#
#         assert isinstance(response.json(), list)
#
#
#
