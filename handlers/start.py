from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext

from keyboards import main_menu_keyboard, inline_start_keyboard, product_inline_keyboard
from config import (
    PRODUCT_NAME,
    PRICE_1_PCS,
    PRICE_2_PCS,
    PRICE_3_PCS,
    SUPPORT_PHONE,
    SUPPORT_USERNAME,
)
from database import get_user_orders

router = Router()

START_TEXT = f"""
✨ **স্বাগতম Magic Pen 3D Official Store-এ!** ✨

আমাদের উদ্ভাবনী **{PRODUCT_NAME}** দিয়ে আপনি লিখতে পারেন সম্পূর্ণ অদৃশ্য কালির গোপন বার্তা, ডায়েরি বা স্পেশাল নোট—যা কেবল কলমের পেছনে থাকা UV (আল্ট্রাভায়োলেট) আলোতে ভেসে উঠবে! 🪄🔦

🎁 **প্যাকেজ অফার সমূহ:**
• ১টি পেন: মাত্র **৳{PRICE_1_PCS}**
• ২টি পেন: মাত্র **৳{PRICE_2_PCS}** 🔥 *(জনপ্রিয়)*
• ৩টি পেন: মাত্র **৳{PRICE_3_PCS}** 🎁 *(সুপার সেভার)*

🚚 **ক্যাশ অন ডেলিভারি সুবিধা রয়েছে সারা বাংলাদেশে!**

অর্ডার করতে নিচের মেনু বাটন ব্যবহার করুন 👇
"""

PRODUCT_DETAILS_TEXT = f"""
🪄 **{PRODUCT_NAME} - প্রোডাক্ট স্পেসিফিকেশন:**

🔹 **কীভাবে কাজ করে?**
পেনটি দিয়ে যেকোনো সাধারণ কাগজে লিখুন—কালিটি সাথে সাথে অদৃশ্য হয়ে যাবে! খালি চোখে কিছুই দেখা যাবে না। এরপর পেনের পেছনের UV লাইটটি লেখার ওপর ধরলেই লেখাটি স্পষ্ট জ্বলজ্বল করে উঠবে!

🔹 **কেন ব্যবহার করবেন?**
✔️ সিক্রেট নোট, পাসওয়ার্ড বা পার্সোনাল ডায়েরি লিখতে।
✔️ প্রিয়জনকে স্পেশাল সারপ্রাইজ মেসেজ দিতে।
✔️ বাচ্চাদের ড্রয়িং ও ম্যাজিক গেমসের জন্য দারুণ উপহার।
✔️ প্রিমিয়াম বিল্ড কোয়ালিটি ও দীর্ঘস্থায়ী ব্যাটারি।

💰 **মূল্য তালিকা:**
1️⃣ ১টি পেন = **৳{PRICE_1_PCS}**
2️⃣ ২টি পেন = **৳{PRICE_2_PCS}** (প্রতি পিস ৳275)
3️⃣ ৩টি পেন = **৳{PRICE_3_PCS}** (প্রতি পিস ৳263)

অর্ডার করতে নিচের **'🛍️ অর্ডার করুন'** বাটনে চাপুন!
"""

SUPPORT_TEXT = f"""
📞 **কাস্টমার সাপোর্ট ও যোগাযোগ:**

আপনার যেকোনো জিজ্ঞাসা, প্রোডাক্ট সম্পর্কিত তথ্য বা অর্ডার সহায়তার জন্য আমাদের সাথে যোগাযোগ করতে পারেন:

📱 **মোবাইল:** `{SUPPORT_PHONE}`
💬 **টেলিগ্রাম সাপোর্ট:** {SUPPORT_USERNAME}
⏰ **সাপোর্ট টাইম:** সকাল ১০:০০ - রাত ১০:০০ (প্রতিদিন)

ধন্যবাদ আমাদের সাথে থাকার জন্য! ❤️
"""

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        START_TEXT,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await message.answer(
        "নিচের বাটনে ক্লিক করে সরাসরি অর্ডার শুরু করতে পারেন:",
        reply_markup=inline_start_keyboard()
    )

@router.message(Command("help"))
@router.message(F.text == "📞 হেল্প ও সাপোর্ট (Support)")
async def show_help(message: Message):
    await message.answer(SUPPORT_TEXT, parse_mode="Markdown")

@router.callback_query(F.data == "view_support")
async def cb_support(callback: CallbackQuery):
    await callback.message.answer(SUPPORT_TEXT, parse_mode="Markdown")
    await callback.answer()

@router.message(Command("product"))
@router.message(F.text == "✨ প্রোডাক্ট বিবরণ (Product Details)")
async def show_product(message: Message):
    await message.answer(
        PRODUCT_DETAILS_TEXT,
        reply_markup=product_inline_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "view_product")
async def cb_product(callback: CallbackQuery):
    await callback.message.answer(
        PRODUCT_DETAILS_TEXT,
        reply_markup=product_inline_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(Command("myorder"))
@router.message(F.text == "📦 আমার অর্ডার (My Orders)")
async def show_my_orders(message: Message):
    orders = await get_user_orders(message.from_user.id)
    if not orders:
        await message.answer(
            "আপনার কোনো পূর্বের অর্ডার পাওয়া যায়নি।\nঅর্ডার করতে '🛍️ অর্ডার করুন' বাটনে চাপুন!",
            reply_markup=main_menu_keyboard()
        )
        return

    text = "📦 **আপনার সাম্প্রতিক অর্ডারসমূহ:**\n\n"
    status_map = {
        "PENDING": "⏳ অপেক্ষমাণ (Pending)",
        "CONFIRMED": "✅ নিশ্চিত করা হয়েছে (Confirmed)",
        "SHIPPED": "🚚 ডেলিভারিতে আছে (Shipped)",
        "DELIVERED": "🎉 ডেলিভারি সম্পন্ন (Delivered)",
        "CANCELLED": "❌ বাতিল (Cancelled)",
    }
    for ord_data in orders:
        status_bn = status_map.get(ord_data['status'], ord_data['status'])
        text += (
            f"🔹 **অর্ডার কোড:** `{ord_data['order_code']}`\n"
            f"   পরিমাণ: {ord_data['quantity']} পিস\n"
            f"   মোট মূল্য: ৳{ord_data['total_price']}\n"
            f"   স্ট্যাটাস: {status_bn}\n"
            f"   তারিখ: {ord_data['created_at']}\n"
            f"──────────────────\n"
        )
    await message.answer(text, parse_mode="Markdown")

@router.message(StateFilter(None))
async def fallback_message(message: Message):
    """Fallback handler for any unrecognized text like 'hello' when NOT in active FSM order"""
    await message.answer(
        START_TEXT,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await message.answer(
        "নিচের বাটনে ক্লিক করে সরাসরি অর্ডার শুরু করতে পারেন:",
        reply_markup=inline_start_keyboard()
    )
