import asyncio
import csv
from database import init_db, get_stats, get_recent_orders, get_all_orders, is_postgres, close_pg_pool
from config import DATABASE_URL, DB_PATH

async def show_orders():
    try:
        await init_db()
        db_type = "Neon PostgreSQL (Cloud)" if is_postgres() else f"Local SQLite ({DB_PATH})"
        
        stats = await get_stats()
        recent = await get_recent_orders(20)

        print("=" * 70)
        print("🪄  MAGIC PEN 3D - ORDERS OVERVIEW  🪄")
        print(f"Database: {db_type}")
        print("=" * 70)
        print(f"Total Orders:     {stats['total_orders']}")
        print(f"Pending Orders:   {stats['pending_orders']}")
        print(f"Confirmed Orders: {stats['confirmed_orders']}")
        print(f"Confirmed Sales:  ৳{stats['total_revenue']}")
        print("-" * 70)

        if not recent:
            print("No orders recorded in database yet.")
        else:
            print(f"{'Code':<10} | {'Customer':<16} | {'Phone':<12} | {'Qty':<4} | {'Total':<6} | {'Status':<10}")
            print("-" * 70)
            for r in recent:
                code = r.get('order_code', '')
                name = (r.get('full_name') or '')[:15]
                phone = r.get('phone', '')
                qty = r.get('quantity', 0)
                total = r.get('total_price', 0)
                status = r.get('status', '')
                print(f"{code:<10} | {name:<16} | {phone:<12} | {qty:<4} | ৳{total:<5} | {status:<10}")

        print("=" * 70)

        all_orders = await get_all_orders()
        if all_orders:
            csv_file = "orders_export.csv"
            with open(csv_file, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Order ID", "Date", "Status", "Customer Name", "Phone",
                    "Quantity", "Product Price", "Delivery Fee", "Total Price",
                    "Delivery Area", "Full Address", "Payment Method", "TrxID", "Username", "UserID"
                ])
                for o in all_orders:
                    writer.writerow([
                        o.get("order_code", ""),
                        o.get("created_at", ""),
                        o.get("status", ""),
                        o.get("full_name", ""),
                        o.get("phone", ""),
                        o.get("quantity", ""),
                        o.get("product_price", ""),
                        o.get("delivery_fee", ""),
                        o.get("total_price", ""),
                        o.get("delivery_area", ""),
                        o.get("address", ""),
                        o.get("payment_method", ""),
                        o.get("trx_id", ""),
                        o.get("username", ""),
                        o.get("user_id", "")
                    ])
            print(f"✓ All orders exported to '{csv_file}' (open in Microsoft Excel)")
            print("=" * 70)
    finally:
        await close_pg_pool()

if __name__ == "__main__":
    asyncio.run(show_orders())
