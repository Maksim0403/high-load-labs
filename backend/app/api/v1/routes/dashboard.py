from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_roles
from app.enums import OrderStatus, UserRole
from app.schemas.delivery_photo import DeliveryPhotoOut, DeliveryPhotoUploadOut
from app.schemas.invoice import InvoiceCreate, InvoiceOut, MonthlyExpenseStat
from app.schemas.notification import NotificationOut
from app.schemas.order import OrderAssign, OrderCreate, OrderOut, OrderUpdate
from app.schemas.route import RouteCreate, RouteOut, RouteUpdate
from app.schemas.route_status import RouteStatusCreate, RouteStatusOut
from app.schemas.shipment import ShipmentCreate, ShipmentOut
from app.schemas.user import UserOut
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate
from app.services.delivery_photo_service import delivery_photo_service
from app.services.invoice_service import invoice_service
from app.services.notification_service import notification_service
from app.services.order_service import order_service
from app.services.route_service import route_service
from app.services.route_status_service import route_status_service
from app.services.shipment_service import shipment_service
from app.services.user_service import user_service
from app.services.vehicle_service import vehicle_service

router = APIRouter()


@router.get("/orders", response_model=list[OrderOut])
async def get_orders(
    status: Optional[OrderStatus] = None,
    is_template: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.CLIENT, UserRole.MANAGER)),
):
    owner_id = (
        current_user.id if current_user.role == UserRole.CLIENT else None
    )
    return await order_service.get_orders(
        db,
        owner_id=owner_id,
        status=status,
        is_template=is_template,
    )


@router.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.CLIENT, UserRole.MANAGER)),
):
    order = await order_service.get_order_or_404(db, order_id)
    if (
        current_user.role == UserRole.CLIENT
        and order.owner_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    return order


@router.post("/orders", response_model=OrderOut, status_code=201)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.CLIENT, UserRole.MANAGER)),
):
    return await order_service.create_order(
        db, order_in, owner_id=current_user.id
    )


@router.patch("/orders/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.CLIENT, UserRole.MANAGER)),
):
    return await order_service.update_order(
        db, order_id, order_in, current_user=current_user
    )


@router.delete("/orders/{order_id}", status_code=204)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.CLIENT, UserRole.MANAGER)),
):
    await order_service.delete_order(db, order_id, current_user=current_user)


@router.post(
    "/orders/from-template/{order_id}",
    response_model=OrderOut,
    status_code=201,
)
async def create_order_from_template(
    order_id: int,
    scheduled_date: datetime,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER)),
):
    template = await order_service.get_order_or_404(db, order_id)
    if (
        current_user.role == UserRole.CLIENT
        and template.owner_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    if not template.is_template:
        raise HTTPException(status_code=422, detail="Order is not a template")
    order_in = OrderCreate(
        title=template.title,
        description=template.description,
        weight=template.weight,
        is_template=False,
    )
    return await order_service.create_order(
        db, order_in, owner_id=current_user.id
    )


@router.post("/orders/{order_id}/assign", response_model=RouteOut)
async def assign_order_to_driver(
    order_id: int,
    assign_in: OrderAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER)),
):
    await order_service.get_order_or_404(db, order_id)
    return await route_service.assign_order_to_driver(
        db,
        order_id=order_id,
        driver_id=assign_in.driver_id,
        vehicle_id=assign_in.vehicle_id,
        eta=assign_in.eta,
    )


@router.post("/routes", response_model=RouteOut, status_code=201)
async def create_route(
    route_in: RouteCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.CLIENT, UserRole.MANAGER)),
):
    return await route_service.create_route(db, route_in)


@router.patch("/routes/{route_id}", response_model=RouteOut)
async def update_route(
    route_id: int,
    route_in: RouteUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.CLIENT, UserRole.MANAGER)),
):
    return await route_service.update_route(db, route_id, route_in)


@router.get("/orders/{order_id}/shipments", response_model=list[ShipmentOut])
async def get_shipments(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    order = await order_service.get_order_or_404(db, order_id)
    if (
        current_user.role == UserRole.CLIENT
        and order.owner_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    return await shipment_service.get_shipments_by_order(db, order_id)


@router.post(
    "/orders/{order_id}/shipments", response_model=ShipmentOut, status_code=201
)
async def add_shipment_to_order(
    order_id: int,
    shipment_in: ShipmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER)),
):
    await order_service.get_order_or_404(db, order_id)
    return await shipment_service.create_shipment(db, order_id, shipment_in)


@router.get("/routes", response_model=list[RouteOut])
async def get_routes(
    order_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    driver_id = (
        current_user.id if current_user.role == UserRole.DRIVER else None
    )
    return await route_service.get_routes(
        db, order_id=order_id, driver_id=driver_id
    )


@router.get("/routes/today", response_model=list[RouteOut])
async def get_today_routes(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER)),
):
    return await route_service.get_today_routes(db, driver_id=current_user.id)


