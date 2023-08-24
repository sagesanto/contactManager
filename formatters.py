import re
from abc import ABC, abstractmethod

import pandas as pd

from addContact import logger


class DataFormatter(ABC):
    def __init__(self, inputColName, outColNames: list):
        self.inputColName = inputColName
        self.outColNames = outColNames

    @abstractmethod
    def info(self):
        # a description of what this formatter does
        pass

    @abstractmethod
    def format(self, entry):
        # take a single entry and format it. return None on failure
        pass


class PhoneNumberFormatter(DataFormatter):
    def __init__(self, inputColName, outColNames: list):
        super().__init__(inputColName, outColNames)
        if len(self.outColNames) != 1:
            raise ValueError("Phone number formatter should have exactly one output column.")

    def info(self):
        return "This formatter takes phone numbers in any form and returns their last 10 digits with no non-digit characters."

    def format(self, number):
        try:
            if pd.isna(number):
                raise ValueError("Empty phone number")
            cleaned = re.sub("[^0-9]", "", str(number))[-10:]
            if len(cleaned) < 10:
                raise ValueError("Must have 10 or more digits.")
            if cleaned.startswith('0') or cleaned.startswith('1'):
                raise ValueError("Valid area codes do not start with 0 or 1.")
            return {self.outColNames[0]: cleaned}
        except Exception as e:
            logger.warning(f"Could not format phone number {number}: {repr(e)}")
            return {self.outColNames[0]: None}
        # last ten digits of phone number stripped of all non-digit characters


class NameFormatter(DataFormatter):
    def __init__(self, inputColName, outColNames):
        super().__init__(inputColName, outColNames)
        if len(self.outColNames) != 2:
            raise ValueError("The name formatter outputs to exactly two columns.")

    def info(self):
        return "This formatter takes a full name string and separates it into First Name and Last Name columns"

    def format(self, name):
        try:
            spl = name.split(" ")
            print(spl)
            return {"First Name": spl[0], "Last Name": " ".join(spl[1:])}
        except:
            return None
