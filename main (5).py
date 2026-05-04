import json
import time
from datetime import datetime

# ================= FILE NAMES =================
USERS = "users.json"
PRODUCTS = "products.json"

# ================= HELPERS =================
def load(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        with open(file, "w") as f:
            json.dump(default, f, indent=4)
        return default

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def log(user, text):
    with open(f"history_{user}.log", "a") as f:
        f.write(f"[{datetime.now()}] {text}\n")

# ================= INIT =================
users = load(USERS, [
    {"username": "admin", "password": "1234", "balance": 100, "failed": 0, "lock": 0}
])

products = load(PRODUCTS, {
    "Geyimler": [
        {"id": 1, "name": "T-Shirt", "price": 12.5},
        {"id": 2, "name": "Hoodie", "price": 45}
    ],
    "Elektronika": [
        {"id": 1, "name": "Qulaqliq", "price": 35},
        {"id": 2, "name": "Mouse", "price": 15}
    ]
})

# ================= LOGIN =================
def login():
    while True:
        u = input("Username: ")
        p = input("Password: ")

        for user in users:
            if user["username"] == u:

                if time.time() < user["lock"]:
                    print("10 saniye gozle!")
                    continue

                if user["password"] == p:
                    user["failed"] = 0
                    log(u, "LOGIN_SUCCESS")
                    return user
                else:
                    user["failed"] += 1
                    log(u, "LOGIN_FAIL")

                    if user["failed"] == 3:
                        user["lock"] = time.time() + 10
                        user["failed"] = 0
                        print("Bloklandin 10 saniye!")
                save(USERS, users)

# ================= FAVORITES =================
def load_fav(username):
    return load(f"fav_{username}.json", [])

def save_fav(username, data):
    save(f"fav_{username}.json", data)

# ================= BASKET =================
def load_basket(username):
    return load(f"basket_{username}.json", [])

def save_basket(username, data):
    save(f"basket_{username}.json", data)

# ================= CATEGORY =================
def categories(user):
    basket = load_basket(user["username"])
    fav = load_fav(user["username"])

    while True:
        print("\nKateqoriyalar:")
        for i, c in enumerate(products.keys(), 1):
            print(i, c)

        ch = input("Sec (0=geri): ")
        if ch == "0":
            return

        cat = list(products.keys())[int(ch)-1]

        for item in products[cat]:
            print(item["id"], item["name"], item["price"])

        pid = int(input("ID sec: "))
        qty = int(input("Miqdar: "))

        for item in products[cat]:
            if item["id"] == pid:

                act = input("B-sebet F-fav X-back: ").lower()

                if act == "b":
                    basket.append({
                        "name": item["name"],
                        "price": item["price"],
                        "qty": qty
                    })
                    log(user["username"], f"BASKET_ADD {item['name']} x{qty}")

                elif act == "f":
                    fav.append(item)
                    log(user["username"], f"FAV_ADD {item['name']}")

        save_basket(user["username"], basket)
        save_fav(user["username"], fav)

# ================= CART =================
def cart(user):
    basket = load_basket(user["username"])

    while True:
        total = 0
        print("\nSebet:")

        for i, item in enumerate(basket):
            t = item["price"] * item["qty"]
            total += t
            print(i, item["name"], item["qty"], "=", t)

        print("Total:", total)

        cmd = input("checkout / remove / clear / back: ")

        if cmd == "checkout":
            if user["balance"] >= total:
                user["balance"] -= total
                log(user["username"], f"CHECKOUT {total}")
                basket.clear()
                print("Alis ugurlu!")
            else:
                log(user["username"], "CHECKOUT_FAIL")
                print("Balans catmir!")

        elif cmd == "remove":
            i = int(input("index: "))
            basket.pop(i)

        elif cmd == "clear":
            basket.clear()

        elif cmd == "back":
            break

        save_basket(user["username"], basket)
        save(USERS, users)

# ================= FAVORITES MENU =================
def favorites(user):
    fav = load_fav(user["username"])
    basket = load_basket(user["username"])

    for i, f in enumerate(fav):
        print(i, f["name"], f["price"])

    ch = input("Sebete at index (yoxsa enter): ")

    if ch != "":
        f = fav[int(ch)]
        qty = int(input("Miqdar: "))
        basket.append({"name": f["name"], "price": f["price"], "qty": qty})

    save_basket(user["username"], basket)

# ================= HISTORY =================
def history(user):
    try:
        with open(f"history_{user['username']}.log") as f:
            lines = f.readlines()
            for l in lines[-20:]:
                print(l.strip())
    except:
        print("History bosdur")

# ================= SETTINGS =================
def change_pass(user):
    old = input("Kohne sifre: ")
    if old == user["password"]:
        new = input("Yeni sifre: ")
        user["password"] = new
        log(user["username"], "PASSWORD_CHANGED")
        save(USERS, users)
        print("Deyisdirildi!")
    else:
        print("Sehv sifre!")

# ================= MAIN =================
def main():
    user = login()

    while True:
        print("\n1 Kateqoriya")
        print("2 Sebet")
        print("3 Favorit")
        print("4 History")
        print("5 Password")
        print("6 Balans")
        print("0 Exit")

        c = input("Sec: ")

        if c == "1":
            categories(user)
        elif c == "2":
            cart(user)
        elif c == "3":
            favorites(user)
        elif c == "4":
            history(user)
        elif c == "5":
            change_pass(user)
        elif c == "6":
            print("Balans:", user["balance"])
        elif c == "0":
            save(USERS, users)
            break

main()
