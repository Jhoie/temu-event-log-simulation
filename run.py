from event_log_script import generate_and_upload_events

NUM_EVENTS = 400_000
JSON_PATH = "temu_column_config.json"
S3_PATH = "s3://temu-event-log-simulation-terraform-bucket/temu_dataset.parquet"


result = generate_and_upload_events(
    num_events=NUM_EVENTS,
    json_path=JSON_PATH,
    s3_path=S3_PATH
)
