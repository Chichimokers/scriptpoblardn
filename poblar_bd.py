from faker import Faker
import pandas as pd
import random
import uuid
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

fake = Faker("es_ES")
load_dotenv("local.env")


# Method to generate common datas
def generate_common_data():
    return {
        "id": uuid.uuid4(),
        "created_at": fake.date_time_between(start_date="-2y", end_date="now"),
        "updated_at": fake.date_time_between(start_date="-2y", end_date="now"),
        "deleted_at": None,
    }


# Method to generate image_urls
def generate_image_url():
    var = f"Designer ({random.randint(0, 15)}).jpeg"
    return f"{os.environ.get('IMAGES')}{var}"


# Category
def generate_category() -> list[dict]:
    categories_data: list[dict] = []
    for _ in ["Electrónica", "Ropa", "Hogar", "Deportes", "Juguetes"]:
        _category: dict = generate_common_data()
        _category.update({"name": _})
        categories_data.append(_category)

    return categories_data


# SubCategory
def generate_subcategory(categories: list[dict]) -> list[dict]:
    subcategories_data: list[dict] = []

    for category in categories:
        for _ in range(3):
            _subcategory: dict = generate_common_data()
            _subcategory.update(
                {
                    "name": fake.unique.word()[:50],
                    "categoryId": category["id"],
                }
            )
            subcategories_data.append(_subcategory)

    return subcategories_data


# Users
def generate_user() -> list[dict]:
    users_data: list[dict] = []

    for _ in range(100):
        _user: dict = generate_common_data()
        _user.update(
            {
                "name": fake.name()[:30],
                "email": f"{fake.user_name()[:15]}{_}@gmail.com"[:40],
                "rol": 1,
                "password": fake.password(length=12),
                "enabled": True,
                "last_login": fake.date_time_between(start_date="-6m", end_date="now"),
                "locked": False,
            }
        )
        users_data.append(_user)

    return users_data


# Provinces
def generate_province() -> list[dict]:
    provinces_data: list[dict] = []
    provinces = [
        "Pinar del Rio",
        "La habana",
        "Artemisa",
        "Mayabeque",
        "Matanzas",
        "Cienfuegos",
        "Villa Clara",
        "Sancti Spiritus",
        "Ciego de Avila",
        "Camaguey",
        "Las Tunas",
        "Granma",
        "Holguin",
        "Santiago de Cuba",
        "Guantanamo",
    ]

    for _ in provinces:
        _province = generate_common_data()
        _province.update({"name": _})
        provinces_data.append(_province)

    return provinces_data


# Discounts
def generate_discount() -> list[dict]:
    discounts_data: list[dict] = []
    num_discounts = max(60, int(3000 * 0.4))

    for _ in range(num_discounts):
        _discount: dict = generate_common_data()
        _discount.update(
            {
                "min": random.randint(2, 10),
                "reduction": round(random.uniform(5, 50), 2),
            }
        )
        discounts_data.append(_discount)

    return discounts_data


# Products
def generate_product(
    discounts: list[dict],
    categories: list[dict],
    subcategories: list[dict],
    provinces: list[dict],
) -> list[dict]:
    products_data: list[dict] = []
    discounts_data_temp: list[dict] = discounts.copy()

    for province in provinces:
        for _ in range(200):
            _category = random.choice(categories)
            matching_subcategories = [
                s for s in subcategories if s["categoryId"] == _category["id"]
            ]

            if not matching_subcategories:  # Skip if no matching subcategories
                continue

            _subcategory = random.choice(matching_subcategories)

            _pdiscounts = None

            if len(discounts_data_temp) > 0 and random.random() > 0.5:
                _pdiscounts = random.choice(discounts_data_temp)
                discounts_data_temp.remove(_pdiscounts)

            _product = generate_common_data()
            _product.update(
                {
                    "name": fake.text(max_nb_chars=30).title()[:100],
                    "price": round(random.uniform(10, 1000), 2),
                    "description": fake.paragraph(nb_sentences=3)[:255],
                    "short_description": fake.sentence()[:255],
                    "quantity": random.randint(0, 100),
                    "categoryId": _category["id"],
                    "subCategoryId": _subcategory["id"],  # Selección segura
                    "discountsId": _pdiscounts["id"] if _pdiscounts else None,
                    "image": generate_image_url(),
                    "weight": random.randint(1, 50),
                    "province_id": str(province["id"]),
                }
            )
            products_data.append(_product)

    return products_data


# Municipalities
def generate_municipality(provinces: list[dict]) -> list[dict]:
    municipalities_data: list[dict] = []

    for _ in range(400):
        _municipality: dict = generate_common_data()
        _municipality.update(
            {
                "name": fake.name()[:50],
                "provinceId": random.choice(provinces)["id"],
                "base_price": random.randint(5, 25),
                "min_hours": 24,
                "max_hours": 24 * random.randint(2, 4),
            }
        )
        municipalities_data.append(_municipality)

    return municipalities_data


# Prices by weights
def generate_price_by_weight(municipalities: list[dict]) -> list[dict]:
    prices_bye_wight_data: list[dict] = []
    unique_prices = set()

    for municipality in municipalities:
        num_prices = random.randint(1, 8)
        for _ in range(num_prices):
            while True:
                _price = round(random.uniform(1, 50), 2)
                min_weight = random.randint(10, 80)
                if (municipality["id"], min_weight) not in unique_prices:
                    unique_prices.add((municipality["id"], min_weight))
                    _pbw: dict = generate_common_data()
                    _pbw.update(
                        {
                            "municipalityId": municipality["id"],
                            "price": _price,
                            "minWeight": min_weight,
                        }
                    )
                    prices_bye_wight_data.append(_pbw)
                    break

    return prices_bye_wight_data


