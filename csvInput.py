import logging
from line_profiler_pycharm import profile
import sys, os, pandas as pd, numpy as np, time

import dbConfig
import formatters
from addContact import addRecord
from schemas import PersonSchema

SCHOOL_EMAIL_DF_COLUMN = "School Email"
EMAIL_DF_COLUMN = "Email"
CLASS_YEAR_DF_COLUMN = "Class Year"
FIRST_NAME_DF_COLUMN = "First Name"
LAST_NAME_DF_COLUMN = "Last Name"
PHONE_NUMBER_DF_COLUMN = "Phone Number"
SCHOOL_DF_COLUMN = "School"
ROLE_DF_COLUMN = "Role"

defaultColumns = [FIRST_NAME_DF_COLUMN, LAST_NAME_DF_COLUMN, ROLE_DF_COLUMN, PHONE_NUMBER_DF_COLUMN, EMAIL_DF_COLUMN,
                  CLASS_YEAR_DF_COLUMN, SCHOOL_DF_COLUMN]
outColumns = ["FirstName", "LastName", "Role", "PhoneNumber", "Email", "ClassYear", "School"]

columnMapping = dict(zip(defaultColumns, outColumns))

dateFormat = '%m/%d/%Y %H:%M:%S'
fileFormatter = logging.Formatter(fmt='%(asctime)s %(levelname)-2s | %(message)s', datefmt=dateFormat)
fileHandler = logging.FileHandler("./contacts.log")
fileHandler.setFormatter(fileFormatter)
fileHandler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@profile
def dbRowToPersonSchema(row: pd.Series, listName):
    d = row.to_dict()
    for key, value in d.items():
        d[key] = value if not pd.isna(value) else None
    d["ContactList"] = listName
    return PersonSchema(**d)


@profile
def formatDf(df, fmters):
    for f in fmters:
        if f.inputColName in df.columns:
            df[f.outColNames] = df.apply(lambda row: f.format(row[f.inputColName]), axis='columns',
                                         result_type='expand')
    return df.rename(columns=columnMapping)  # this maps the columns to what PersonSchema is expecting


@profile
def main():
    with open("./CSVs/manifest.txt", "r") as f:
        lines = [line.split(", ") for line in f.readlines() if not line.startswith("%")]

    nameFormatter = formatters.NameFormatter("Name", [FIRST_NAME_DF_COLUMN, LAST_NAME_DF_COLUMN])
    numberFormatter = formatters.PhoneNumberFormatter(PHONE_NUMBER_DF_COLUMN, [PHONE_NUMBER_DF_COLUMN])

    fmters = [numberFormatter, nameFormatter]
    # logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    for file, description in lines:
        df = formatDf(pd.read_csv("./CSVs/" + file), fmters)
        # for col in defaultColumns:
        #     if col not in df.columns:
        #         raise ValueError(f"CSV {file} must have column header '{col}'")
        logger.info(f"Adding CSV {file}")
        for index, row in df.iterrows():
            # print("Would have added",row,description)
            try:
                person = dbRowToPersonSchema(row, description.replace('\n', ''))
                person.CsvFilePath = file
            except Exception as e:
                print(f"Could not perform conversion on row {row} in file {file}. Are you sure that you have all of the required columns?",repr(e))
                logger.warning(f"Could not perform conversion on row {row} in file {file}: {repr(e)}")
                continue
            addRecord(person)
        dbConfig.renewDbSession()


if __name__ == "__main__":
    start = time.time()
    main()
    duration = time.time() - start
    print(f"Completed in {duration} seconds.")
