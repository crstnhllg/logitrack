from app.schemas.vehicle import VehicleResponse, VehicleRequest, VehicleStatusRequest, VehicleDriverRequest
from fastapi import APIRouter, HTTPException, Path, Query
from app.database import db_dependency
from starlette import status
from app.models import Vehicle, User
from app.dependencies import user_dependency


router = APIRouter(
    prefix='/vehicles',
    tags=['Vehicles']
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=list[VehicleResponse])
def get_all_vehicles(
        db: db_dependency,
        user: user_dependency,
        driver_id: int = Query(None, description='Filter by driver ID'),
        vehicle_type: str = Query(None, description='Filter by vehicle type'),
        capacity_kg: int = Query(None, description='Filter by vehicle capacity in kg'),
        vehicle_status: str = Query(None, description='Filter by vehicle status'),
):
    """Retrieve a list of all vehicles, with optional filters (driver, type, capacity, status)."""
    query = db.query(Vehicle)
    filters = {
        'driver_id': driver_id,
        'type': vehicle_type,
        'capacity_kg': capacity_kg,
        'status': vehicle_status
    }

    for key, value in filters.items():
        if value is not None:
            query = query.filter(getattr(Vehicle, key) == value)

    return query.all()


@router.get('/{vehicle_id}', status_code=status.HTTP_200_OK, response_model=VehicleResponse)
def get_vehicle_by_id(db: db_dependency, user: user_dependency, vehicle_id: int = Path(gt=0)):
    """Retrieve details of a specific vehicle by its ID."""
    target_vehicle = db.get(Vehicle, vehicle_id)

    if target_vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified vehicle could not be found.'
        )

    return target_vehicle


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=VehicleResponse)
def add_vehicle(db: db_dependency, user: user_dependency, vehicle_request: VehicleRequest):
    """Create a new vehicle and assign it to a driver (admin only)."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action.'
        )

    assigned_driver = db.query(User).filter(User.id == vehicle_request.driver_id, User.role == 'driver').first()
    if assigned_driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified driver could not be found.'
        )

    if db.query(Vehicle).filter(Vehicle.license_plate == vehicle_request.license_plate).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='A vehicle with this license plate already exists.'
        )

    new_vehicle = Vehicle(
        license_plate=vehicle_request.license_plate,
        type=vehicle_request.vehicle_type,
        capacity_kg=vehicle_request.capacity_kg,
        status=vehicle_request.vehicle_status,
        driver_id=assigned_driver.id
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle


@router.put('/{vehicle_id}/status', status_code=status.HTTP_200_OK, response_model=VehicleResponse)
def update_vehicle_status(
        db: db_dependency,
        user: user_dependency,
        status_request: VehicleStatusRequest,
        vehicle_id: int = Path(gt=0)
    ):
    """Update the operational status of a vehicle by its ID (admin only)."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action.'
        )

    target_vehicle = db.get(Vehicle, vehicle_id)
    if target_vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified vehicle could not be found.'
        )
    if target_vehicle.status == status_request.vehicle_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= f"Vehicle status is already set to '{target_vehicle.status}'."
        )

    target_vehicle.status = status_request.vehicle_status
    db.commit()
    db.refresh(target_vehicle)

    return target_vehicle


@router.put('/{vehicle_id}/driver', status_code=status.HTTP_200_OK, response_model=VehicleResponse)
def change_vehicle_driver(
        db: db_dependency,
        user: user_dependency,
        driver_request:
        VehicleDriverRequest,
        vehicle_id: int = Path(gt=0)
    ):
    """Reassign a vehicle to a different driver (admin only)."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action.'
        )

    target_vehicle = db.get(Vehicle, vehicle_id)
    if target_vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified vehicle could not be found.'
        )
    if target_vehicle.driver_id == driver_request.driver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This vehicle is already assigned to the specified driver."
        )

    new_driver = db.query(User).filter(User.id == driver_request.driver_id, User.role == 'driver').first()
    if new_driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified driver could not be found.'
        )

    target_vehicle.driver_id = new_driver.id
    db.commit()
    db.refresh(target_vehicle)

    return target_vehicle


@router.delete('/{vehicle_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(db: db_dependency, user: user_dependency, vehicle_id: int = Path(gt=0)):
    """Delete a vehicle by its ID (admin only)."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action.'
        )

    target_vehicle = db.get(Vehicle, vehicle_id)
    if target_vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified vehicle could not be found.'
        )

    db.delete(target_vehicle)
    db.commit()