from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import invoice as crud_invoice
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


class InvoiceService:
    async def get_invoice_or_404(self, db: AsyncSession, invoice_id: int):
        invoice = await crud_invoice.get_invoice_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice

    async def get_invoices(self, db: AsyncSession, **filters):
        return await crud_invoice.get_invoices(db, **filters)

    async def create_invoice(
        self, db: AsyncSession, invoice_in: InvoiceCreate
    ):
        return await crud_invoice.create_invoice(db, invoice_in)

    async def update_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        invoice_in: InvoiceUpdate,
    ):
        invoice = await self.get_invoice_or_404(db, invoice_id)
        return await crud_invoice.update_invoice(db, invoice, invoice_in)

    async def delete_invoice(self, db: AsyncSession, invoice_id: int):
        invoice = await self.get_invoice_or_404(db, invoice_id)
        await crud_invoice.delete_invoice(db, invoice)

    async def get_monthly_statistics(
        self,
        db: AsyncSession,
        owner_id: Optional[int] = None,
        month: Optional[str] = None,
    ):
        return await crud_invoice.get_monthly_statistics(db, owner_id, month)

    async def add_order_to_invoice(self, db: AsyncSession, order):
        billing_month = order.received_at or order.created_at
        if not billing_month:
            billing_month = datetime.now(timezone.utc)

        invoice = await crud_invoice.get_invoice_by_month(
            db, order.owner_id, billing_month
        )

        if not invoice:
            month_start = billing_month.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            invoice_in = InvoiceCreate(
                owner_id=order.owner_id,
                billing_month=month_start,
                total_shipment=1,
                total_weight=order.weight,
                total_amount=order.total_amount,
            )
            await crud_invoice.create_invoice(db, invoice_in)
        else:
            invoice_update = InvoiceUpdate(
                total_shipment=invoice.total_shipment + 1,
                total_weight=float(invoice.total_weight or 0)
                + float(order.weight or 0),
                total_amount=float(invoice.total_amount or 0)
                + float(order.total_amount or 0),
            )
            await crud_invoice.update_invoice(db, invoice, invoice_update)


invoice_service = InvoiceService()
