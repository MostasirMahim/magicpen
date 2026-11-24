import csv
import os
import tempfile
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command

from config import ADMIN_ID
from database import (
    get_stats,
    get_recent_orders,
    get_order_by_code,
    update_order_status,
    get_all_orders,
    get_orders_by_status,
)

router = Router()

def is_admin(user_id: int) -> bool:
    return ADMIN_ID and user_id == ADMIN_ID

def admin_dashboard_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="⏳ পেন্ডিং অর্ডারসমূহ", callback_data="adm_view_pending"),
            InlineKeyboardButton(text="📥 এক্সেল/CSV ডাউনলোড", callback_data="adm_export_csv"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

@router.message(Command("admin"))
async def admin_dashboard(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ আপনার এই কমান্ড ব্যবহারের অনুমতি নেই।")
        return

    stats = await get_stats()
    recent = await get_recent_orders(5)

    text = (
        f"👑 **Magic Pen 3D - Admin Dashboard** 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 **মোট অর্ডার:** {stats['total_orders']} টি\n"
        f"⏳ **পেন্ডিং অর্ডার:** {stats['pending_orders']} টি\n"
        f"✅ **কনফার্মড অর্ডার:** {stats['confirmed_orders']} টি\n"
        f"💰 **কনফার্মড সেলস:** ৳{stats['total_revenue']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 **সর্বশেষ ৫টি অর্ডার:**\n\n"
    )

    if not recent:
        text += "এখনো কোনো অর্ডার আসেনি।"
    else:
        for ord_data in recent:
            text += (
                f"• `{ord_data['order_code']}` | {ord_data['full_name']} | ৳{ord_data['total_price']} | "
                f"[{ord_data['status']}]\n"
                f"  📞 `{ord_data['phone']}` | {ord_data['created_at']}\n"
            )

    await message.answer(text, reply_markup=admin_dashboard_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "adm_view_pending")
async def admin_pending_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("অনুমতি নেই!", show_alert=True)
        return

    pending = await get_orders_by_status("PENDING", 10)
    if not pending:
        await callback.message.answer("🎉 বর্তমানে কোনো পেন্ডিং অর্ডার নেই! সব অর্ডার প্রসেস করা হয়েছে।")
        await callback.answer()
        return

    text = "⏳ **বর্তমানে পেন্ডিং অর্ডারসমূহ (সর্বোচ্চ ১০টি):**\n━━━━━━━━━━━━━━━━━━━━\n"
    for ord_data in pending:
        text += (
            f"🆔 `{ord_data['order_code']}` | 👤 {ord_data['full_name']}\n"
            f"📞 ফোন: `{ord_data['phone']}`\n"
            f"🛍️ পরিমাণ: {ord_data['quantity']} টি | বিল: ৳{ord_data['total_price']}\n"
            f"📍 এলাকা: {ord_data['delivery_area']}\n"
            f"💳 পেমেন্ট: {ord_data['payment_method']}\n"
            f"──────────────────\n"
        )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.message(Command("export"))
@router.callback_query(F.data == "adm_export_csv")
async def admin_export_csv(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not is_admin(user_id):
        if isinstance(event, CallbackQuery):
            await event.answer("অনুমতি নেই!", show_alert=True)
        else:
            await event.answer("⛔ আপনার এই কমান্ড ব্যবহারের অনুমতি নেই।")
        return

    orders = await get_all_orders()
    if not orders:
        msg = "এক্সপোর্ট করার মতো কোনো অর্ডার এখনো পাওয়া যায়নি।"
        if isinstance(event, CallbackQuery):
            await event.answer(msg, show_alert=True)
        else:
            await event.answer(msg)
        return

    # Write CSV with UTF-8 BOM so Microsoft Excel renders Bengali correctly
    temp_dir = tempfile.gettempdir()
    csv_file_path = os.path.join(temp_dir, "magicpen_orders.csv")

    fieldnames = [
        "Order ID", "Date", "Status", "Customer Name", "Phone",
        "Quantity", "Product Price", "Delivery Fee", "Total Price",
        "Delivery Area", "Full Address", "Payment Method", "TrxID", "Telegram Username", "Telegram UserID"
    ]

    with open(csv_file_path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        for o in orders:
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

    doc = FSInputFile(csv_file_path, filename="MagicPen3D_Orders.csv")
    caption = f"📊 **Magic Pen 3D - সমস্ত অর্ডারের এক্সেল/CSV ফাইল**\nমোট অর্ডার: {len(orders)} টি"

    if isinstance(event, CallbackQuery):
        await event.message.answer_document(doc, caption=caption, parse_mode="Markdown")
        await event.answer("ফাইল পাঠানো হয়েছে!")
    else:
        await event.answer_document(doc, caption=caption, parse_mode="Markdown")

@router.callback_query(F.data.startswith("adm_confirm:"))
async def admin_confirm_order(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("অনুমতি নেই!", show_alert=True)
        return

    order_code = callback.data.split(":")[1]
    order = await get_order_by_code(order_code)
    if not order:
        await callback.answer("অর্ডার পাওয়া যায়নি!", show_alert=True)
        return

    await update_order_status(order_code, "CONFIRMED")
    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ **স্ট্যাটাস: অ্যাডমিন কর্তৃক কনফার্মড হয়েছে!**",
        parse_mode="Markdown"
    )
    await callback.answer(f"অর্ডার {order_code} কনফার্ম করা হয়েছে!")

    # Notify customer
    try:
        user_id = order["user_id"]
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 **আপনার অর্ডার কনফার্ম করা হয়েছে!**\n\n"
                f"🆔 অর্ডার কোড: `{order_code}`\n"
                f"পণ্য: {order['quantity']} টি Magic Pen 3D\n"
                f"মোট মূল্য: ৳{order['total_price']}\n\n"
                f"ডেলিভারি পার্টনারের মাধ্যমে শীঘ্রই আপনার ঠিকানায় পাঠিয়ে দেওয়া হবে। সাথে থাকার জন্য ধন্যবাদ! ❤️"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Customer notification error: {e}")

@router.callback_query(F.data.startswith("adm_cancel:"))
async def admin_cancel_order(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("অনুমতি নেই!", show_alert=True)
        return

    order_code = callback.data.split(":")[1]
    order = await get_order_by_code(order_code)
    if not order:
        await callback.answer("অর্ডার পাওয়া যায়নি!", show_alert=True)
        return

    await update_order_status(order_code, "CANCELLED")
    await callback.message.edit_text(
        callback.message.text + f"\n\n❌ **স্ট্যাটাস: বাতিল করা হয়েছে!**",
        parse_mode="Markdown"
    )
    await callback.answer(f"অর্ডার {order_code} বাতিল করা হয়েছে!")

    # Notify customer
    try:
        user_id = order["user_id"]
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"⚠️ **অর্ডার আপডেট:**\n\n"
                f"আপনার অর্ডার `{order_code}` টি বাতিল করা হয়েছে।\n"
                f"যেকোনো প্রয়োজনে আমাদের সাপোর্টে যোগাযোগ করুন।"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Customer notification error: {e}")
