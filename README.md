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

---

## What This System Does

- Provisions AWS infrastructure using **Terraform**
- Creates an **EC2 instance** with least-privilege IAM access
- Runs a **Python event generator** on the instance
- Generates **400,000–500,000 events per run**
- Writes **Parquet event logs** to **Amazon S3**
- Produces **append-only, time-sequenced datasets**

---

## High-Level Architecture

![Architecture Diagram](image/infra.png)

