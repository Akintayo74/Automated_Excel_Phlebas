from dataclasses import dataclass

@dataclass
class Student:
    name: str
    row_idx: int
    sheet_name: str
    admission_number: str = None
