from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import OrderStatus
from app.models.invoice import Invoice
from app.models.order import Order
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    MonthlyExpenseStat,
)


async def get_invoice_by_id(
    db: AsyncSession, invoice_id: int
) -> Optional[Invoice]:
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    return result.scalars().first()


async def get_invoices(
    db: AsyncSession,
    owner_id: Optional[int] = None,
) -> Sequence[Invoice]:
    query = select(Invoice)
    if owner_id is not None:
        query = query.where(Invoice.owner_id == owner_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_invoice(
    db: AsyncSession, invoice_in: InvoiceCreate
) -> Invoice:
    db_invoice = Invoice(**invoice_in.model_dump())
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice


async def update_invoice(
    db: AsyncSession, invoice: Invoice, invoice_in: InvoiceUpdate
) -> Invoice:
    update_data = invoice_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def delete_invoice(db: AsyncSession, invoice: Invoice) -> None:
    await db.delete(invoice)
    await db.commit()


async def get_invoice_by_month(
    db: AsyncSession, owner_id: int, billing_month: datetime
) -> Optional[Invoice]:
    month_start = billing_month.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    query = select(Invoice).where(
        Invoice.owner_id == owner_id, Invoice.billing_month == month_start
    )
    result = await db.execute(query)
    return result.scalars().first()


async def get_monthly_statistics(
    db: AsyncSession,
    owner_id: Optional[int] = None,
    month: Optional[str] = None,
) -> Sequence[MonthlyExpenseStat]:
    if month:
        try:
            target_date = datetime.strptime(month, "%Y-%m")
            next_month = (
                target_date.month % 12 + 1,
                target_date.year + (target_date.month // 12),
            )
            end_date = datetime(next_month[1], next_month[0], 1)

            day_col = func.date_trunc("day", Order.received_at).label("day")
            query = (
                select(
                    day_col,
                    func.count(Order.id).label("total_shipments"),
                    func.sum(Order.weight).label("total_weight"),
                    func.sum(Order.total_amount).label("total_amount"),
                )
                .where(
                    Order.status == OrderStatus.COMPLETED,
                    Order.received_at >= target_date,
                    Order.received_at < end_date,
                )
                .group_by("day")
                .order_by("day")
            )

            if owner_id is not None:
                query = query.where(Order.owner_id == owner_id)

            result = await db.execute(query)
            return [
                MonthlyExpenseStat(
                    month=row.day,
                    total_shipments=row.total_shipments or 0,
                    total_weight=float(row.total_weight or 0),
                    total_volume=0.0,
                    total_distance=0.0,
                    total_amount=float(row.total_amount or 0),
                    invoice_count=0,
                )
                for row in result.all()
            ]
        except ValueError:
            pass

    month_col = func.date_trunc("month", Invoice.billing_month).label("month")
    query = (
        select(
            month_col,
            func.sum(Invoice.total_shipment).label("total_shipments"),
            func.sum(Invoice.total_weight).label("total_weight"),
            func.sum(Invoice.total_volume).label("total_volume"),
            func.sum(Invoice.total_distance).label("total_distance"),
            func.sum(Invoice.total_amount).label("total_amount"),
            func.count(Invoice.id).label("invoice_count"),
        )
        .group_by("month")
        .order_by(month_col.desc())
    )

    if owner_id is not None:
        query = query.where(Invoice.owner_id == owner_id)

    result = await db.execute(query)
    return [
        MonthlyExpenseStat(
            month=row.month,
            total_shipments=row.total_shipments or 0,
            total_weight=float(row.total_weight or 0),
            total_volume=float(row.total_volume or 0),
            total_distance=float(row.total_distance or 0),
            total_amount=float(row.total_amount or 0),
            invoice_count=row.invoice_count,
        )
        for row in result.all()
    ]
