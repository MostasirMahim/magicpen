# 🚀 Linux VPS সহজ ডেপ্লয়মেন্ট গাইড (Ubuntu / Debian)
## Magic Pen 3D Telegram Bot (@magicpen3d_bot) ২৪/৭ লাইভ রান করার নির্দেশিকা

এই গাইডে থাকা কমান্ডগুলো কপি-পেস্ট করে যেকোনো সাশ্রয়ী Ubuntu VPS (যেমন: DigitalOcean, Hetzner, Linode, Vultr বা যেকোনো ক্লাউড সার্ভার)-এ বটটি ২৪ ঘণ্টা চালু রাখা যাবে।

---

### ধাপ ১: সার্ভার প্যাকেজ আপডেট ও পাইথন ইনস্টলেশন

আপনার কম্পিউটারের টার্মিনাল বা PuTTY দিয়ে VPS সার্ভারে SSH লগইন করুন:

```bash
# সার্ভারের প্যাকেজ আপডেট
sudo apt update && sudo apt upgrade -y

# পাইথন ৩, pip, ভার্চুয়াল এনভায়রনমেন্ট ও গিট ইনস্টল
sudo apt install python3 python3-pip python3-venv git curl -y
```

---

### ধাপ ২: প্রজেক্ট ফোল্ডার তৈরি

```bash
# প্রজেক্ট ফোল্ডার তৈরি ও প্রবেশ
mkdir -p ~/magicpen3d_bot
cd ~/magicpen3d_bot
```

> **ফাইল আপলোড করার উপায়:**
> - আপনি চাইলে GitHub রিপোজিটরি বানিয়ে `git clone <আপনার_ইউআরএল> .` কমান্ড দিতে পারেন।
> - অথবা **FileZilla** / **WinSCP** সফটওয়্যার দিয়ে আপনার পিসির ফাইলগুলো সরাসরি `/home/ubuntu/magicpen3d_bot` ফোল্ডারে আপলোড করে দিতে পারেন।

---

### ধাপ ৩: ভার্চুয়াল এনভায়রনমেন্ট ও ডিপেন্ডেন্সি ইনস্টল

```bash
# ভার্চুয়াল এনভায়রনমেন্ট তৈরি
python3 -m venv venv

# এনভায়রনমেন্ট অ্যাক্টিভেশন
source venv/bin/activate

# pip আপডেট ও প্রয়োজনীয় লাইব্রেরি ইনস্টল
pip install --upgrade pip
pip install -r requirements.txt
```

---

### ধাপ ৪: `.env` ফাইল কনফিগারেশন

```bash
nano .env
```

ফাইলের ভেতরে নিচের তথ্যগুলো পেস্ট করুন:

```env
# Database (Neon PostgreSQL Cloud)
DATABASE_URL=postgresql://neondb_owner:npg_DewMEq9uaK4V@ep-rapid-cake-bet8abv6-pooler.c-9.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Telegram Bot Configuration
BOT_TOKEN=9200368407:AAFnyy1ExB6SarMlmiHf6bDzuoKj2WYBl4Y
ADMIN_ID=আপনার_টেলিগ্রাম_আইডি

# Product Pricing (BDT)
PRODUCT_NAME=Magic Pen 3D (UV Invisible Ink)
PRICE_1_PCS=290
PRICE_2_PCS=550
PRICE_3_PCS=790

# Delivery Charges (BDT)
DELIVERY_INSIDE_DHAKA=80
DELIVERY_OUTSIDE_DHAKA=140

# Payment Accounts
BKASH_NUMBER=017XXXXXXXX
NAGAD_NUMBER=018XXXXXXXX

# Support
SUPPORT_PHONE=017XXXXXXXX
SUPPORT_USERNAME=@MagicPen3DSupport
```

> **সেভ করার নিয়ম:** কিবোর্ডে `Ctrl + O` চেপে `Enter` দিন, এরপর `Ctrl + X` চেপে ন্যানো এডিটর থেকে বের হয়ে আসুন।

---

### ধাপ ৫: লাইভ টেস্ট রান

সার্ভারে ডাটাবেজ ও বট টেস্ট করুন:

```bash
# ডাটাবেজ কানেকশন চেক
python view_orders.py

# টেস্ট রান (বট ঠিকমতো রেসপন্স করছে কিনা দেখতে)
python main.py
```
*(যদি টার্মিনালে `Bot started successfully` দেখায়, তাহলে কিবোর্ডে `Ctrl + C` চেপে থামান। এবার আমরা একে ২৪/৭ ব্যাকগ্রাউন্ড সার্ভিস বানাব)*

---

### ধাপ ৬: Background Service (systemd) তৈরি (সবচেয়ে গুরুত্বপূর্ণ)

সার্ভার রিস্টার্ট হলেও বট যাতে নিজে নিজে অটোমেটিক চালু থাকে:

```bash
sudo nano /etc/systemd/system/magicpen.service
```

নিচের কনফিগারেশনটি হুবহু পেস্ট করুন:

```ini
[Unit]
Description=Magic Pen 3D Telegram Store Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/magicpen3d_bot
ExecStart=/home/ubuntu/magicpen3d_bot/venv/bin/python /home/ubuntu/magicpen3d_bot/main.py
Restart=always
RestartSec=5
EnvironmentFile=/home/ubuntu/magicpen3d_bot/.env

[Install]
WantedBy=multi-user.target
```
*(যদি আপনার VPS-এর ইউজারনেম `ubuntu` না হয়ে `root` বা অন্য কিছু হয়, তবে `User=` এবং পাথে সেই নাম দিন)*

`Ctrl + O`, `Enter`, `Ctrl + X` চেপে সেভ করুন।

---

### ধাপ ৭: সার্ভিস চালু ও এনেবল করা

```bash
# সিস্টেমড রিলোড
sudo systemctl daemon-reload

# বট সার্ভিসটি স্টার্ট এবং অটো-স্টার্ট এনেবল করা
sudo systemctl enable --now magicpen
```

---

### 🛠️ প্রয়োজনীয় হ্যান্ডি কমান্ডসমূহ (Management Cheat Sheet)

| কাজের বিবরণ | কমান্ড |
| :--- | :--- |
| **বটের স্ট্যাটাস দেখতে (Running আছে কিনা)** | `sudo systemctl status magicpen` |
| **রিয়েল-টাইম লাইভ লগ দেখতে** | `sudo journalctl -u magicpen -f` |
| **বট রিস্টার্ট করতে** | `sudo systemctl restart magicpen` |
| **বট বন্ধ করতে** | `sudo systemctl stop magicpen` |
| **বট পুনরায় চালু করতে** | `sudo systemctl start magicpen` |

---

### 🔄 পরবর্তীতে কোড আপডেট করার নিয়ম

ভবিষ্যতে কোনো কোড আপডেট বা পরিবর্তন করলে সার্ভারে ঢুকে শুধু এই কমান্ডগুলো দিলেই হবে:

```bash
cd ~/magicpen3d_bot
# নতুন কোড আপলোড করার পর
sudo systemctl restart magicpen
```
ব্যাস! নতুন কোড স্বয়ংক্রিয়ভাবে লাইভ হয়ে যাবে।
