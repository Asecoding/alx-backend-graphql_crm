#!/usr/bin/env python3

import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup logging
log_path = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=log_path, level=logging.INFO)

# GraphQL transport setup
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date range
today = datetime.date.today()
seven_days_ago = today - datetime.timedelta(days=7)

# GraphQL query
query = gql("""
query GetRecentOrders($startDate: Date!) {
  orders(orderDate_Gte: $startDate, status: "PENDING") {
    id
    customer {
      email
    }
  }
}
""")

# Execute query
try:
    result = client.execute(query, variable_values={"startDate": seven_days_ago.isoformat()})
    orders = result.get("orders", [])

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for order in orders:
        log_entry = f"[{timestamp}] Order ID: {order['id']}, Email: {order['customer']['email']}"
        logging.info(log_entry)

    print("Order reminders processed!")

except Exception as e:
    logging.error(f"[{timestamp}] Error fetching orders: {e}")
    print("Failed to process order reminders.")

