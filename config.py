import os
from dotenv import load_dotenv

# Fix Python 3.12.0 typing.Union hash compatibility with Pydantic FailFast
try:
    from pydantic import FailFast
    if not hasattr(FailFast, "__hash__") or FailFast.__hash__ is None:
        FailFast.__hash__ = lambda self: hash(getattr(self, "fail_fast", True))
except Exception:
    pass

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0").strip())
except ValueError:
    ADMIN_ID = 0

PRODUCT_NAME = os.getenv("PRODUCT_NAME", "Magic Pen 3D (UV Invisible Ink)")
PRICE_1_PCS = int(os.getenv("PRICE_1_PCS", "290"))
PRICE_2_PCS = int(os.getenv("PRICE_2_PCS", "550"))
PRICE_3_PCS = int(os.getenv("PRICE_3_PCS", "790"))

DELIVERY_INSIDE_DHAKA = int(os.getenv("DELIVERY_INSIDE_DHAKA", "80"))
DELIVERY_OUTSIDE_DHAKA = int(os.getenv("DELIVERY_OUTSIDE_DHAKA", "140"))

BKASH_NUMBER = os.getenv("BKASH_NUMBER", "017XXXXXXXX")
NAGAD_NUMBER = os.getenv("NAGAD_NUMBER", "018XXXXXXXX")

SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "017XXXXXXXX")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@MagicPen3DSupport")

DB_PATH = "magicpen.db"

def get_product_price(quantity: int) -> int:
    """Calculate price based on quantity tier"""
    if quantity == 1:
        return PRICE_1_PCS
    elif quantity == 2:
        return PRICE_2_PCS
    elif quantity == 3:
        return PRICE_3_PCS
    else:
        # For >3, rate based on 3-pcs average
        return quantity * 260
