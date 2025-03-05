from faker import Faker
import pandas as pd
import random
import uuid
from sqlalchemy import create_engine


def generate_common_data():
    fake = Faker('es_ES')

    return {
        'id': uuid.uuid4(),
        'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
        'updated_at': fake.date_time_between(start_date='-2y', end_date='now'),
        'deleted_at': None
    }

def generate_image_url():
    var = f'Designer ({random.randint(0, 15)}).jpeg'
    return f'http://localhost:8080/images/{var}'


def generate_data():
    fake = Faker('es_ES')

    # --- Generación segura de datos ---

    # 1. tb_category (5 categorías)
    categories = pd.DataFrame([{
        'id': uuid.uuid4(),
        'name': name,
        'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
        'updated_at': fake.date_time_between(start_date='-2y', end_date='now'),
        'deleted_at': None
    } for name in ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Juguetes']])

    # 2. tb_subcategory (15 subcategorías - 3 por categoría)
    subcategories_data = []
    for category_id in categories['id']:
        # 3 subcategorías por categoría (5 categorías × 3 = 15)
        for _ in range(3):
            subcategories_data.append({
                'id': uuid.uuid4(),
                'name': fake.unique.word()[:50],
                'categoryId': category_id,  # Asignación directa a la categoría
                'created_at': fake.date_time_between(start_date='-1y', end_date='now'),
                'updated_at': fake.date_time_between(start_date='-1y', end_date='now'),
                'deleted_at': None
            })
    subcategories = pd.DataFrame(subcategories_data)

    # 3. tb_user (100 usuarios)
    users = pd.DataFrame([{
        'id': uuid.uuid4(),
        'name': fake.name()[:30],
        'email': f"{fake.user_name()[:15]}{i}@gmail.com"[:40],
        'rol': random.randint(1, 2),
        'password': fake.password(length=12),
        'enabled': True,
        'last_login': fake.date_time_between(start_date='-6m', end_date='now'),
        'locked': False,
        'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
        'updated_at': fake.date_time_between(start_date='-2y', end_date='now'),
        'deleted_at': None
    } for i in range(100)])

    # 4. Province (15 provincias)
    provinces_data = []
    provinces = ['Pinar del Rio', 'La habana', 'Artemisa', 'Mayabeque', 'Matanzas', 'Cienfuegos', 'Villa Clara',
                 'Sancti Spiritus', 'Ciego de Avila', 'Camaguey', 'Las Tunas', 'Granma', 'Holguin', 'Santiago de Cuba',
                 'Guantanamo']

    for _ in provinces:
        _province = generate_common_data()
        _province.update({'name': _})
        provinces_data.append(_province)

    provinces_data_frame = pd.DataFrame(provinces_data)

    # 5. tb_discounts (60 descuentos para 200 productos con 30% de probabilidad)
    discounts_data = []
    num_discounts = max(60, int(3000 * 0.4)) # Mínimo 1500 descuentos

    for _ in range(num_discounts):
        _discount: dict = generate_common_data()
        _discount.update({
            'min': random.randint(2, 10),
            'reduction': round(random.uniform(5, 50), 2),
        })
        discounts_data.append(_discount)

    discounts_data_frame = pd.DataFrame(discounts_data)

    # 6. tb_products (200 productos)
    products_data = []
    discounts_data_temp = discounts_data.copy()
    for province in provinces_data:
        for _ in range(200):
            # Seleccionar categoría y sus subcategorías
            category = random.choice(categories.to_dict('records'))
            subcats_for_category = subcategories[subcategories['categoryId'] == category['id']]

            # Seleccion del descuento
            _pdiscounts = None

            if len(discounts_data_temp) > 0 and random.random() > 0.5:
                _pdiscounts = random.choice(discounts_data_temp)
                discounts_data_temp.remove(_pdiscounts)

            _product = generate_common_data()
            _product.update({
                'name': fake.text(max_nb_chars=30).title()[:100],
                'price': round(random.uniform(10, 1000), 2),
                'description': fake.paragraph(nb_sentences=3)[:255],
                'short_description': fake.sentence()[:255],
                'quantity': random.randint(0, 100),
                'categoryId': category['id'],
                'subCategoryId': subcats_for_category.sample(1)['id'].values[0],# Selección segura
                'discountsId': _pdiscounts['id'] if _pdiscounts else None,
                'image': generate_image_url(),
                'weight': random.randint(1, 50),
                'province_id': str(province['id']),
            })
            products_data.append(_product)

    products = pd.DataFrame(products_data)

    # 7. Municipality
    municipalities_data = []

    for _ in range(400):
        _municipality = generate_common_data()
        _municipality.update({
            'name': fake.name()[:50],
            'provinceId': random.choice(provinces_data_frame['id']),
            'base_price': random.randint(5, 25),
            'min_hours': 24,
            'max_hours': 24 * random.randint(2, 4),
        })
        municipalities_data.append(_municipality)

    municipalities_data_frame = pd.DataFrame(municipalities_data)

    # 8. Prices by Weight
    prices_by_weight_data = []
    unique_prices = set()

    for municipality_id in municipalities_data_frame['id']:
        num_prices = random.randint(1, 4)
        for _ in range(num_prices):
            while True:
                _price = round(random.uniform(1, 50), 2)
                min_weight = random.randint(10, 50)
                if (municipality_id, _price) not in unique_prices:
                    unique_prices.add((municipality_id, _price))
                    _pbw = generate_common_data()
                    _pbw.update({
                        'municipalityId': municipality_id,
                        'price': _price,
                        'minWeight': min_weight,
                    })
                    prices_by_weight_data.append(_pbw)
                    break

    prices_by_weight_data_frame = pd.DataFrame(prices_by_weight_data)

    # 9. tb_orders (300 órdenes)
    orders_data = []
    provinces = [
        'Álava', 'Albacete', 'Alicante', 'Almería', 'Asturias', 'Ávila',
        'Badajoz', 'Baleares', 'Barcelona', 'Burgos', 'Cáceres', 'Cádiz',
        'Cantabria', 'Castellón', 'Ciudad Real', 'Córdoba', 'Cuenca',
        'Gerona', 'Granada', 'Guadalajara', 'Guipúzcoa', 'Huelva',
        'Huesca', 'Jaén', 'La Coruña', 'La Rioja', 'Las Palmas', 'León',
        'Lérida', 'Lugo', 'Madrid', 'Málaga', 'Murcia', 'Navarra',
        'Orense', 'Palencia', 'Pontevedra', 'Salamanca', 'Tenerife',
        'Segovia', 'Sevilla', 'Soria', 'Tarragona', 'Teruel', 'Toledo',
        'Valencia', 'Valladolid', 'Vizcaya', 'Zamora', 'Zaragoza'
    ]

    for _ in range(300):
        _order = generate_common_data()
        _order.update({
            'receiver_name': fake.name()[:70],
            'phone': fake.numerify('+34 6## ### ###')[:15],
            'province': random.choice(provinces)[:20],
            'address': fake.street_address()[:255],
            'CI': fake.bothify(text='########?').upper(),
            'subtotal': 0.0,
            'status': random.choice(['pending', 'accepted', 'cancelled', 'retired', 'paid', 'completed']),
            'userId': random.choice(users['id']),
            'stripe_id': fake.uuid4() if random.random() > 0.5 else None,
        })
        orders_data.append(_order)
    orders = pd.DataFrame(orders_data)

    # 10. tb_order_products (Relación segura)
    order_products = []
    for _, order in orders.iterrows():
        num_products = random.randint(1, 5)
        selected_products = products.sample(num_products)
        subtotal = 0.0

        for _, product in selected_products.iterrows():
            quantity = random.randint(1, 3)
            subtotal += product['price'] * quantity

            _order = generate_common_data()
            _order.update({
                'orderId': order['id'],
                'productId': product['id'],
                'quantity': quantity,
            })
            order_products.append(_order)

        orders.loc[orders['id'] == order['id'], 'subtotal'] = round(subtotal, 2)

    order_products = pd.DataFrame(order_products)

    # 11. tb_rating (500 ratings únicos)
    unique_pairs = set()
    while len(unique_pairs) < 500:
        user = random.choice(users['id'])
        product = random.choice(products['id'])
        unique_pairs.add((user, product))

    ratings = pd.DataFrame([{
        'id': uuid.uuid4(),
        'rate': random.randint(1, 5),
        'userId': pair[0],
        'productId': pair[1],
        'created_at': fake.date_time_between(start_date='-3m', end_date='now'),
        'updated_at': fake.date_time_between(start_date='-3m', end_date='now'),
        'deleted_at': None
    } for pair in list(unique_pairs)[:500]])


    # --- Exportar a CSV ---
    def safe_save(df, name):
        df.replace({pd.NaT: None}, inplace=True)  # Manejar NaT para PostgreSQL
        df.to_csv(f'{name}.csv', index=False, sep=';', encoding='utf-8')

    safe_save(categories, 'tb_category')
    safe_save(subcategories, 'tb_subcategory')
    safe_save(users, 'tb_user')
    safe_save(discounts_data_frame, 'tb_discounts')
    safe_save(provinces_data_frame, 'tb_province')
    safe_save(products, 'tb_products')
    safe_save(municipalities_data_frame, 'tb_municipality')
    safe_save(prices_by_weight_data_frame, 'tb_price_by_weight')
    safe_save(orders, 'tb_orders')
    safe_save(order_products, 'tb_order_products')
    safe_save(ratings, 'tb_rating')



def load_to_postgres():
    try:
        engine = create_engine('postgresql+psycopg2://myuser:mypassword@localhost:5432/esaquishop')

        tables = [
            'tb_province',
            'tb_category',
            'tb_subcategory',
            'tb_user',
            'tb_discounts',
            'tb_products',
            'tb_orders',
            'tb_order_products',
            'tb_rating',
            'tb_municipality',
            'tb_price_by_weight'
        ]

        # 

        for table in tables:
            df = pd.read_csv(f'{table}.csv', sep=';', dtype={'id': str})
            df.to_sql(
                name=table,
                con=engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            print(f'✅ Tabla {table} cargada exitosamente')

    except Exception as e:
        print(f'❌ Error: {str(e)}')
        raise


if __name__ == "__main__":
    generate_data()
    load_to_postgres()
