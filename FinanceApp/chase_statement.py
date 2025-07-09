import re
import pdfplumber
import pandas as pd
from collections import namedtuple
import pprint
import datetime
import time


class Chase:

    def __init__(self,file):


#CHASE BANK STATEMENT READER

#PDF to DataFrame

        self.Line = namedtuple("Line", "Date Details Amount")
        self.Doc = namedtuple("Range","opening closing")
        self.line_re = re.compile(r'\d{2}/\d{2}')
        self.ranges = []
        self.lines = []
        self.total_check = 0

    def pdf_convert(self,file):
        with pdfplumber.open(file) as pdf:
            pages = pdf.pages
            for page in pdf.pages:
                text = page.extract_text()
                for line in text.split("\n"):
                    if line.startswith("Opening/Closing"):
                        split_line = line.split()
                        opening_date = split_line[-3]
                        closing_date = split_line[-1]
                        self.ranges.append(self.Doc(opening=opening_date,closing=closing_date))
                    elif self.line_re.match(line):
                        items = line.split()
                        x = " ".join(items[1:-1])
                        try:
                            date_time_str = f"{items[0]}/{year}"
                        except:
                            date_time_str = {items[0]}
                        if items[-1] != "EURO":
                            self.lines.append(self.Line(Date=date_time_str,Details=x,Amount=items[-1]))



#Data Frame

        df = pd.DataFrame(self.lines)

        df["Amount"] = df["Amount"].astype(str).str.replace(",", "").astype(float)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Details"] = df["Details"].str.strip().replace(r'\s+', ' ', regex=True)
        df = df.sort_values(by=["Date"])

        debit_credit = []

        for _ in df["Amount"]:

            if _ < 0:
                debit_credit.append("Credit")
            else:
                debit_credit.append("Debit")

        currency = ["USD" for number in df["Amount"]]

        df["Currency"] = currency
        df["Debit/Credit"] = debit_credit

        return df
