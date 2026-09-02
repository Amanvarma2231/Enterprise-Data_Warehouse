{{ config(materialized='table') }}

SELECT * FROM warehouse.dim_date
