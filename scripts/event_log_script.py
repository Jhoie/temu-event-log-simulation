import json
import logging
import random
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import awswrangler as wr
import config_variables as cv
import niafaker as nfake
import pandas as pd
from botocore.exceptions import ClientError
from faker import Faker

logging.basicConfig(
    filename="scripts/temu_event_simulation.log",
    level=logging.INFO,
    format="%(asctime)s || %(levelname)s || %(message)s")
logger = logging.getLogger()


def read_json(json_path: str):
    """
    Reads a JSON configuration file that determines column values.

    Parameter:
    - json_path (str): Path to the JSON column configuration file.
    Returns:
    - config (dict): Dictionary containing the column configuration.
    """
    try:
        with open(json_path) as f:
            config = json.load(f)

        logger.info(f"JSON file read: {json_path}")
        return config

    except FileNotFoundError:
        logger.error(f"File not found: {json_path}")
        raise

    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {json_path}")
        raise

    except Exception as e:
        logger.error(f"An unexpected error occurred while reading JSON file:\
                      {json_path}. Error {e}")
        raise


def generate_events(config: dict, num_events: int):
    """
    Generates simulated event log data based on the provided configuration.

    Parameters:
    - config (dict): Dictionary containing the column configuration.
    - num_events (int): Number of events to generate.
    Returns:
    - df: Pandas DataFrame representing the simulated event log data.
    """

    try:
        # Define values
        fake = Faker()
        simulated_data = []

        country = config["country"]
        platform_type = config["platform_type"]
        number_prefix_opt = config["number_prefix_opt"]
        events = config["all_events"]
        total_amount_events = config["total_amount_events"]
        payment_method_events = config["payment_method_events"]
        payment_method_type = config["payment_method_type"]
        payment_status_captured_events = \
            config["payment_status_captured_events"]
        payment_status_refunded_events = \
            config["payment_status_refunded_events"]
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
            if carrier is not None:
                tracking_number = fake.numerify("TRK" + '######')

            else:
                tracking_number = None

            # Error
            latency_ms = (random.randint(0, 300_000)
                          if random.random() < 0.95
                          else random.randint(300_001, 600_000))

            if latency_ms > 300000:
                error_code = "INVALID LATENCY"

            else:
                error_code = None

            temp_data = {
                "event_ts": fake.date_time_between_dates(
                    datetime_start="-4w", datetime_end="now"
                    ),
                "event_id": fake.numerify("EV-" + '###########'),
                "event_type": event_type,
                "customer_id": str(uuid.uuid4()),
                "name": nfake.generate_name(country),
                "phone_number": fake.numerify(
                    random.choice(number_prefix_opt) +
                    '########'
                    ),
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

        df = pd.DataFrame(simulated_data)
        logger.info(f"Simulated data created. Number of events: {len(df)}")
        return df

    except Exception as e:
        logger.error(f"An error occurred during event generation. {e}")
        raise


def write_chunk_to_s3_parquet(
        df: pd.DataFrame, s3_path: str, run_id: str, chunk_counter: int):
    """
    Writes a chunk of the number of events requested to a parquet file,
    instead of writing the entire dataset to memory at once and risk
    failure. This function is called iteratively for each chunk
    until all events are generated and written to parquet.

    Parameters:
    - df (pd.DataFrame): DataFrame chunk to write.
    - s3_path (str): S3 path where the parquet file will be saved.
    - run_id (str): Unique identifier for the current run.
    - chunk_counter (int): Counter of the current chunk.

    Returns:
    - parquet_path (str): The S3 path where the parquet file was uploaded.
    example output:
    s3://temu-event-log-simulation-terraform-bucket/run_id=20260205T101500Z/part_001.parquet
    """
    try:
        parquet_path = (f"{s3_path.rstrip('/')}/run_id={run_id}/"
                        f"part_{chunk_counter:03d}.parquet")

        wr.s3.to_parquet(
            df=df,
            path=parquet_path)

        logger.info(f"Writing chunk to file: {parquet_path}. "
                    f"Chunk size: {len(df)}")
        return parquet_path

    except ClientError as e:
        logger.error(f"AWS ClientError occurred during upload to S3. {e}")
        raise

    except Exception as e:
        logger.error(f"An error occurred while writing chunk {chunk_counter}"
                     f" to parquet. {e}")
        raise


def split_events_into_chunks(config: dict, num_events: int, s3_path: str):
    """
    Splits the requested number of events into smaller chunks for processing.

    Parameters:
    - config (dict): Dictionary containing the column configuration.
    - num_events (int): Total number of events to generate.
    - s3_path (str): S3 path where the parquet files will be saved.
    """
    try:
        chunk_size = 500_000
        remaining = num_events

        if num_events <= 0:
            raise ValueError(f"num_events must be > 0. Received: {num_events}")

        run_id = datetime.now(ZoneInfo("Africa/Lagos"))\
            .strftime("%Y%m%dT%H%M%S")
        logger.info(f"Starting run_id={run_id} and num_events={num_events}")

        chunk_counter = 0
        while remaining > 0:
            current_chunk_size = min(chunk_size, remaining)

            df_chunk = generate_events(config, current_chunk_size)
            parquet_path = write_chunk_to_s3_parquet(
                df_chunk, s3_path, run_id, chunk_counter)

            remaining -= current_chunk_size
            logger.info(
              f"Chunk {chunk_counter:03d} of run_id {run_id} completed."
              f" This chunk generated {len(df_chunk)} rows(events) in "
              f" {parquet_path} and has {remaining} left"
              )

            chunk_counter += 1
        logger.info(f"Chunking complete run_id={run_id}. {num_events} events"
                    f"generated in {chunk_counter} chunks")

    except Exception as e:
        logger.error(f"An error occurred while splitting events into chunks."
                     f" {e}")
        raise


config = read_json(cv.json_path)
split_events_into_chunks(config, cv.num_events, cv.s3_path)
