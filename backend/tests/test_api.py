import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Импортируем твое приложение и зависимости
from main import app
from database import Base, get_db
import models
# 1. НАСТРОЙКА ТЕСТОВОЙ БАЗЫ ДАННЫХ (SQLite в памяти)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Переопределяем зависимость get_db, чтобы FastAPI использовал тестовую БД
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Создаем тестовый клиент
client = TestClient(app)


# Фикстура: создает таблицы перед тестами и удаляет после
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# --- ХЕЛПЕР (Вспомогательная функция для получения токена админа) ---
def получить_токен_админа():
    # 1. Регистрируем админа
    client.post("/register", json={
        "username": "test_admin",
        "password": "adminpassword",
        "role": "admin"
    })
    # 2. Логинимся
    response = client.post("/login", data={
        "username": "test_admin",
        "password": "adminpassword"
    })
    return response.json()["access_token"]


# ================= ТЕСТЫ =================

def test_главная_страница_доступна():
    """Тест 1: Проверяем, что главная страница API работает."""
    response = client.get("/")
    assert response.status_code == 200
    assert "работает" in response.json()["message"]


def test_регистрация_и_авторизация():
    """Тест 2: Проверяем, что пользователь может зарегистрироваться и войти."""
    # Используем уникальное имя, чтобы не было конфликта
    response = client.post("/register", json={
        "username": "test_user_unique",
        "password": "password123",  # Пароль больше 6 символов
        "role": "user"
    })
    assert response.status_code == 200, f"Ошибка регистрации: {response.text}"
    assert response.json()["username"] == "test_user_unique"

    # Логин
    response = client.post("/login", data={
        "username": "test_user_unique",
        "password": "password123"
    })
    assert response.status_code == 200, f"Ошибка логина: {response.text}"
    assert "access_token" in response.json()


def test_создание_марки_авто_без_прав():
    """Тест 3: Проверяем, что обычный пользователь НЕ МОЖЕТ создать марку."""
    # 1. Регистрируем юзера (пароль больше 6 символов)
    reg_response = client.post("/register",
                               json={"username": "just_user_unique", "password": "1234567", "role": "user"})
    assert reg_response.status_code == 200, f"Ошибка регистрации: {reg_response.text}"

    # 2. Логинимся и получаем токен
    login_response = client.post("/login", data={"username": "just_user_unique", "password": "1234567"})
    assert login_response.status_code == 200, f"Ошибка логина: {login_response.text}"
    token = login_response.json()["access_token"]

    # 3. Пытаемся создать марку с токеном обычного юзера
    response = client.post(
        "/brands/",
        json={"name": "Toyota"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. Ожидаем 403 Forbidden
    assert response.status_code == 403, f"Ожидали 403, но получили {response.status_code}. Ответ: {response.text}"
def test_создание_марки_админом():
    """Тест 4: Проверяем, что админ МОЖЕТ создать марку."""
    token = получить_токен_админа()

    response = client.post(
        "/brands/",
        json={"name": "Lada"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Lada"


def test_создание_запчасти():
    """Тест 5: Проверяем создание запчасти (имитируем поставщика)."""
    # Создаем админа (чтобы он создал поставщика)
    token = получить_токен_админа()

    # Сначала создаем поставщика
    response = client.post(
        "/suppliers/",
        json={"name": "ООО Ромашка", "contact_info": "test@mail.ru", "user_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    supplier_id = response.json()["id"]

    # Создаем запчасть
    response = client.post(
        "/parts/",
        json={
            "article": "ART-123",
            "name": "Фильтр масляный",
            "price": 500.0,
            "stock_quantity": 10,
            "supplier_id": supplier_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["article"] == "ART-123"


def test_получение_списка_запчастей():
    """Тест 6: Проверяем, что список запчастей доступен (для всех)."""
    response = client.get("/parts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)