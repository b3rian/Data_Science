import random
from faker import Faker
import mysql.connector
from datetime import datetime, timedelta
import time

# Initialize Faker and database connection
fake = Faker()
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Augengneiss@8189',
    database='greensproutorganicsdb',
)
cursor = conn.cursor()

# Constants based on your max record counts
MAX_EMPLOYEES = 200
MAX_STORES = 12
MAX_PRODUCTS = 5000
MAX_CUSTOMERS = 30000
MAX_SUPPLIERS = 300
MAX_DEPARTMENTS = 15
MAX_CATEGORIES = 100
MAX_SALES_PER_STORE_PER_YEAR = 50000  # ~1,000 transactions/store/week

def create_departments():
    print("Creating departments...")
    departments = [
        ('Executive', 500000),
        ('Finance', 300000),
        ('Human Resources', 250000),
        ('Marketing', 200000),
        ('Operations', 400000),
        ('Produce', 350000),
        ('Grocery', 300000),
        ('Deli/Bakery', 280000),
        ('Customer Service', 220000),
        ('Inventory', 270000),
        ('IT', 180000),
        ('Maintenance', 150000),
        ('Quality Control', 160000),
        ('Sustainability', 120000),
        ('Community Outreach', 100000)
    ]
    
    cursor.executemany(
        "INSERT INTO departments (department_name, budget) VALUES (%s, %s)",
        departments[:MAX_DEPARTMENTS]
    )
    conn.commit()

def create_stores():
    print("Creating stores...")
    stores = []
    cities = [
        ('Portland', 'OR'), ('Seattle', 'WA'), ('Eugene', 'OR'),
        ('Boise', 'ID'), ('Spokane', 'WA'), ('Tacoma', 'WA'),
        ('Salem', 'OR'), ('Vancouver', 'WA'), ('Bend', 'OR'),
        ('Missoula', 'MT'), ('Ashland', 'OR'), ('Bellingham', 'WA')
    ]
    
    for i in range(MAX_STORES):
        city, state = cities[i]
        stores.append((
            f"{city} {fake.street_suffix()}",
            fake.street_address(),
            city,
            state,
            fake.zipcode_in_state(state),
            fake.phone_number()[:20],
            f"info.{city.lower()}@greensprout.com",
            fake.date_between(start_date='-8y', end_date='today'),
            random.randint(2000, 5000),  # square footage
            None  # manager_id will be set later
        ))
    
    cursor.executemany(
        """INSERT INTO stores (store_name, address, city, state, zip_code, 
           phone, email, opening_date, square_footage, manager_id) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        stores
    )
    conn.commit()

def create_product_categories():
    print("Creating product categories...")
    categories = []
    main_categories = [
        'Produce', 'Dairy', 'Bakery', 'Meat', 'Seafood',
        'Frozen Foods', 'Dry Goods', 'Beverages', 'Snacks',
        'Household', 'Personal Care', 'Supplements'
    ]
    
    # Create main categories
    for main in main_categories:
        categories.append((main, f"Organic {main} products", None))
    
    # Create subcategories (3-5 per main category)
    for main_id in range(1, len(main_categories)+1):
        for i in range(random.randint(3,5)):
            sub_name = fake.word().capitalize() + " " + main_categories[main_id-1]
            categories.append((sub_name, f"Specialty {sub_name}", main_id))
    
    cursor.executemany(
        """INSERT INTO product_categories (category_name, description, parent_category_id) 
           VALUES (%s, %s, %s)""",
        categories[:MAX_CATEGORIES]
    )
    conn.commit()

def create_suppliers():
    print("Creating suppliers...")
    suppliers = []
    supplier_types = [
        'Organic Farm', 'Fair Trade Co-op', 'Local Producer',
        'Distributor', 'Specialty Importer'
    ]
    
    for _ in range(MAX_SUPPLIERS):
        suppliers.append((
            fake.company() + " " + random.choice(('Organics', 'Farms', 'Goods', 'Provisions')),
            fake.name(),
            fake.unique.email(),
            fake.phone_number()[:20],
            fake.street_address(),
            fake.city(),
            fake.state_abbr(),
            fake.zipcode(),
            random.choice(('USDA Organic', 'Fair Trade', 'Non-GMO', 'B Corp')),
            fake.date_between(start_date='-10y', end_date='-1y')
        ))
    
    cursor.executemany(
        """INSERT INTO suppliers (supplier_name, contact_name, email, phone, 
           address, city, state, zip_code, certification_status, partnership_start_date) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        suppliers
    )
    conn.commit()

