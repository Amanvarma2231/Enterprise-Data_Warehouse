# RetailSphere Enterprise Data Governance Framework

## 1. Information Security & Data Classification Policy

RetailSphere enforces a 4-tier data classification hierarchy aligned with GDPR, CCPA, and ISO/IEC 27001 standards:

| Classification Tier | Definition & Scope | Examples | Access Controls & Encryption |
| :--- | :--- | :--- | :--- |
| **PUBLIC** | Information that can be freely shared externally without risk to the enterprise. | Product Catalog Names, Store Locations, Public Pricing | Unrestricted Read Access; SSL/TLS in transit |
| **INTERNAL** | Standard operational data intended for internal staff and analytics workloads. | Aggregated Sales, Store IDs, SKU metadata, General Metrics | Role-Based Access Control (RBAC); corporate network / VPN |
| **CONFIDENTIAL (PII)** | Personally Identifiable Information (PII) that directly identifies individual humans. | Customer First/Last Names, Email Addresses, Phone Numbers | Column-level encryption, Dynamic Data Masking, strict RBAC |
| **RESTRICTED** | Highly sensitive proprietary commercial metrics and secret credentials. | Unit Procurement Cost, Bank Authorization Hashes, Margin Secrets | Column-level hashing, multi-factor authorization, immutable audit logs |

---

## 2. PII Data Masking Standards (SQL Implementation)

For non-privileged analytical users, PII fields must be dynamically masked:

```sql
-- Dynamic Email Masking
CREATE VIEW analytics.v_dim_customer AS
SELECT 
    customer_key,
    customer_id,
    SUBSTRING(first_name, 1, 1) || '****' AS first_name,
    SUBSTRING(last_name, 1, 1) || '****' AS last_name,
    SUBSTRING(email, 1, 2) || '****@' || SPLIT_PART(email, '@', 2) AS masked_email,
    '***-***-' || RIGHT(phone, 4) AS masked_phone,
    city,
    state,
    country,
    segment
FROM warehouse.dim_customer;
```

---

## 3. Data Quality SLA & Quarantine Rules

- **Zero-Tolerance Rules (Quarantine Trigger):** Any record with a `NULL` Primary Key, orphaned Foreign Key, or negative quantity is immediately redirected to `data/quarantine/`.
- **Warning Rules (Audit Flag):** Missing optional attributes (postal code, store manager) trigger metric logs but do not block pipeline progression.
