from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from config import (
    PRICE_1_PCS,
    PRICE_2_PCS,
    PRICE_3_PCS,
    DELIVERY_INSIDE_DHAKA,
    DELIVERY_OUTSIDE_DHAKA,
)

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main persistent reply keyboard menu"""
    kb = [
        [
            KeyboardButton(text="🛍️ অর্ডার করুন (Order Now)"),
            KeyboardButton(text="✨ প্রোডাক্ট বিবরণ (Product Details)"),
        ],
        [
            KeyboardButton(text="📦 আমার অর্ডার (My Orders)"),
            KeyboardButton(text="📞 হেল্প ও সাপোর্ট (Support)"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)

def product_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline buttons under product description"""
    kb = [
        [InlineKeyboardButton(text="🛍️ এখনই অর্ডার করুন (Order Now)", callback_data="start_order")],
        [InlineKeyboardButton(text="📞 কাস্টমার সাপোর্ট", callback_data="view_support")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def inline_start_keyboard() -> InlineKeyboardMarkup:
    """Inline buttons under welcome message"""
    kb = [
        [
            InlineKeyboardButton(text="🛍️ এখনই অর্ডার করুন", callback_data="start_order"),
            InlineKeyboardButton(text="✨ প্রোডাক্ট ফিচার", callback_data="view_product"),
        ],
        [
            InlineKeyboardButton(text="📞 কাস্টমার সাপোর্ট", callback_data="view_support"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def quantity_keyboard() -> ReplyKeyboardMarkup:
    """Quantity selection buttons"""
    kb = [
        [KeyboardButton(text=f"1️⃣ ১টি পেন — ৳{PRICE_1_PCS}")],
        [KeyboardButton(text=f"2️⃣ ২টি পেন — ৳{PRICE_2_PCS} (জনপ্রিয় 🔥)")],
        [KeyboardButton(text=f"3️⃣ ৩টি পেন — ৳{PRICE_3_PCS} (সুপার অফার 🎁)")],
        [KeyboardButton(text="❌ বাতিল করুন")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def delivery_area_keyboard() -> ReplyKeyboardMarkup:
    """Delivery zone selection buttons"""
    kb = [
        [KeyboardButton(text=f"🏙️ ঢাকার ভেতরে (৳{DELIVERY_INSIDE_DHAKA})")],
        [KeyboardButton(text=f"🚚 ঢাকার বাইরে (৳{DELIVERY_OUTSIDE_DHAKA})")],
        [KeyboardButton(text="❌ বাতিল করুন")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def payment_method_keyboard() -> ReplyKeyboardMarkup:
    """Payment methods selection"""
    kb = [
        [KeyboardButton(text="💵 Cash on Delivery (ক্যাশ অন ডেলিভারি)")],
        [KeyboardButton(text="📱 bKash / Nagad (বিকাশ বা নগদ)")],
        [KeyboardButton(text="❌ বাতিল করুন")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def order_confirm_keyboard() -> ReplyKeyboardMarkup:
    """Confirmation keyboard before submitting"""
    kb = [
        [KeyboardButton(text="✅ হ্যাঁ, অর্ডার নিশ্চিত করুন")],
        [KeyboardButton(text="❌ অর্ডার বাতিল করুন")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Single cancel button"""
    kb = [[KeyboardButton(text="❌ বাতিল করুন")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def admin_order_keyboard(order_code: str) -> InlineKeyboardMarkup:
    """Admin action buttons on new order notification"""
    kb = [
        [
            InlineKeyboardButton(
                text="✅ কনফার্ম করুন",
                callback_data=f"adm_confirm:{order_code}"
            ),
            InlineKeyboardButton(
                text="❌ বাতিল করুন",
                callback_data=f"adm_cancel:{order_code}"
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
