from app.schemas.order import OrderResponse, OrderRequest, OrderStatusRequest
from fastapi import APIRouter, HTTPException, Path, Query
from app.database import db_dependency
from starlette import status
from app.models import Vehicle, User, Order
from app.dependencies import user_dependency


router = APIRouter(
    prefix='/orders',
    tags=['Orders']
)

@router.get('/', status_code=status.HTTP_200_OK, response_model=list[OrderResponse])
def get_all_orders(
        db: db_dependency,
        user: user_dependency,
        destination: str = Query(None, description='Filter by order destination'),
        size: str = Query(None, description='Filter by order size'),
        order_status: str = Query(None, description='Filter by order status')
    ):
    """Retrieve a list of all orders, with optional filters (destination, size, status)."""
    query = db.query(Order)
    filters = {
        'destination': destination,
        'size': size,
        'status': order_status
    }

    for key, value in filters.items():
        if value is not None:
            query = query.filter(getattr(Order, key) == value)

    return query.all()


@router.get('/{order_id}', status_code=status.HTTP_200_OK, response_model=OrderResponse)
def get_order_by_id(db: db_dependency, user: user_dependency, order_id: int = Path(gt=0)):
    """Retrieve details of a specific order by its ID."""
    target_order = db.get(Order, order_id)

    if target_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified order could not be found.'
        )

    return target_order


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def add_order(db: db_dependency, user: user_dependency, order_request: OrderRequest):
    """Create a new order with the specified details."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action.'
        )

    assigned_vehicle = None
    if order_request.vehicle_id is not None:
        assigned_vehicle = db.query(Vehicle).filter(Vehicle.id == order_request.vehicle_id).first()
        if assigned_vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='The specified vehicle could not be found.'
            )

    new_order = Order(
        destination=order_request.destination,
        size=order_request.size,
        priority=order_request.priority,
        delivery_window_start=order_request.delivery_window_start,
        delivery_window_end=order_request.delivery_window_end,
        status=order_request.status,
        vehicle_id=order_request.vehicle_id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@router.put('/{order_id}/status', status_code=status.HTTP_200_OK, response_model=OrderResponse)
def update_order_status(
        db: db_dependency,
        user: user_dependency,
        status_request: OrderStatusRequest,
        order_id: int = Path(gt=0)
    ):
    """Update the status of an order by its ID (admin only)."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action.'
        )

    target_order = db.get(Order, order_id)
    if target_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified order could not be found.'
        )
    if target_order.status == status_request.order_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= f"Order status is already set to '{target_order.status}'."
        )

    target_order.status = status_request.order_status
    db.commit()
    db.refresh(target_order)

    return target_order


@router.delete('/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_order(db: db_dependency, user: user_dependency, order_id: int = Path(gt=0)):
    """Delete an order by its ID (admin only)."""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action.'
        )

    target_order = db.get(Order, order_id)
    if target_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified order could not be found.'
        )

    db.delete(target_order)
    db.commit()