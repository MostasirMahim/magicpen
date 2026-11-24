import asyncio
from database import (
    init_db,
    create_order,
    get_order_by_code,
    update_order_status,
    get_stats,
    get_user_orders,
)

async def test():
    print("Testing Database and Order Flow...")
    await init_db()
    print("✓ Database initialized.")

    test_order_data = {
        "user_id": 987654321,
        "username": "testuser",
        "full_name": "Rahim Ahmed",
        "phone": "01712345678",
        "quantity": 2,
        "delivery_area": "ঢাকার ভেতরে",
        "address": "House 12, Road 4, Sector 7, Uttara, Dhaka",
        "payment_method": "Cash on Delivery",
        "trx_id": "N/A (COD)",
        "product_price": 550,
        "delivery_fee": 80,
        "total_price": 630,
    }

    order_code = await create_order(test_order_data)
    print(f"✓ Created test order: {order_code}")

    order = await get_order_by_code(order_code)
    assert order is not None
    assert order["full_name"] == "Rahim Ahmed"
    print(f"✓ Retrieved order {order_code} for {order['full_name']} (Total: ৳{order['total_price']})")

    await update_order_status(order_code, "CONFIRMED")
    order = await get_order_by_code(order_code)
    assert order["status"] == "CONFIRMED"
    print(f"✓ Status successfully updated to: {order['status']}")

    stats = await get_stats()
    print(f"✓ Stats: Total={stats['total_orders']}, Confirmed={stats['confirmed_orders']}, Revenue=৳{stats['total_revenue']}")
    print("\n🎉 ALL LOCAL LOGIC & DATABASE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test())
