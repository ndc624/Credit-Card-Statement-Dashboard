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
                        df1 = pd.DataFrame(self.ranges)
                        df1["opening"] = pd.to_datetime(df1["opening"], format="mixed")
                        df1["closing"] = pd.to_datetime(df1["closing"], format="mixed")
                        year = df1["opening"][0].year
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

        # for number in ["Amount"]:
        #
        #     number = number[1:]


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

        # for date in df["Date"]:
        #
        #     df["Date"] = date.date()


        df["Currency"] = currency
        df["Debit/Credit"] = debit_credit
        # df = df.set_index(df["Date"])
        # debit = ["Debit" for number in df["Amount"] if number < 0 and "Credit" for number in df["Amount"] if number > 0]
        # print(debit_credit)
        #
        # df.to_csv(f"chase_statement ({df1["opening"][0]}-{df1["closing"][0]})")


        return df
