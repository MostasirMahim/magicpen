import aiosqlite
try:
    import asyncpg
except ImportError:
    asyncpg = None

from config import DB_PATH, DATABASE_URL

_pg_pool = None

def is_postgres() -> bool:
    return bool(asyncpg and DATABASE_URL and (DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")))

async def get_pg_pool():
    global _pg_pool
    if _pg_pool is None:
        clean_dsn = DATABASE_URL.split("?")[0]
        if clean_dsn.startswith("postgres://"):
            clean_dsn = "postgresql://" + clean_dsn[len("postgres://"):]
        _pg_pool = await asyncpg.create_pool(
            dsn=clean_dsn,
            ssl="require",
            min_size=1,
            max_size=10
        )
    return _pg_pool

async def close_pg_pool():
    """Close the PostgreSQL connection pool"""
    global _pg_pool
    if _pg_pool is not None:
        await _pg_pool.close()
        _pg_pool = None

async def init_db():
    """Initialize database tables for either PostgreSQL or SQLite"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    order_code VARCHAR(50) UNIQUE,
                    user_id BIGINT,
                    username VARCHAR(100),
                    full_name VARCHAR(150),
                    phone VARCHAR(50),
                    quantity INT,
                    delivery_area VARCHAR(100),
                    address TEXT,
                    payment_method VARCHAR(100),
                    trx_id VARCHAR(100),
                    product_price INT,
                    delivery_fee INT,
                    total_price INT,
                    status VARCHAR(50) DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_code TEXT UNIQUE,
                    user_id INTEGER,
                    username TEXT,
                    full_name TEXT,
                    phone TEXT,
                    quantity INTEGER,
                    delivery_area TEXT,
                    address TEXT,
                    payment_method TEXT,
                    trx_id TEXT,
                    product_price INTEGER,
                    delivery_fee INTEGER,
                    total_price INTEGER,
                    status TEXT DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

async def create_order(data: dict) -> str:
    """Create a new order and return order code"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM orders")
            order_code = f"MP3D-{1001 + count}"
            await conn.execute("""
                INSERT INTO orders (
                    order_code, user_id, username, full_name, phone,
                    quantity, delivery_area, address, payment_method,
                    trx_id, product_price, delivery_fee, total_price, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 'PENDING')
            """,
                order_code,
                data.get("user_id"),
                data.get("username", ""),
                data.get("full_name"),
                data.get("phone"),
                data.get("quantity"),
                data.get("delivery_area"),
                data.get("address"),
                data.get("payment_method"),
                data.get("trx_id", ""),
                data.get("product_price"),
                data.get("delivery_fee"),
                data.get("total_price")
            )
            return order_code
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM orders")
            count = (await cursor.fetchone())[0]
            order_code = f"MP3D-{1001 + count}"
            
            await db.execute("""
                INSERT INTO orders (
                    order_code, user_id, username, full_name, phone,
                    quantity, delivery_area, address, payment_method,
                    trx_id, product_price, delivery_fee, total_price, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
            """, (
                order_code,
                data.get("user_id"),
                data.get("username", ""),
                data.get("full_name"),
                data.get("phone"),
                data.get("quantity"),
                data.get("delivery_area"),
                data.get("address"),
                data.get("payment_method"),
                data.get("trx_id", ""),
                data.get("product_price"),
                data.get("delivery_fee"),
                data.get("total_price")
            ))
            await db.commit()
            return order_code

async def get_order_by_code(order_code: str):
    """Fetch order details by order_code"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM orders WHERE order_code = $1", order_code)
            return dict(row) if row else None
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM orders WHERE order_code = ?", (order_code,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

async def update_order_status(order_code: str, status: str):
    """Update order status (e.g. CONFIRMED, CANCELLED)"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            await conn.execute("UPDATE orders SET status = $1 WHERE order_code = $2", status, order_code)
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE orders SET status = ? WHERE order_code = ?", (status, order_code))
            await db.commit()

async def get_user_orders(user_id: int, limit: int = 5):
    """Get orders made by a specific user"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM orders WHERE user_id = $1 ORDER BY id DESC LIMIT $2", user_id, limit)
            return [dict(r) for r in rows]
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

async def get_recent_orders(limit: int = 10):
    """Get recent orders for admin"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM orders ORDER BY id DESC LIMIT $1", limit)
            return [dict(r) for r in rows]
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM orders ORDER BY id DESC LIMIT ?",
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

async def get_all_orders():
    """Get all orders for export"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM orders ORDER BY id DESC")
            return [dict(r) for r in rows]
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM orders ORDER BY id DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

async def get_orders_by_status(status: str, limit: int = 10):
    """Get orders filtered by status"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM orders WHERE status = $1 ORDER BY id DESC LIMIT $2", status, limit)
            return [dict(r) for r in rows]
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM orders WHERE status = ? ORDER BY id DESC LIMIT ?",
                (status, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]

async def get_stats():
    """Get dashboard stats for admin"""
    if is_postgres():
        pool = await get_pg_pool()
        async with pool.acquire() as conn:
            total_orders = await conn.fetchval("SELECT COUNT(*) FROM orders")
            pending_orders = await conn.fetchval("SELECT COUNT(*) FROM orders WHERE status = 'PENDING'")
            confirmed_orders = await conn.fetchval("SELECT COUNT(*) FROM orders WHERE status = 'CONFIRMED'")
            total_revenue = await conn.fetchval("SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status = 'CONFIRMED'")
            return {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "confirmed_orders": confirmed_orders,
                "total_revenue": total_revenue
            }
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM orders") as c:
                total_orders = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM orders WHERE status = 'PENDING'") as c:
                pending_orders = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM orders WHERE status = 'CONFIRMED'") as c:
                confirmed_orders = (await c.fetchone())[0]
            async with db.execute("SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status = 'CONFIRMED'") as c:
                total_revenue = (await c.fetchone())[0]
                
            return {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "confirmed_orders": confirmed_orders,
                "total_revenue": total_revenue
            }
