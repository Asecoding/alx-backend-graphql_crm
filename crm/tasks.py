from celery import shared_task
import requests
from datetime import datetime

@shared_task
def generate_crm_report():
    query = """
    query {
      totalCustomers
      totalOrders
      totalRevenue
    }
    """
    try:
        response = requests.post("http://localhost:8000/graphql", json={"query": query})
        data = response.json()["data"]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - Report: {data['totalCustomers']} customers, {data['totalOrders']} orders, {data['totalRevenue']} revenue\n"

        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(log_line)

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{datetime.now()} - ERROR: {str(e)}\n")

