from faker import Faker
import awswrangler as wr
import json
import logging
import niafaker as nfake
import pandas as pd
import random
import uuid


logging.basicConfig(
    filename="temu_event_simulation.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger()

def generate_and_upload_events(num_events: int, json_path: str, s3_path: str):
    """
    Generates simulated event log data and uploads it to S3 in Parquet format.

    Parameters:
    - num_events (int): Number of events to generate.
    - json_path (str): Path to the JSON configuration file.
    - s3_path (str): S3 path where the Parquet file will be uploaded.
    """
    
    # Define values
    fake = Faker()
    simulated_data = []

    with open(json_path) as f:
      config = json.load(f)

    logger.info(f"JSON file read: {json_path}")

    country = config["country"]
    platform_type = config["platform_type"]
    number_prefix_opt = config["number_prefix_opt"]
    events = config["all_events"]
    total_amount_events = config["total_amount_events"]
    payment_method_events = config["payment_method_events"]
    payment_method_type = config["payment_method_type"]
    payment_status_captured_events = config["payment_status_captured_events"]
    payment_status_refunded_events = config["payment_status_refunded_events"]
    carrier_events = config["carrier_events"]
    carrier_type = config["carrier_type"]


    # Generates dataset based on column config
    for i in range(num_events):
      event_type = random.choice(events)

      # Total_Amount
      if event_type in total_amount_events:
        total_amount = random.randint(1_000, 10_000_000)

      else:
        total_amount = None

      # Payment_Method
      if event_type in payment_method_events:
        payment_method = random.choice(payment_method_type)

      else:
        payment_method = None

      # Payment_Status
      if event_type in payment_status_captured_events:
        payment_status = "CAPTURED"

      elif event_type in payment_status_refunded_events:
        payment_status = "REFUNDED"

      else:
        payment_status = None

      # Carrier
      if event_type in carrier_events:
        carrier = random.choice(carrier_type)

      else:
        carrier = None

      # Tracking_Number
      if carrier != None:
        tracking_number = fake.numerify("TRK" + '######')

      else:
        tracking_number = None

      # Error
      latency_ms = (random.randint(0, 300_000)
                    if random.random() < 0.95
                    else random.randint(300_001, 600_000))

      if latency_ms > 300000 or isinstance(latency_ms, int) == False:
        error_code = "INVALID LATENCY"

      else:
        error_code = None

      temp_data = {
          "event_ts": fake.date_time_between_dates(datetime_start="-4w",
                                                  datetime_end="now"),
          "event_id": fake.numerify("EV-" + '###########'),
          "event_type": event_type,
          "customer_id": str(uuid.uuid4()),
          "name": nfake.generate_name(country),
          "phone_number": fake.numerify(random.choice(number_prefix_opt) +
                                        '########'),
          "address": nfake.generate_address(country),
          "email": nfake.generate_email(),
          "platform": random.choice(platform_type),
          "total_amount": total_amount,
          "payment_status": payment_status,
          "payment_method": payment_method,
          "carrier": carrier,
          "tracking_number": tracking_number,
          "latency_ms": latency_ms,
          "error_code": error_code}

      simulated_data.append(temp_data)
      logger.info(f"Simulated data created.")

    df = pd.DataFrame(simulated_data)
    wr.s3.to_parquet(
        df=df,
        path=s3_path,
    )
    logger.info(f"Parquet file uploaded to S3 at {s3_path}.")
    