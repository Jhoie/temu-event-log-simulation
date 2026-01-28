# Temu Event Log Simulation
## Overview

This project simulates high-volume e-commerce event logs for **Temu’s Nigeria launch** using cloud-native infrastructure and realistic customer behavior.

The system provisions AWS infrastructure with **Terraform**, runs a **Python-based event generator on an EC2 instance**, and writes **append-only event logs to Amazon S3**. These logs are designed to validate downstream ETL pipelines, analytics models, and scaling assumptions *before real production traffic exists*.

This is a **production-style data platform simulation**, not a tutorial project.


## Business Context

When Temu expanded to Nigeria, the data platform engineering team needed to test:

- Event ingestion at scale  
- Order and payment lifecycle modeling  
- Reliability and failure scenarios  
- Data partitioning strategies for analytics  

Rather than waiting for live traffic, this system **synthetically generates realistic Nigerian e-commerce activity**, closely mirroring how users interact across web and mobile platforms.

## What This System Does

- Provisions AWS infrastructure using **Terraform**
- Creates an **EC2 instance** with least-privilege IAM access
- Runs a **Python event generator** on the instance
- Generates **400,000–500,000 events per run**
- Writes **Parquet event logs** to **Amazon S3**
- Produces **append-only, time-sequenced datasets**

## High-Level Architecture

![Architecture Diagram](image/infra.png)


## Infrastructure Stack

### Provisioned with Terraform

- **Amazon S3**
  - Stores generated event logs
- **Amazon EC2**
  - Executes the Python event generator
- **IAM**
  - Least-privilege permissions allowing EC2 to write to S3

Infrastructure is fully reproducible using Terraform.

## Event Model

**Grain**

- **1 row = 1 event**
- Each row represents a single action at a specific timestamp

## Event Types

The generator produces the following **11 event types**:

### User Lifecycle
- `OPEN`
- `USER_LOGIN`

### Engagement
- `PRODUCT_VIEW`
- `ADD_TO_CART`

### Checkout & Payments
- `CHECKOUT_STARTED`
- `PAYMENT_AUTHORIZED`
- `PAYMENT_FAILED`

### Orders & Fulfillment
- `ORDER_PLACED`
- `PACKED`
- `SHIPPED`
- `DELIVERED`

## Event Log Schema

### Core Columns

| Column | Type | Description |
|------|-----|-------------|
| event_id | UUID | Unique event identifier |
| event_ts | TIMESTAMP | When the event occurred |
| event_type | STRING | Type of event |
| customer_id | STRING | Unique Temu customer |
| name | STRING | Customer name |
| phone_number | STRING | Customer phone number |
| address | STRING | Customer address |
| email | STRING | Customer email |
| platform | STRING | ANDRIOD, IOS, WEB |
| latency_ms | INTEGER | Simulated platform response time |
| error_code | STRING | Error flag when latency exceeds threshold |

## Conditional Columns

These fields are populated **only when relevant**, based on `event_type`.

| Column | Description | Condition |
|------|-------------|-----------|
| total_amount | Order/payment value | CHECKOUT_STARTED, PAYMENT_AUTHORIZED, PAYMENT_FAILED, ORDER_PLACED |
| payment_method | CARD, USSD, TRANSFER, PAYPAL | PAYMENT_AUTHORIZED, ORDER_PLACED |
| payment_status | CAPTURED or REFUNDED | Derived from payment events |
| carrier | Delivery company | PAYMENT_AUTHORIZED → DELIVERED |
| tracking_number | Shipment ID | Only when carrier exists |

### Payment Status Logic

- `CAPTURED` → `CHECKOUT_STARTED`, `PAYMENT_AUTHORIZED`, `ORDER_PLACED`
- `REFUNDED` → `PAYMENT_FAILED`
- `None` → All other events

## Reliability Simulation

- `latency_ms` is generated for **every event**
- `error_code = "INVALID LATENCY"` when latency exceeds the configured threshold
- Otherwise, `error_code` is `None`



