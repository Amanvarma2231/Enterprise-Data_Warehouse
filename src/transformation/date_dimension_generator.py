"""
Date Dimension Generator for Enterprise Data Warehouse
Populates conformed dim_date table across multi-year horizon
"""

from datetime import date, timedelta
import pandas as pd

from src.config import DATE_DIM_START_YEAR, DATE_DIM_END_YEAR


def generate_date_dimension_df(
    start_year: int = DATE_DIM_START_YEAR,
    end_year: int = DATE_DIM_END_YEAR
) -> pd.DataFrame:
    """Generate a comprehensive conformed date dimension dataframe."""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    
    current_date = start_date
    records = []
    
    # Standard holidays (New Year, Republic Day, Independence Day, Gandhi Jayanti, Christmas)
    standard_holidays = {
        (1, 1): "New Year's Day",
        (1, 26): "Republic Day",
        (8, 15): "Independence Day",
        (10, 2): "Gandhi Jayanti",
        (12, 25): "Christmas Day",
    }
    
    while current_date <= end_date:
        date_key = int(current_date.strftime("%Y%m%d"))
        year = current_date.year
        month = current_date.month
        day = current_date.day
        quarter = (month - 1) // 3 + 1
        day_of_week = current_date.isoweekday() # 1=Mon, 7=Sun
        is_weekend = day_of_week in (6, 7)
        is_holiday = (month, day) in standard_holidays
        
        # Indian Financial Year starts in April
        if month >= 4:
            fiscal_year = year + 1
            fiscal_quarter = f"FY{str(fiscal_year)[2:]}-Q{quarter - 1}"
        else:
            fiscal_year = year
            fiscal_quarter = f"FY{str(fiscal_year)[2:]}-Q4"
            
        records.append({
            "date_key": date_key,
            "full_date": current_date.strftime("%Y-%m-%d"),
            "day_of_month": day,
            "month_number": month,
            "month_name": current_date.strftime("%B"),
            "month_short_name": current_date.strftime("%b"),
            "quarter_number": quarter,
            "quarter_name": f"Q{quarter}",
            "year_number": year,
            "year_month": current_date.strftime("%Y-%m"),
            "day_of_week": day_of_week,
            "day_name": current_date.strftime("%A"),
            "week_of_year": int(current_date.strftime("%V")),
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "fiscal_year": fiscal_year,
            "fiscal_quarter": fiscal_quarter,
        })
        current_date += timedelta(days=1)
        
    return pd.DataFrame(records)


if __name__ == "__main__":
    df = generate_date_dimension_df()
    print(f"Generated {len(df):,} date dimension rows ({df['full_date'].min()} to {df['full_date'].max()})")