@router.get("/routes/{route_id}", response_model=RouteOut)
async def get_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    route = await route_service.get_route_or_404(db, route_id)
    if (
        current_user.role == UserRole.DRIVER
        and route.driver_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not your route")
    return route


@router.get("/routes/{route_id}/statuses", response_model=list[RouteStatusOut])
async def get_route_statuses(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    await route_service.get_route_or_404(db, route_id)
    return await route_status_service.get_statuses(db, route_id)


@router.get("/routes/{route_id}/status")
async def get_route_current_status(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    await route_service.get_route_or_404(db, route_id)
    statuses = await route_status_service.get_statuses(db, route_id)
    if not statuses:
        return {"status": None}
    return {"status": statuses[-1].status}


@router.get("/routes/{route_id}/eta")
async def get_route_eta(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    route = await route_service.get_route_or_404(db, route_id)
    return {"eta": route.eta}


@router.get("/routes/{route_id}/photos", response_model=list[DeliveryPhotoOut])
async def get_route_photos(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    await route_service.get_route_or_404(db, route_id)
    return await delivery_photo_service.get_route_photos(db, route_id)


@router.get("/notifications", response_model=list[NotificationOut])
async def get_notifications(
    is_read: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    return await notification_service.get_notifications(
        db, user_id=current_user.id, is_read=is_read
    )


@router.patch("/notifications/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    updated = await notification_service.mark_all_as_read(
        db, user_id=current_user.id
    )
    return {"updated": updated}


@router.patch(
    "/notifications/{notification_id}", response_model=NotificationOut
)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(
        require_roles(UserRole.CLIENT, UserRole.DRIVER, UserRole.MANAGER)
    ),
):
    return await notification_service.mark_as_read(
        db, notification_id, user_id=current_user.id
    )


@router.get("/invoices", response_model=list[InvoiceOut])
async def get_invoices(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.CLIENT)),
):
    owner_id = (
        current_user.id if current_user.role == UserRole.CLIENT else None
    )
    return await invoice_service.get_invoices(
        db,
        owner_id=owner_id,
    )


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.CLIENT)),
):
    invoice = await invoice_service.get_invoice_or_404(db, invoice_id)
    if (
        current_user.role == UserRole.CLIENT
        and invoice.owner_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    return invoice


@router.get("/statistics/monthly", response_model=list[MonthlyExpenseStat])
async def get_monthly_statistics(
    month: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER, UserRole.CLIENT)),
):
    owner_id = (
        current_user.id if current_user.role == UserRole.CLIENT else None
    )
    return await invoice_service.get_monthly_statistics(
        db, owner_id=owner_id, month=month
    )


@router.post("/invoices", response_model=InvoiceOut, status_code=201)
async def create_invoice(
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.MANAGER)),
):
    invoices = await invoice_service.get_invoices(
        db, owner_id=invoice_in.owner_id
    )
    for inv in invoices:
        if inv.billing_month == invoice_in.billing_month:
            raise HTTPException(
                status_code=409,
                detail="Invoice already exists for this period",
            )

    return await invoice_service.create_invoice(db, invoice_in)


@router.post(
    "/routes/{route_id}/statuses",
    response_model=RouteStatusOut,
    status_code=201,
)
async def add_route_status(
    route_id: int,
    status_in: RouteStatusCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER)),
):
    route = await route_service.get_route_or_404(db, route_id)
    if route.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your route")
    return await route_status_service.add_status(db, route_id, status_in)


@router.post(
    "/routes/{route_id}/photos",
    response_model=DeliveryPhotoUploadOut,
    status_code=201,
)
async def upload_route_photo(
    route_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER)),
):
    route = await route_service.get_route_or_404(db, route_id)
    if route.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your route")
    return await delivery_photo_service.upload_photo(
        db, route_id, file, description, current_user
    )


@router.delete("/routes/photos/{photo_id}", status_code=204)
async def delete_route_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER, UserRole.MANAGER)),
):
    await delivery_photo_service.delete_photo(db, photo_id, current_user)


@router.get("/vehicles", response_model=list[VehicleOut])
async def get_my_vehicles(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER)),
):
    return await vehicle_service.get_driver_vehicles(db, current_user.id)


@router.post("/vehicles", response_model=VehicleOut, status_code=201)
async def add_vehicle(
    vehicle_in: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER)),
):
    return await vehicle_service.add_vehicle(db, vehicle_in, current_user)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleOut)
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER)),
):
    vehicle = await vehicle_service.get_vehicle_or_404(db, vehicle_id)
    if vehicle.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your vehicle")
    return vehicle


@router.patch("/vehicles/{vehicle_id}", response_model=VehicleOut)
async def update_vehicle(
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER)),
):
    return await vehicle_service.update_vehicle(
        db, vehicle_id, vehicle_in, current_user
    )


@router.delete("/vehicles/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.DRIVER)),
):
    await vehicle_service.remove_vehicle(db, vehicle_id, current_user)


@router.get("/drivers", response_model=list[UserOut])
async def get_drivers(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.MANAGER, UserRole.CLIENT)),
):
    return await user_service.get_users_by_role(db, role=UserRole.DRIVER)
