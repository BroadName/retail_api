import pytest
from rest_framework.test import APIClient
import base64

from backend.models import Shop, Product, ProductInfo, Order, OrderItem
from users.models import CustomUser, Contact



@pytest.fixture
def client():
    """
    Fixture that returns an instance of `rest_framework.test.APIClient`,
    which is a test client for making requests to your Django views.
    """
    return APIClient()


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


@pytest.fixture
def user():
    """
    Fixture that returns a `CustomUser` instance created with
    the given email and password.
    This user can be used for testing purposes.
    """
    user = CustomUser.objects.create_user(email='test_user@mail.ru', password='secret', is_active=True, type='shop')
    return user


@pytest.fixture
def products(client):
    response = client.post('/api/v1/upload/', data={
        'url': 'https://raw.githubusercontent.com/BroadName/retail_api/refs/heads/main/shop1.yaml',
    }, headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'
    })
    products = Product.objects.all()
    return products


def encode_base64(string: str) -> str:
    """
    Encodes a given string using base64 and decodes the result back to string.

    Args:
        string (str): The string, that contains email and password, to be encoded.

    Returns:
        str: The base64 encoded string, decoded back to string.
    """
    return base64.b64encode(string.encode()).decode()

@pytest.mark.parametrize(
    ['quantity', 'status_code', 'shop_id', 'product_1_id', 'product_2_id'],
    (
        (1, 201, 1, 1, 2 ),
        (100, 403, 2, 15, 16 ),
    )
)
@pytest.mark.django_db
def test_create_delete_order(client, user, contact, products, quantity, status_code, shop_id, product_1_id, product_2_id):
    """
    Tests the creation of a new order.

    Tests that the API returns 201 status code when creates a new `Order` instance, which
    creates `OrderItem` instance, and that the order has the correct contact,
    user, status, and number of order items.

    Also tests that basket endpoint returns 200 status code and the correct data when
    retrieving the basket of the user.
    """

    #shop_id = products.first().product_info.first().shop_id

    response = client.post('/api/v1/add_order_items/',
                          data={
                                "contact": contact.id,
                                "order_items":
                                    [
                                        {
                                            "product":
                                            {
                                                "id": product_1_id
                                            },
                                            "quantity": quantity,
                                            "shop": shop_id
                                        },

                                        {
                                            "product":
                                            {
                                                "id": product_2_id
                                            },
                                            "quantity": 1,
                                            "shop": shop_id
                                        }
                                    ]
                                },
                          headers={
                              'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
                              'Content-Type': 'application/json'
                          })

    response_1 = client.get('/api/v1/basket', headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'
    })

    basket = response_1.json()

    order = Order.objects.all().first()

    assert response.status_code == status_code
    if response.status_code == 201:
        assert order is not None
        assert OrderItem.objects.all().first()
        assert order
        assert order.contact == contact
        assert order.user == user
        assert order.status == 'new'
        assert order.orderitem_set.count() == 2

        assert response_1.status_code == 200
        assert basket[0].get('order') == 1
        assert basket[0].get('product').get('id') == 2
        assert basket[1].get('product').get('id') == 1
        assert basket[0].get('quantity') == 1

        response_to_delete = client.delete('/api/v1/delete_order_item/{100}/', headers={
            'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
            'Content-Type': 'application/json'
        })
        assert response_to_delete.status_code == 404

        response_to_delete = client.delete('/api/v1/delete_order_item/1/', headers={
            'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
            'Content-Type': 'application/json'
        })
        assert response_to_delete.status_code == 204

        response_to_confirm = client.patch('/api/v1/confirm/1/',
                                           data = {
                                                    "status": "confirm"
                                           },
                                           headers={
            'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
            'Content-Type': 'application/json'
        })

        order.refresh_from_db()
        assert response_to_confirm.status_code == 200
        assert order.status == 'confirmed'

@pytest.mark.django_db
def test_upload(client, user):
    response = client.post('/api/v1/upload/', data={
        'url': 'https://raw.githubusercontent.com/BroadName/retail_api/refs/heads/main/shop1.yaml',
    }, headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'
    })
    shop = Shop.objects.get(name='Связной')
    products = Product.objects.all().count()

    assert response.status_code == 200
    assert shop.name == 'Связной'
    assert products == 14


@pytest.mark.django_db
def test_get_products(client, user, products):
    response = client.get('/api/v1/products/', headers={
        'Authorization': f'Basic {encode_base64("test_user@mail.ru:secret")}',
        'Content-Type': 'application/json'
    })

    assert response.status_code == 200
    assert products.count() == Product.objects.all().count()
