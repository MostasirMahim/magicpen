import re
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import (
    main_menu_keyboard,
    quantity_keyboard,
    delivery_area_keyboard,
    payment_method_keyboard,
    order_confirm_keyboard,
    cancel_keyboard,
    admin_order_keyboard,
)
from config import (
    ADMIN_ID,
    PRODUCT_NAME,
    PRICE_1_PCS,
    PRICE_2_PCS,
    PRICE_3_PCS,
    DELIVERY_INSIDE_DHAKA,
    DELIVERY_OUTSIDE_DHAKA,
    BKASH_NUMBER,
    NAGAD_NUMBER,
    get_product_price,
)
from database import create_order

router = Router()

class OrderFSM(StatesGroup):
    choosing_quantity = State()
    entering_name = State()
    entering_phone = State()
    choosing_area = State()
    entering_address = State()
    choosing_payment = State()
    entering_trx_id = State()
    confirming_order = State()

def normalize_digits(text: str) -> str:
    """Convert Bengali numerals to English numerals"""
    bn_to_en = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
    return text.translate(bn_to_en)

@router.message(F.text.in_(["❌ বাতিল করুন", "❌ অর্ডার বাতিল করুন"]))
async def cancel_order(message: Message, state: FSMContext):
    """Cancel order at any stage"""
    await state.clear()
    await message.answer(
        "❌ অর্ডার প্রক্রিয়া বাতিল করা হয়েছে।\nপ্রয়োজনে আবার নতুন অর্ডার শুরু করতে পারেন।",
        reply_markup=main_menu_keyboard()
    )

@router.message(Command("order"))
@router.message(F.text == "🛍️ অর্ডার করুন (Order Now)")
@router.callback_query(F.data == "start_order")
async def start_order_process(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        f"🛍️ **{PRODUCT_NAME} অর্ডার ফরম**\n\n"
        f"অনুগ্রহ করে আপনি কত পিস পেন নিতে চান তা সিলেক্ট করুন:"
    )
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=quantity_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=quantity_keyboard(), parse_mode="Markdown")
    await state.set_state(OrderFSM.choosing_quantity)

