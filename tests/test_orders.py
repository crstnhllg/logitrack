from app.models import User, Vehicle, Order
from tests.conftest import (
    client,
    test_vehicle,
    test_order,
    db_session
)


def test_get_all_orders(test_order):
    response = client.get('/orders/')
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0].get('id') == test_order.id


def test_get_order_by_id(test_order):
    response = client.get(f'/orders/{test_order.id}')

    assert response.status_code == 200
    assert response.json().get('id') == test_order.id


def test_get_order_by_id_not_found():
    response = client.get('/orders/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'The specified order could not be found.'}


def test_add_order(test_vehicle):
    data_request = {
      "destination": "Manila",
      "size": "xs",
      "priority": False,
      "delivery_window_start": "2025-09-2 10:00",
      "delivery_window_end": "2025-09-03 10:00",
      "status": "in_transit",
      "vehicle_id": test_vehicle.id
    }

    response = client.post('/orders/', json=data_request)
    data = response.json()

    assert response.status_code == 201
    assert data.get('destination') == data_request.get('destination')
    assert data.get('vehicle_id') == test_vehicle.id


def test_update_order_status(test_order):
    data_request = {
        'order_status': 'completed',
    }
    response = client.put(f'/orders/{test_order.id}/status', json=data_request)
    data = response.json()

    assert response.status_code == 200
    assert data.get('id') == test_order.id
    assert data.get('status') == data_request.get('order_status')


def test_update_order_status_duplicate(test_order):
    data_request = {
        'order_status': test_order.status,
    }
    response = client.put(f'/orders/{test_order.id}/status', json=data_request)

    assert response.status_code == 400
    assert response.json() == {'detail': f"Order status is already set to '{test_order.status}'."}


def test_delete_order(db_session, test_order):
    response = client.delete(f'/orders/{test_order.id}')
    assert response.status_code == 204

    deleted_order = db_session.query(Order).filter(Order.id == test_order.id).first()
    assert deleted_order is None


def test_delete_order_unauthorized(db_session, test_order, test_user):
    test_user.role = 'driver'
    db_session.commit()

    response = client.delete(f'/orders/{test_order.id}')
    assert response.status_code == 403
    assert response.json() == {'detail': 'You are not authorized to perform this action.'}


def test_order_response_serialization(test_order):
    response = client.get('/orders/')
    data = response.json()
    expected_keys = {
    'id',
    'updated_at',
    'destination',
    'size',
    'priority',
    'delivery_window_start',
    'delivery_window_end',
    'status',
    'vehicle_id',
    }

    assert set(data[0].keys()) == expected_keys