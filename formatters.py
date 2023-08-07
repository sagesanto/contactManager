import re
from abc import ABC, abstractmethod


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
            if not isinstance(number, str):
                number = int(number)  # get rid of an annoying floating .0 that sometimes appeears
            number = str(number)
            cleaned = re.sub("[^0-9]", "", str(number))
            return {self.outColNames[0]: cleaned[-10:]}
        except:
            return {self.outColNames[0]: None}


class NameFormatter(DataFormatter):
    def __init__(self, inputColName, outColNames):
        super().__init__(inputColName, outColNames)
        if len(self.outColNames) != 2:
            raise ValueError("The name formatter outputs to exactly two columns.")

    def info(self):
        return "This formatter takes a full name string and separates it into first name, last name"

    def format(self, name):
        try:
            spl = name.split(" ")
            print(spl)
            return {"First Name": spl[0], "Last Name": " ".join(spl[1:])}
        except:
            return None
        # last ten digits of phone number stripped of all non-digit characters