@router.message(OrderFSM.choosing_quantity)
async def process_quantity(message: Message, state: FSMContext):
    text = message.text
    qty = 0
    if "1️⃣" in text or "১" in text or "1" in text:
        qty = 1
    elif "2️⃣" in text or "২" in text or "2" in text:
        qty = 2
    elif "3️⃣" in text or "৩" in text or "3" in text:
        qty = 3
    else:
        try:
            qty = int(normalize_digits(text.strip()))
        except ValueError:
            qty = 0

    if qty <= 0:
        await message.answer(
            "অনুগ্রহ করে নিচের বাটন থেকে সঠিক পরিমাণ বেছে নিন:",
            reply_markup=quantity_keyboard()
        )
        return

    prod_price = get_product_price(qty)
    await state.update_data(quantity=qty, product_price=prod_price)

    await message.answer(
        f"✅ আপনি **{qty} টি** পেন নির্বাচন করেছেন (মূল্য: ৳{prod_price})।\n\n"
        "এবার আপনার **পূর্ণ নাম (Full Name)** লিখুন:",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(OrderFSM.entering_name)

@router.message(OrderFSM.entering_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("অনুগ্রহ করে আপনার সঠিক নাম লিখুন:")
        return

    await state.update_data(full_name=name)
    await message.answer(
        f"ধন্যবাদ, **{name}**!\n\n"
        "এবার আপনার সাথে যোগাযোগের জন্য একটি **সচল মোবাইল নম্বর** দিন (যেমন: 017XXXXXXXX):",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(OrderFSM.entering_phone)

@router.message(OrderFSM.entering_phone)
async def process_phone(message: Message, state: FSMContext):
    raw_phone = normalize_digits(message.text.strip())
    # Clean non-digits
    digits = re.sub(r'\D', '', raw_phone)
    if digits.startswith("880"):
        digits = digits[2:]

    if not (len(digits) == 11 and digits.startswith("01")):
        await message.answer(
            "⚠️ অনুগ্রহ করে সঠিক ১১ ডিজিটের মোবাইল নম্বর দিন (যেমন: `01712345678`):",
            parse_mode="Markdown"
        )
        return

    await state.update_data(phone=digits)
    await message.answer(
        "📍 আপনার ডেলিভারি এলাকা নির্বাচন করুন:",
        reply_markup=delivery_area_keyboard()
    )
    await state.set_state(OrderFSM.choosing_area)

@router.message(OrderFSM.choosing_area)
async def process_area(message: Message, state: FSMContext):
    text = message.text
    if "ঢাকার ভেতরে" in text:
        area = "ঢাকার ভেতরে"
        delivery_fee = DELIVERY_INSIDE_DHAKA
    elif "ঢাকার বাইরে" in text:
        area = "ঢাকার বাইরে"
        delivery_fee = DELIVERY_OUTSIDE_DHAKA
    else:
        await message.answer(
            "অনুগ্রহ করে নিচের অপশন থেকে একটি বেছে নিন:",
            reply_markup=delivery_area_keyboard()
        )
        return

    await state.update_data(delivery_area=area, delivery_fee=delivery_fee)
    await message.answer(
        f"✅ ডেলিভারি চার্জ: ৳{delivery_fee}\n\n"
        "এবার আপনার সম্পূর্ণ ডেলিভারি ঠিকানা লিখুন:\n"
        "*(বাসা/হোল্ডিং নম্বর, রোড, এলাকা, থানা ও জেলা উল্লেখ করুন)*",
        reply_markup=cancel_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(OrderFSM.entering_address)

@router.message(OrderFSM.entering_address)
async def process_address(message: Message, state: FSMContext):
    address = message.text.strip()
    if len(address) < 5:
        await message.answer("অনুগ্রহ করে আপনার বিস্তারিত সম্পূর্ণ ঠিকানা দিন:")
        return

    await state.update_data(address=address)
    await message.answer(
        "💳 আপনি কীভাবে মূল্য পরিশোধ করতে চান? পেমেন্ট মাধ্যম বেছে নিন:",
        reply_markup=payment_method_keyboard()
    )
    await state.set_state(OrderFSM.choosing_payment)

@router.message(OrderFSM.choosing_payment)
async def process_payment(message: Message, state: FSMContext):
    text = message.text
    if "Cash on Delivery" in text or "ক্যাশ অন" in text:
        method = "Cash on Delivery"
        await state.update_data(payment_method=method, trx_id="N/A (COD)")
        await show_order_summary(message, state)
    elif "bKash" in text or "নগদ" in text:
        method = "bKash / Nagad"
        await state.update_data(payment_method=method)
        data = await state.get_data()
        total = data["product_price"] + data["delivery_fee"]
        await message.answer(
            f"📱 **বিকাশ বা নগদ সেন্ড মানি নির্দেশিকা:**\n\n"
            f"আমাদের একাউন্টে মোট **৳{total}** সেন্ড মানি করুন:\n"
            f"🔹 বিকাশ (Personal): `{BKASH_NUMBER}`\n"
            f"🔹 নগদ (Personal): `{NAGAD_NUMBER}`\n\n"
            f"টাকা পাঠানোর পর বিকাশ/নগদের **Transaction ID (TrxID)** টি এখানে লিখে পাঠান:",
            reply_markup=cancel_keyboard(),
            parse_mode="Markdown"
        )
        await state.set_state(OrderFSM.entering_trx_id)
    else:
        await message.answer(
            "অনুগ্রহ করে নিচের অপশন থেকে পেমেন্ট মাধ্যম বেছে নিন:",
            reply_markup=payment_method_keyboard()
        )

@router.message(OrderFSM.entering_trx_id)
async def process_trx_id(message: Message, state: FSMContext):
    trx = message.text.strip()
    if len(trx) < 4:
        await message.answer("অনুগ্রহ করে সঠিক Transaction ID (TrxID) লিখুন:")
        return

    await state.update_data(trx_id=trx)
    await show_order_summary(message, state)

async def show_order_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    total = data["product_price"] + data["delivery_fee"]
    await state.update_data(total_price=total)

    summary_text = (
        f"📋 **আপনার অর্ডারের বিবরণ যাচাই করুন:**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛍️ **পণ্য:** {PRODUCT_NAME}\n"
        f"🔢 **পরিমাণ:** {data['quantity']} পিস\n"
        f"💵 **পণ্যের মূল্য:** ৳{data['product_price']}\n"
        f"🚚 **ডেলিভারি এলাকা:** {data['delivery_area']} (৳{data['delivery_fee']})\n"
        f"💰 **সর্বমোট প্রদেয়:** ৳{total}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **গ্রাহক:** {data['full_name']}\n"
        f"📞 **ফোন:** `{data['phone']}`\n"
        f"📍 **ঠিকানা:** {data['address']}\n"
        f"💳 **পেমেন্ট মেথড:** {data['payment_method']}\n"
        f"🧾 **TrxID:** `{data.get('trx_id', 'N/A')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"সব তথ্য ঠিক থাকলে **'✅ হ্যাঁ, অর্ডার নিশ্চিত করুন'** বাটনে চাপুন।"
    )
    await message.answer(summary_text, reply_markup=order_confirm_keyboard(), parse_mode="Markdown")
    await state.set_state(OrderFSM.confirming_order)

@router.message(OrderFSM.confirming_order, F.text == "✅ হ্যাঁ, অর্ডার নিশ্চিত করুন")
async def confirm_order(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    data["user_id"] = message.from_user.id
    data["username"] = message.from_user.username or ""

    order_code = await create_order(data)
    await state.clear()

    # Confirmation to customer
    success_text = (
        f"🎉 **অভিনন্দন! আপনার অর্ডারটি সফলভাবে গ্রহণ করা হয়েছে!**\n\n"
        f"🆔 **আপনার অর্ডার কোড:** `{order_code}`\n"
        f"💰 **মোট প্রদেয় বিল:** ৳{data['total_price']}\n\n"
        f"খুব শীঘ্রই আমাদের প্রতিনিধি ফোন করে অর্ডারটি কনফার্ম করবেন এবং ডেলিভারি প্রস্তুত করবেন।\n"
        f"যেকোনো প্রয়োজনে আমাদের সাপোর্ট টিমে যোগাযোগ করতে পারেন। ❤️"
    )
    await message.answer(success_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

    # Notification to Admin
    if ADMIN_ID and ADMIN_ID != 0:
        admin_text = (
            f"🚨 **নতুন অর্ডার এসেছে!**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **অর্ডার কোড:** `{order_code}`\n"
            f"🛍️ **পণ্য:** {PRODUCT_NAME} ({data['quantity']} টি)\n"
            f"💰 **মোট বিল:** ৳{data['total_price']} (পণ্য ৳{data['product_price']} + ডেলিভারি ৳{data['delivery_fee']})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **নাম:** {data['full_name']}\n"
            f"📞 **ফোন:** `{data['phone']}`\n"
            f"📍 **ঠিকানা:** {data['address']} ({data['delivery_area']})\n"
            f"💳 **পেমেন্ট:** {data['payment_method']} | Trx: `{data.get('trx_id', 'N/A')}`\n"
            f"👤 **ইউজার:** @{data['username']} (ID: `{data['user_id']}`)\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text,
                reply_markup=admin_order_keyboard(order_code),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
