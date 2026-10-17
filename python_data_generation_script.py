import random
from datetime import datetime, timedelta
import mysql.connector
from faker import Faker

# Configure database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'winwin19',  # Replace with your MySQL root password
    'database': 'harborwing_air',
    'port': 3306
}

# Initialize Faker with a fixed seed for repeatable data generation
faker = Faker()
SEED = 42
Faker.seed(SEED)
random.seed(SEED)


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def generate_synthetic_data():
    conn = connect_db()
    cursor = conn.cursor()

    print("--- Starting Synthetic Data Generation ---")

    # Disable Foreign Key checks temporarily during clean setup
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    # Clear existing records
    tables = [
        "reservation_leg_link", "reservation_payment_link", "flight_cost",
        "flight_leg", "flight_schedule", "calendar_date", "payment",
        "reservation", "airport", "passenger", "booking_agent"
    ]
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()

    # 1. Populate booking_agent (50 rows)
    print("Populating booking_agent...")
    agent_ids = []
    for _ in range(50):
        name = faker.company()
        details = faker.catch_phrase()
        cursor.execute(
            "INSERT INTO booking_agent (name, additional_details) VALUES (%s, %s)",
            (name, details)
        )
        agent_ids.append(cursor.lastrowid)

    # 2. Populate passenger (50 rows)
    print("Populating passenger...")
    passenger_ids = []
    for _ in range(50):
        first_name = faker.first_name()
        second_name = faker.first_name() if random.choice([True, False]) else None
        last_name = faker.last_name()
        phone = faker.numerify(text="###-###-####")
        email = faker.unique.email()
        address = faker.street_address()
        city = faker.city()
        state = faker.state()
        country = faker.country()
        details = faker.text(max_nb_chars=50)

        cursor.execute("""
            INSERT INTO passenger (first_name, second_name, last_name, phone_number,
                                 email_address, address_lines, city, state_province_county,
                                 country, other_details)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, second_name, last_name, phone, email, address, city, state, country, details))
        passenger_ids.append(cursor.lastrowid)

    # 3. Populate airport (50 rows)
    print("Populating airport...")
    airport_codes = []
    used_codes = set()
    for _ in range(50):
        while True:
            code = faker.unique.lexify(text='???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            if code not in used_codes:
                used_codes.add(code)
                break
        name = f"{faker.city()} Regional Airport"
        location = faker.city()
        details = f"Terminal count: {random.randint(1, 5)}"
        
        cursor.execute("""
            INSERT INTO airport (airport_code, name, location, other_details)
            VALUES (%s, %s, %s, %s)
        """, (code, name, location, details))
        airport_codes.append(code)

    # 4. Populate reservation (50 rows)
    print("Populating reservation...")
    reservation_ids = []
    status_codes = ['CONFIRMED', 'CANCELLED', 'PENDING']
    ticket_types = ['ONE_WAY', 'ROUND_TRIP']
    travel_classes = ['ECONOMY', 'BUSINESS', 'FIRST']

    for _ in range(50):
        p_id = random.choice(passenger_ids)
        a_id = random.choice(agent_ids) if random.choice([True, False]) else None
        status = random.choice(status_codes)
        ticket = random.choice(ticket_types)
        travel_class = random.choice(travel_classes)
        created_at = faker.date_time_between(start_date="-1y", end_date="now")
        party_size = random.randint(1, 6)

        cursor.execute("""
            INSERT INTO reservation (passenger_id, agent_id, reservation_status_code,
                                    ticket_type_code, travel_class_code, creation_timestamp,
                                    number_in_party)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (p_id, a_id, status, ticket, travel_class, created_at, party_size))
        reservation_ids.append(cursor.lastrowid)

    # 5. Populate payment (50 rows)
    print("Populating payment...")
    payment_ids = []
    payment_statuses = ['COMPLETED', 'REFUNDED', 'FAILED']

    for _ in range(50):
        status = random.choice(payment_statuses)
        p_date = faker.date_time_between(start_date="-1y", end_date="now")
        amount = round(random.uniform(50.0, 1500.0), 2)

        cursor.execute("""
            INSERT INTO payment (payment_status_code, payment_date, payment_amount)
            VALUES (%s, %s, %s)
        """, (status, p_date, amount))
        payment_ids.append(cursor.lastrowid)

    # 6. Populate calendar_date (50 unique sequential dates)
    print("Populating calendar_date...")
    calendar_dates = []
    start_date = datetime(2026, 1, 1).date()
    for i in range(50):
        current_date = start_date + timedelta(days=i)
        day_of_month = current_date.day
        is_business = current_date.weekday() < 5

        cursor.execute("""
            INSERT INTO calendar_date (calendar_date, day_of_the_month, business_day_indicator)
            VALUES (%s, %s, %s)
        """, (current_date, day_of_month, is_business))
        calendar_dates.append(current_date)

    # 7. Populate flight_schedule (50 rows)
    print("Populating flight_schedule...")
    flight_numbers = []
    aircraft_types = ['A320', 'B737', 'E190', 'ATR72']

    for i in range(50):
        flight_num = f"HW{100 + i}"
        airline_code = "HW"
        aircraft = random.choice(aircraft_types)
        
        origin = random.choice(airport_codes)
        dest = random.choice([a for a in airport_codes if a != origin])

        dep_time = faker.date_time_between(start_date="now", end_date="+30d")
        arr_time = dep_time + timedelta(hours=random.randint(1, 5))

        cursor.execute("""
            INSERT INTO flight_schedule (flight_number, airline_code, usual_aircraft_type_code,
                                         origin_airport_code, destination_airport_code,
                                         scheduled_departure_time, scheduled_arrival_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (flight_num, airline_code, aircraft, origin, dest, dep_time, arr_time))
        flight_numbers.append(flight_num)

    # 8. Populate flight_leg (50 rows)
    print("Populating flight_leg...")
    leg_ids = []
    for _ in range(50):
        f_num = random.choice(flight_numbers)
        origin = random.choice(airport_codes)
        dest = random.choice([a for a in airport_codes if a != origin])

        actual_dep = faker.date_time_between(start_date="-30d", end_date="now")
        actual_arr = actual_dep + timedelta(hours=random.randint(1, 5))

        cursor.execute("""
            INSERT INTO flight_leg (flight_number, origin_airport_code, destination_airport_code,
                                    actual_departure_time, actual_arrival_time)
            VALUES (%s, %s, %s, %s, %s)
        """, (f_num, origin, dest, actual_dep, actual_arr))
        leg_ids.append(cursor.lastrowid)

    # 9. Populate flight_cost (50 rows with composite primary keys)
    print("Populating flight_cost...")
    cost_keys = set()
    for _ in range(50):
        while True:
            f_num = random.choice(flight_numbers)
            ac_type = random.choice(aircraft_types)
            valid_from = random.choice(calendar_dates[:25])
            if (f_num, ac_type, valid_from) not in cost_keys:
                cost_keys.add((f_num, ac_type, valid_from))
                break

        valid_to = random.choice([d for d in calendar_dates if d >= valid_from])
        cost = round(random.uniform(100.0, 800.0), 2)

        cursor.execute("""
            INSERT INTO flight_cost (flight_number, aircraft_type_code, valid_from_date,
                                     valid_to_date, cost_amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (f_num, ac_type, valid_from, valid_to, cost))

    # 10. Populate reservation_payment_link (50 unique link pairs)
    print("Populating reservation_payment_link...")
    res_pay_pairs = set()
    for _ in range(50):
        while True:
            r_id = random.choice(reservation_ids)
            p_id = random.choice(payment_ids)
            if (r_id, p_id) not in res_pay_pairs:
                res_pay_pairs.add((r_id, p_id))
                break

        cursor.execute("""
            INSERT INTO reservation_payment_link (reservation_id, payment_id)
            VALUES (%s, %s)
        """, (r_id, p_id))

    # 11. Populate reservation_leg_link (50 unique link pairs)
    print("Populating reservation_leg_link...")
    res_leg_pairs = set()
    for _ in range(50):
        while True:
            r_id = random.choice(reservation_ids)
            l_id = random.choice(leg_ids)
            if (r_id, l_id) not in res_leg_pairs:
                res_leg_pairs.add((r_id, l_id))
                break

        cursor.execute("""
            INSERT INTO reservation_leg_link (reservation_id, leg_id)
            VALUES (%s, %s)
        """, (r_id, l_id))

    conn.commit()
    print("\n--- Data Generation Completed Successfully! ---\n")

    # Verification: Display Row Count for Every Table
    print("=" * 40)
    print("      ROW COUNT VERIFICATION METRICS     ")
    print("=" * 40)

    all_tables = [
        "booking_agent", "passenger", "airport", "reservation",
        "payment", "calendar_date", "flight_schedule", "flight_leg",
        "flight_cost", "reservation_payment_link", "reservation_leg_link"
    ]

    for table in all_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"Table: {table:<25} | Row Count: {count}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    generate_synthetic_data()