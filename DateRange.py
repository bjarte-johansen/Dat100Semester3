from datetime import datetime
from typing import Tuple


def get_number_of_days_between_dates(start_date, end_date) -> int:
    return (end_date - start_date).days

class DateRange:
    def __init__(self, start_date, end_date):
        self.start_date = None
        self.end_date  = None
        self.init(start_date, end_date)

    def init(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def get_duration_in_days(self):
        return get_number_of_days_between_dates(self.start_date, self.end_date)

    def to_days_interval(self) -> Tuple[int, int]:
        start_of_year_date = datetime(self.start_date.year, 1, 1)
        num_days_into_year = get_number_of_days_between_dates(
            start_of_year_date,
            self.start_date
            )

        return (
            num_days_into_year,
            num_days_into_year + self.get_duration_in_days()
            )
# END DateRange