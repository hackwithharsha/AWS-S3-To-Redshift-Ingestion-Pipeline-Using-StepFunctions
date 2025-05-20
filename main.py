import csv
import uuid
import random
from faker import Faker
from datetime import datetime
from tqdm import tqdm

fake = Faker()

# Estimate how many rows to generate for ~5MB (50 * 1024 * 1024 bytes)
# Assuming each row is ~70 bytes on average
target_size_bytes = 50 * 1024 * 1024
avg_row_size_bytes = 70
num_rows = target_size_bytes // avg_row_size_bytes

currencies = ['USD', 'EUR', 'GBP', 'INR', 'CAD', 'AUD']

with open("customer.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["order_id", "order_date", "country", "amount", "currency"])

    for _ in tqdm(range(int(num_rows))):
        order_id = str(uuid.uuid4())
        order_date = fake.date_between(start_date="-2y", end_date="today").isoformat()
        country = fake.country()
        amount = round(random.uniform(10, 10000), 2)
        currency = random.choice(currencies)

        writer.writerow([order_id, order_date, country, amount, currency])
