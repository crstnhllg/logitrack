from app.models import User, Vehicle
from app.core.security import bcrypt_context
from tests.conftest import (
    client,
    test_vehicle,
    db_session
)


def test_get_all_vehicles(test_vehicle):
    response = client.get('/vehicles/')
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0].get('id') == test_vehicle.id


def test_get_vehicle_by_id(test_vehicle):
    response = client.get(f'/vehicles/{test_vehicle.id}')

    assert response.status_code == 200
    assert response.json().get('id') == test_vehicle.id


def test_get_vehicle_by_id_not_found():
    response = client.get('/vehicles/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'The specified vehicle could not be found.'}


def test_add_vehicle(test_vehicle):
    data_request = {
        'license_plate': 'abc111',
        'vehicle_type': 'truck',
        'capacity_kg': 1500,
        'vehicle_status': 'maintenance',
        'driver_id': test_vehicle.driver_id
    }

    response = client.post('/vehicles/', json=data_request)
    data = response.json()

    assert response.status_code == 201
    assert data.get('license_plate') == data_request.get('license_plate')
    assert data.get('driver_id') == test_vehicle.driver_id


def test_add_vehicle_duplicate(test_vehicle):
    data_request = {
        'license_plate': test_vehicle.license_plate,
        'vehicle_type': 'truck',
        'capacity_kg': 1500,
        'vehicle_status': 'maintenance',
        'driver_id': test_vehicle.driver_id
    }
    response = client.post('/vehicles/', json=data_request)

    assert response.status_code == 400
    assert response.json() == {'detail': 'A vehicle with this license plate already exists.'}


def test_update_vehicle_status(test_vehicle):
    data_request = {
        'vehicle_status': 'inactive',
    }
    response = client.put(f'/vehicles/{test_vehicle.id}/status', json=data_request)
    data = response.json()

    assert response.status_code == 200
    assert data.get('id') == test_vehicle.id
    assert data.get('status') == data_request.get('vehicle_status')


def test_update_vehicle_status_duplicate(test_vehicle):
    data_request = {
        'vehicle_status': test_vehicle.status,
    }
    response = client.put(f'/vehicles/{test_vehicle.id}/status', json=data_request)

    assert response.status_code == 400
    assert response.json() == {'detail': f"Vehicle status is already set to '{test_vehicle.status}'."}


def test_change_vehicle_driver(db_session, test_vehicle):
    new_driver = User(
        username='driver_12345',
        email='driver_12345@email.com',
        role='driver',
        hashed_password=bcrypt_context.hash('12345')
    )
    db_session.add(new_driver)
    db_session.commit()

    data_request = {
        'driver_id': new_driver.id,
    }
    response = client.put(f'/vehicles/{test_vehicle.id}/driver', json=data_request)
    data = response.json()

    assert response.status_code == 200
    assert data.get('id') == test_vehicle.id
    assert data.get('driver_id') == new_driver.id


def test_change_vehicle_driver_not_found(test_vehicle):
    data_request = {
        'driver_id': 999,
    }
    response = client.put(f'/vehicles/{test_vehicle.id}/driver', json=data_request)

    assert response.status_code == 404
    assert response.json() == {'detail': 'The specified driver could not be found.'}


def test_delete_vehicle(db_session, test_vehicle):
    response = client.delete(f'/vehicles/{test_vehicle.id}')
    assert response.status_code == 204

    deleted_vehicle = db_session.query(Vehicle).filter(Vehicle.id == test_vehicle.id).first()
    assert deleted_vehicle is None


def test_delete_vehicle_unauthorized(db_session, test_vehicle, test_user):
    test_user.role = 'driver'
    db_session.commit()

    response = client.delete(f'/vehicles/{test_vehicle.id}')
    assert response.status_code == 403
    assert response.json() == {'detail': 'You are not authorized to perform this action.'}


def test_vehicle_response_serialization(test_vehicle):
    response = client.get('/vehicles/')
    data = response.json()
    expected_keys = {'id', 'updated_at', 'license_plate', 'type', 'capacity_kg', 'status', 'driver_id'}

    assert set(data[0].keys()) == expected_keys