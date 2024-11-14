import pytest
from rest_framework.test import APIClient
import base64
from users.models import CustomUser, Contact


# for testing change POSTGRES_HOST to 127.0.0.1 in .env file

@pytest.fixture
def client():
    """
    Fixture that returns an instance of `rest_framework.test.APIClient`,
    which is a test client for making requests to your Django views.
    """
    return APIClient()


@pytest.fixture
def user():
    """
    Fixture that returns a `CustomUser` instance created with
    the given email and password.
    This user can be used for testing purposes.
    """
    user = CustomUser.objects.create_user(email='test_user@mail.ru', password='secret', is_active=True)
    return user


@pytest.fixture
def contact(user):
    """
    Fixture that returns a `Contact` instance created with the given city, street, house, structure, building, apartment, phone, and additional description.
    This contact can be used for testing purposes.
    """
    contact = Contact.objects.create(
        city='test',
        street='test',
        house='test',
        structure='test',
        building='test',
        apartment='test',
        phone='test',
        additional_desc='',
        user=user
    )
    return contact


def encode_base64(string: str) -> str:
    return base64.b64encode(string.encode()).decode()

@pytest.mark.parametrize(
    ["email", "status_code"],
    (
        ("test_user@mail.ru", 201),
        ("test_user@mailru", 400),
    )
)
@pytest.mark.django_db
def test_create_user(client, email, status_code):
    response1 = client.post('/api/v1/registration/', data={
        'email': email,
        'password': 'secret',
    })
    data = response1.json()
    new_user = CustomUser.objects.filter(email='test_user@mail.ru').first()

    assert response1.status_code == status_code
    if new_user:
        assert data == {"Success": "Account created successfully, please confirm your email"}
        assert new_user.is_active is False


@pytest.mark.django_db
def test_update_user(client, user):
    # when user update email, account will be deactivated
    response = client.patch('/api/v1/update_user/', data={
        'email': 'new_email@mail.ru',
        'password': 'secret',
    }, headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'
    })
    user.refresh_from_db()

    response1 = client.post('/api/v1/registration/', data={
        'email': 'new_email@mail.ru',
        'password': 'secret',
    })

    assert response.status_code == 201
    assert user.is_active == False
    assert response1.status_code == 400


@pytest.mark.django_db
def test_create_contact(client, user):
    response = client.post('/api/v1/add_contact/', data={
        'city': 'test',
        'street': 'test',
        'house': 'test',
        'structure': 'test',
        'building': 'test',
        'apartment': 'test',
        'phone': 'test',
        'additional_desc': '',
    }, headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'
    })
    contact = Contact.objects.get(user=user.id)

    assert response.status_code == 201
    assert contact.user == user

@pytest.mark.django_db
def test_update_contact(client, user, contact):
    put_response = client.put(f'/api/v1/update_contact/{contact.id}/', data={
        'city': 'test1',
        'street': 'test2',
        'house': 'test3',
    }, headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'
    })
    contact.refresh_from_db()

    assert put_response.status_code == 200
    assert contact.city == 'test1'
    assert contact.street == 'test2'
    assert contact.house == 'test3'
    assert contact.structure == 'test'


@pytest.mark.django_db
def test_get_contacts(client, user, contact):
    get_response = client.get('/api/v1/contacts/', headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'
    })
    data = get_response.json()

    assert get_response.status_code == 200
    assert data[0].get('city') == 'test'


@pytest.mark.django_db
def test_delete_contact(client, user, contact):
    delete_response = client.delete(f'/api/v1/delete_contact/{contact.id}/', headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'})

    assert delete_response.status_code == 204