# Orders
def generate_order(users: list[dict], municipalities: list[dict]) -> list[dict]:
    orders_data: list[dict] = []

    for _ in range(300):
        _order = generate_common_data()
        _order.update(
            {
                "receiver_name": fake.name()[:70],
                "phone": fake.numerify("+34 6## ### ###")[:15],
                "aux_phone": fake.numerify("+34 6## ### ###")[:15],
                "address": fake.street_address()[:255],
                "CI": fake.bothify(text="########?").upper(),
                "subtotal": 0.0,
                "status": random.choice(
                    ["pending", "accepted", "cancelled", "retired", "paid", "completed"]
                ),
                "userId": random.choice(users)["id"],
                "stripe_id": fake.uuid4() if random.random() > 0.5 else None,
                "shipping_price": random.randint(5, 40),
            }
        )
        orders_data.append(_order)

    return orders_data


# Order products
def generate_order_product(orders: list[dict], products: list[dict]) -> list[dict]:
    order_product_data: list[dict] = []

    for i, order in enumerate(orders):
        _num_products: int = random.randint(1, 6)
        _selected_products = random.choices(products, k=_num_products)
        subtotal: float = 0.0

        for product in _selected_products:
            _quantity: int = random.randint(1, 3)
            subtotal += product["price"] * _quantity

            _order_product: dict = generate_common_data()
            _order_product.update(
                {
                    "orderId": order["id"],
                    "productId": product["id"],
                    "quantity": _quantity,
                }
            )
            order_product_data.append(_order_product)

        orders[i]["subtotal"] = round(subtotal, 2)

    return order_product_data


# Ratings
def generate_rating(users: list[dict], products: list[dict]) -> list[dict]:
    rating_data: list[dict] = []
    unique: set = set()

    while len(unique) < 500:
        user = random.choice(users)["id"]
        product = random.choice(products)["id"]
        if (user, product) not in unique:
            unique.add((user, product))
            _rating: dict = generate_common_data()
            _rating.update(
                {
                    "rate": random.randint(1, 5),
                    "userId": user,
                    "productId": product,
                }
            )
            rating_data.append(_rating)

    return rating_data


def generate_data():
    # --- Generación segura de datos ---
    # 1. Categorias
    categories_data: list[dict] = generate_category()

    # 2. SubCategorias
    subcategories_data: list[dict] = generate_subcategory(categories_data)

    # 3. User
    users_data: list[dict] = generate_user()

    # 4. Province (15 provincias)
    provinces_data: list[dict] = generate_province()

    # 5. tb_discounts (60 descuentos para 200 productos con 30% de probabilidad)
    discounts_data: list[dict] = generate_discount()

    # 6. tb_products (200 productos)
    products_data: list[dict] = generate_product(
        discounts_data, categories_data, subcategories_data, provinces_data
    )

    # 7. Municipality
    municipalities_data: list[dict] = generate_municipality(provinces_data)

    # 8. Prices by Weight
    prices_by_weight_data: list[dict] = generate_price_by_weight(municipalities_data)

    # 9. tb_orders (300 órdenes)
    orders_data: list[dict] = generate_order(users_data, municipalities_data)

    # 10. tb_order_products (Relación segura)
    order_products_data: list[dict] = generate_order_product(orders_data, products_data)

    # 11. tb_rating (500 ratings únicos)
    rating_data: list[dict] = generate_rating(users_data, products_data)

    return {
        "tb_category": categories_data,
        "tb_subcategory": subcategories_data,
        "tb_user": users_data,
        "tb_province": provinces_data,
        "tb_discounts": discounts_data,
        "tb_products": products_data,
        "tb_municipality": municipalities_data,
        "tb_price_by_weight": prices_by_weight_data,
        "tb_orders": orders_data,
        "tb_order_products": order_products_data,
        "tb_rating": rating_data,
    }

    # --- Exportar a CSV ---


def safe_save(df, name):
    df.replace({pd.NaT: None}, inplace=True)  # Manejar NaT para PostgreSQL
    df.to_csv(f"{name}.csv", index=False, sep=";", encoding="utf-8")


def save_all(items: dict) -> None:
    for name, data in items.items():
        df = pd.DataFrame(data)
        safe_save(df, name)


def load_to_postgres():
    try:
        engine = create_engine("postgresql://basededato1:contrbasededato2aseña@localhost:5432/esaquishop")

        tables = [
            "tb_province",
            "tb_category",
            "tb_subcategory",
            "tb_user",
            "tb_discounts",
            "tb_products",
            "tb_orders",
            "tb_order_products",
            "tb_rating",
            "tb_municipality",
            "tb_price_by_weight",
        ]

        #

        for table in tables:
            df = pd.read_csv(f"{table}.csv", sep=";", dtype={"id": str})
            df.to_sql(
                name=table, con=engine, if_exists="append", index=False, method="multi"
            )
            print(f"✅ Tabla {table} cargada exitosamente")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    data: dict = generate_data()
    save_all(data)
    load_to_postgres()