def create_products():
    print("Creating products...")
    cursor.execute("SELECT category_id FROM product_categories")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT supplier_id FROM suppliers")
    supplier_ids = [row[0] for row in cursor.fetchall()]
    
    products = []
    organic_keywords = ['Organic', 'Natural', 'Sustainable', 'Eco', 'Green', 'Bio']
    product_types = [
        ('Fruit', 'lb'), ('Vegetable', 'lb'), ('Milk', 'gal'), ('Cheese', 'oz'),
        ('Bread', 'loaf'), ('Pasta', 'oz'), ('Coffee', 'lb'), ('Tea', 'oz'),
        ('Cereal', 'oz'), ('Snack Bar', 'ct'), ('Soap', 'bar'), ('Shampoo', 'fl oz')
    ]
    
    for _ in range(MAX_PRODUCTS):
        p_type, unit = random.choice(product_types)
        product_name = f"{random.choice(organic_keywords)} {fake.word().capitalize()} {p_type}"
        cost = round(random.uniform(0.5, 20), 2)
        price = round(cost * random.uniform(1.3, 2.5), 2)  # 30-150% markup
        
        products.append((
            product_name,
            f"Delicious {product_name}. {fake.sentence()}",
            random.choice(category_ids),
            random.choice(supplier_ids),
            price,
            cost,
            round(random.uniform(0.1, 5),2),  # weight
            random.choice([True, False]),
            random.choice([True, False]),
            random.choice([True, False]),
            fake.date_between(start_date='-5y', end_date='today')
        ))
    
    # Batch insert for performance
    batch_size = 1000
    for i in range(0, len(products), batch_size):
        cursor.executemany(
            """INSERT INTO products (product_name, description, category_id, supplier_id, 
               unit_price, cost, weight, organic, fair_trade, discontinued, date_added) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            products[i:i+batch_size]
        )
        conn.commit()
        print(f"Inserted {min(i+batch_size, len(products))}/{len(products)} products")

def create_employees():
    print("Creating employees...")
    cursor.execute("SELECT department_id FROM departments")
    dept_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT store_id FROM stores")
    store_ids = [row[0] for row in cursor.fetchall()]
    
    # First create executives (department_id=1)
    executives = []
    exec_titles = ['CEO', 'CFO', 'COO', 'VP Marketing', 'VP Operations', 'VP Finance']
    for i in range(6):  # 6 executives
        executives.append((
            fake.first_name(),
            fake.last_name(),
            fake.unique.email(),
            fake.phone_number()[:20],
            fake.date_between(start_date='-8y', end_date='-5y'),
            exec_titles[i],
            1,  # department_id for Executive
            random.randint(150000, 250000),
            None,  # no manager
            None,  # no store
            'active'
        ))
    
    cursor.executemany(
        """INSERT INTO employees (first_name, last_name, email, phone, hire_date, 
           job_title, department_id, salary, manager_id, store_id, status) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        executives
    )
    conn.commit()
    
    # Get executive IDs for managers
    cursor.execute("SELECT employee_id FROM employees")
    exec_ids = [row[0] for row in cursor.fetchall()]
    
    # Create department managers
    dept_managers = []
    for dept_id in dept_ids[1:]:  # skip Executive dept
        dept_managers.append((
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.phone_number()[:20],
            fake.date_between(start_date='-7y', end_date='-3y'),
            f"{fake.job()} Manager",
            dept_id,
            random.randint(65000, 85000),
            random.choice(exec_ids),
            None,  # no store
            'active'
        ))
    
    cursor.executemany(
        """INSERT INTO employees (first_name, last_name, email, phone, hire_date, 
           job_title, department_id, salary, manager_id, store_id, status) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        dept_managers
    )
    conn.commit()
    
    # Get manager IDs for store managers
    cursor.execute("SELECT employee_id FROM employees")
    manager_ids = [row[0] for row in cursor.fetchall()]
    
    # Create store managers
    store_managers = []
    for store_id in store_ids:
        store_managers.append((
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.phone_number()[:20],
            fake.date_between(start_date='-6y', end_date='-2y'),
            'Store Manager',
            5,  # Operations department
            random.randint(75000, 100000),
            random.choice(exec_ids),
            store_id,
            'active'
        ))
    
    cursor.executemany(
        """INSERT INTO employees (first_name, last_name, email, phone, hire_date, 
           job_title, department_id, salary, manager_id, store_id, status) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        store_managers
    )
    conn.commit()
    
    # Update stores with manager IDs
    cursor.execute("SELECT employee_id, store_id FROM employees WHERE job_title = 'Store Manager'")
    for emp_id, store_id in cursor.fetchall():
        cursor.execute(
            "UPDATE stores SET manager_id = %s WHERE store_id = %s",
            (emp_id, store_id))
    conn.commit()
    
    # Create regular employees
    regular_employees = []
    job_titles = {
        2: ['Accountant', 'Financial Analyst', 'Payroll Specialist'],  # Finance
        3: ['HR Generalist', 'Recruiter', 'Training Coordinator'],  # HR
        4: ['Marketing Specialist', 'Graphic Designer', 'Social Media Manager'],  # Marketing
        5: ['Operations Coordinator', 'Logistics Specialist'],  # Operations
        6: ['Produce Clerk', 'Produce Manager', 'Quality Inspector'],  # Produce
        7: ['Grocery Clerk', 'Stock Associate', 'Inventory Specialist'],  # Grocery
        8: ['Deli Clerk', 'Baker', 'Chef'],  # Deli/Bakery
        9: ['Cashier', 'Customer Service Rep', 'Returns Specialist'],  # Customer Service
        10: ['Inventory Clerk', 'Receiving Specialist'],  # Inventory
        11: ['IT Support', 'Systems Analyst'],  # IT
        12: ['Maintenance Technician', 'Janitor'],  # Maintenance
    }
    
    remaining_employees = MAX_EMPLOYEES - len(executives) - len(dept_managers) - len(store_managers)
    
    for _ in range(remaining_employees):
        dept_id = random.choice(dept_ids[1:])  # skip Executive
        title = random.choice(job_titles[dept_id])
        salary = 0
        
        # Set salary ranges based on department
        if dept_id in [6,7,8]:  # Store operations
            salary = random.randint(32000, 50000)
        elif dept_id == 9:  # Customer Service
            salary = random.randint(30000, 42000)
        elif dept_id == 11:  # IT
            salary = random.randint(50000, 75000)
        else:  # Other departments
            salary = random.randint(35000, 60000)
        
        # 80% chance to be assigned to a store if in retail ops
        store_id = None
        if dept_id in [6,7,8,9,10,12] and random.random() < 0.8:
            store_id = random.choice(store_ids)
        
        regular_employees.append((
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.phone_number()[:20],
            fake.date_between(start_date='-5y', end_date='today'),
            title,
            dept_id,
            salary,
            random.choice(manager_ids),
            store_id,
            random.choices(['active', 'on_leave', 'terminated'], weights=[0.9, 0.05, 0.05])[0]
        ))
    
    # Batch insert for performance
    batch_size = 500
    for i in range(0, len(regular_employees), batch_size):
        cursor.executemany(
            """INSERT INTO employees (first_name, last_name, email, phone, hire_date, 
               job_title, department_id, salary, manager_id, store_id, status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            regular_employees[i:i+batch_size]
        )
        conn.commit()
        print(f"Inserted {min(i+batch_size, len(regular_employees))}/{len(regular_employees)} employees")

def create_customers():
    print("Creating customers...")
    cursor.execute("SELECT store_id FROM stores")
    store_ids = [row[0] for row in cursor.fetchall()]
    
    customers = []
    for _ in range(MAX_CUSTOMERS):
        loyalty_member = random.random() < 0.3  # 30% chance
        customers.append((
            fake.first_name(),
            fake.last_name(),
            fake.unique.email(),
            fake.phone_number(),
            fake.street_address(),
            fake.city(),
            fake.state_abbr(),
            fake.zipcode(),
            loyalty_member,
            fake.date_between(start_date='-5y', end_date='today') if loyalty_member else None,
            random.choice(store_ids) if loyalty_member and random.random() < 0.7 else None
        ))
    
    # Batch insert for performance
    batch_size = 1000
    for i in range(0, len(customers), batch_size):
        cursor.executemany(
            """INSERT INTO customers (first_name, last_name, email, phone, address, 
               city, state, zip_code, loyalty_member, member_since, preferred_store_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            customers[i:i+batch_size]
        )
        conn.commit()
        print(f"Inserted {min(i+batch_size, len(customers))}/{len(customers)} customers")

def create_loyalty_program():
    print("Creating loyalty program members...")
    cursor.execute(
        "SELECT customer_id FROM customers WHERE loyalty_member = TRUE"
    )
    member_ids = [row[0] for row in cursor.fetchall()]
    
    loyalty_members = []
    tiers = ['Basic', 'Silver', 'Gold', 'Platinum']
    weights = [0.6, 0.25, 0.1, 0.05]  # 60% Basic, 25% Silver, etc.
    
    for customer_id in member_ids:
        tier = random.choices(tiers, weights=weights)[0]
        base_points = {'Basic': 500, 'Silver': 2000, 'Gold': 5000, 'Platinum': 10000}[tier]
        
        loyalty_members.append((
            customer_id,
            random.randint(base_points, base_points * 3),  # current balance
            tier,
            fake.date_between(start_date='-4y', end_date='today'),
            fake.date_between(start_date='-30d', end_date='today'),
            random.randint(base_points * 2, base_points * 10),  # lifetime earned
            random.randint(base_points, base_points * 5)  # lifetime redeemed
        ))
    
    cursor.executemany(
        """INSERT INTO loyalty_program (customer_id, points_balance, membership_tier, 
           join_date, last_activity_date, lifetime_points_earned, lifetime_points_redeemed) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        loyalty_members
    )
    conn.commit()

def create_inventory():
    print("Creating inventory records...")
    cursor.execute("SELECT product_id FROM products")
    product_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT store_id FROM stores")
    store_ids = [row[0] for row in cursor.fetchall()]
    
    inventory = []
    for store_id in store_ids:
        for product_id in random.sample(product_ids, int(len(product_ids) * 0.7)):  # 70% of products per store
            inventory.append((
                product_id,
                store_id,
                random.randint(0, 200),
                random.randint(5, 50),
                fake.date_between(start_date='-30d', end_date='today'),
                f"Aisle {random.randint(1, 20)}",
                f"Shelf {random.choice('ABCDEF')}"
            ))
    
    # Batch insert for performance
    batch_size = 1000
    for i in range(0, len(inventory), batch_size):
        cursor.executemany(
            """INSERT INTO inventory (product_id, store_id, quantity_in_stock, 
               reorder_level, last_restocked, aisle_location, shelf_location) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            inventory[i:i+batch_size]
        )
        conn.commit()
        print(f"Inserted inventory for {min(i+batch_size, len(inventory))}/{len(inventory)} product-store combinations")

def create_sales_data():
    print("Creating sales data...")
    cursor.execute("SELECT store_id FROM stores")
    store_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT employee_id, store_id FROM employees WHERE store_id IS NOT NULL")
    cashiers = {row[1]: [] for row in cursor.fetchall()}
    for row in cursor.fetchall():
        cashiers[row[1]].append(row[0])
    
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id FROM products")
    product_ids = [row[0] for row in cursor.fetchall()]
    
    payment_methods = ['Cash', 'Credit Card', 'Debit Card', 'SNAP', 'WIC']
    
    # Create sales for the past 2 years
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now()
    
    sales_count = 0
    sale_items_count = 0
    
    for store_id in store_ids:
        print(f"Creating sales for store {store_id}")
        store_sales = MAX_SALES_PER_STORE_PER_YEAR // 365 * 730  # 2 years
        
        for _ in range(store_sales):
            sale_date = fake.date_time_between(start_date=start_date, end_date=end_date)
            customer_id = random.choice(customer_ids) if random.random() < 0.7 else None  # 70% have customer ID
            employee_id = random.choice(cashiers.get(store_id, []))
            
            # Create sale
            subtotal = round(random.uniform(10, 200), 2)
            tax = round(subtotal * 0.08, 2)  # 8% tax
            total = subtotal + tax
            
            cursor.execute(
                """INSERT INTO sales (customer_id, store_id, employee_id, sale_date, 
                   subtotal, tax, total, payment_method, loyalty_points_earned, loyalty_points_redeemed) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    customer_id,
                    store_id,
                    employee_id,
                    sale_date,
                    subtotal,
                    tax,
                    total,
                    random.choice(payment_methods),
                    random.randint(1, 20) if customer_id and random.random() < 0.3 else 0,
                    random.randint(10, 100) if customer_id and random.random() < 0.2 else 0
                )
            )
            sale_id = cursor.lastrowid
            sales_count += 1
            
            # Create sale items (3-8 items per sale)
            num_items = random.randint(3, 8)
            for _ in range(num_items):
                product_id = random.choice(product_ids)
                quantity = random.randint(1, 3)
                cursor.execute(
                    "SELECT unit_price FROM products WHERE product_id = %s",
                    (product_id,)
                )
                unit_price = float(cursor.fetchone()[0])
                discount = round(unit_price * random.uniform(0, 0.3), 2) if random.random() < 0.2 else 0  # 20% chance of discount
                total_price = (unit_price - discount) * quantity
                
                cursor.execute(
                    """INSERT INTO sale_items (sale_id, product_id, quantity, 
                       unit_price, discount, total_price) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (sale_id, product_id, quantity, unit_price, discount, total_price)
                )
                sale_items_count += 1
            
            if sales_count % 1000 == 0:
                conn.commit()
                print(f"Created {sales_count} sales with {sale_items_count} items")
    
    conn.commit()
    print(f"Finished creating {sales_count} sales with {sale_items_count} items")

def create_purchases():
    print("Creating purchase orders...")
    cursor.execute("SELECT supplier_id FROM suppliers")
    supplier_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT employee_id FROM employees WHERE department_id = 5")  # Operations
    employee_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT product_id FROM products")
    product_ids = [row[0] for row in cursor.fetchall()]
    
    payment_terms = ['Net 30', 'Net 15', 'Due on Receipt', '50% Advance']
    
    # Create purchases for the past 2 years
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now()
    
    purchases_count = 0
    purchase_items_count = 0
    
    for _ in range(5000):  # 5,000 purchase orders
        supplier_id = random.choice(supplier_ids)
        order_date = fake.date_time_between(start_date=start_date, end_date=end_date)
        expected_delivery_date = order_date + timedelta(days=random.randint(1, 14))
        actual_delivery_date = expected_delivery_date + timedelta(days=random.randint(-1, 3))
        status = random.choices(
            ['Pending', 'Shipped', 'Delivered', 'Cancelled'],
            weights=[0.1, 0.2, 0.65, 0.05]
        )[0]
        approved_by = random.choice(employee_ids)
        
        cursor.execute(
            """INSERT INTO purchases (supplier_id, order_date, expected_delivery_date, 
               actual_delivery_date, status, total_cost, payment_terms, approved_by) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                supplier_id,
                order_date,
                expected_delivery_date,
                actual_delivery_date if status in ['Delivered', 'Shipped'] else None,
                status,
                0,  # Will be updated after items are added
                random.choice(payment_terms),
                approved_by
            )
        )
        purchase_id = cursor.lastrowid
        purchases_count += 1
        
        # Create purchase items (5-20 items per order)
        num_items = random.randint(5, 20)
        total_cost = 0
        
        for _ in range(num_items):
            product_id = random.choice(product_ids)
            quantity = random.randint(10, 100)
            cursor.execute(
                "SELECT cost FROM products WHERE product_id = %s",
                (product_id,)
            )
            unit_cost = float(cursor.fetchone()[0])
            item_cost = unit_cost * quantity
            total_cost += item_cost
            
            cursor.execute(
                """INSERT INTO purchase_items (purchase_id, product_id, quantity, 
                   unit_cost, total_cost) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (purchase_id, product_id, quantity, unit_cost, item_cost)
            )
            purchase_items_count += 1
        
        # Update purchase total
        cursor.execute(
            "UPDATE purchases SET total_cost = %s WHERE purchase_id = %s",
            (total_cost, purchase_id)
        )
        
        if purchases_count % 500 == 0:
            conn.commit()
            print(f"Created {purchases_count} purchases with {purchase_items_count} items")
    
    conn.commit()
    print(f"Finished creating {purchases_count} purchases with {purchases_count} items")

def create_customer_feedback():
    print("Creating customer feedback...")
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT store_id FROM stores")
    store_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT employee_id FROM employees WHERE department_id = 9")  # Customer Service
    employee_ids = [row[0] for row in cursor.fetchall()]
    
    feedback_types = ['Compliment', 'Complaint', 'Suggestion', 'Question']
    
    feedbacks = []
    for _ in range(2000):  # 2,000 feedback entries
        feedback_date = fake.date_time_between(start_date='-1y', end_date='now')
        feedbacks.append((
            random.choice(customer_ids),
            random.choice(store_ids),
            random.choice(feedback_types),
            fake.paragraph(nb_sentences=2),
            feedback_date,
            random.randint(1, 5),
            random.choices(['New', 'In Review', 'Resolved', 'Follow Up'], weights=[0.2, 0.3, 0.4, 0.1])[0],
            random.choice(employee_ids) if random.random() < 0.7 else None,
            fake.paragraph(nb_sentences=1) if random.random() < 0.5 else None,
            feedback_date + timedelta(days=random.randint(1, 7)) if random.random() < 0.4 else None
        ))
    
    cursor.executemany(
        """INSERT INTO customer_feedback (customer_id, store_id, feedback_type, 
           feedback_text, submission_date, rating, status, assigned_to, 
           resolution_notes, resolution_date) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        feedbacks
    )
    conn.commit()

def create_marketing_campaigns():
    print("Creating marketing campaigns...")
    channels = ['Email', 'Social Media', 'In-Store', 'Direct Mail', 'SMS']
    statuses = ['Planning', 'Active', 'Completed', 'Cancelled']
    
    campaigns = []
    for i in range(50):  # 50 campaigns
        start_date = fake.date_between(start_date='-2y', end_date='+3M')
        end_date = start_date + timedelta(days=random.randint(7, 90))
        campaigns.append((
            f"{fake.word().capitalize()} {fake.word().capitalize()} Campaign",
            fake.paragraph(nb_sentences=3),
            start_date,
            end_date,
            random.randint(1000, 50000),
            random.choice(['New Customers', 'Loyalty Members', 'All Customers', 'Local Community']),
            random.choice(channels),
            random.choices(statuses, weights=[0.1, 0.3, 0.5, 0.1])[0]
        ))
    
    cursor.executemany(
        """INSERT INTO marketing_campaigns (campaign_name, description, start_date, 
           end_date, budget, target_audience, channel, status) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        campaigns
    )
    conn.commit()

if __name__ == "__main__":
    try:
        # Create tables in proper order
        create_departments()
        create_stores()
        create_product_categories()
        create_suppliers()
        create_products()
        create_employees()
        create_customers()
        create_loyalty_program()
        create_inventory()
        create_sales_data()
        create_purchases()
        create_customer_feedback()
        create_marketing_campaigns()
        
        print("Database population complete!")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()