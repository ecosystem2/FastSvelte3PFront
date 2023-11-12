import pandera as pa
import pandas as pd
from pandera.typing import Series
from typing import Optional
import uuid

# Define a regular expression to match ISO 8601 date format "YYYY-MM-DD"
iso8601_date_pattern = r"^\d{4}-\d{2}-\d{2}$"

# Load the CSV file as a controlled list
controlled_list_df = pd.read_csv(
    'schemamodels\models\controlled_lists\list_of_lists_nov23.csv')
# Replace 'column_name' with the actual column name in your CSV
product_type_controlled_list = controlled_list_df['product type'].tolist()
deposit_return_scheme_controlled_list = controlled_list_df['deposit return scheme'].tolist(
)

# Custom check function for UUID4 format
# previous check was pa.Check.str_length(36),


def check_uuid4(value):
    try:
        uuid_obj = uuid.UUID(value, version=4)
        return True
    except ValueError:
        return False


# import column from pandera as pa.column
schema = pa.DataFrameSchema(
    {
        "identifier": pa.Column(str, checks=pa.Check(lambda s: check_uuid4(s))),
        "completePackagingName": pa.Column(str, required=False),
        "description": pa.Column(str, required=False),
        "externalIdentifier": pa.Column(dict, required=False),
        "imageURLs": pa.Column(list, required=False),
        "completePackagingConstituentsIdentifier": pa.Column(list),
        "LOWcodeWOproduct": pa.Column(str, required=False),
        "productType": pa.Column(pa.String, checks=pa.Check(lambda s: s.isin(product_type_controlled_list)), required=False),
        "componentContactWithProduct": pa.Column(list),
        "LOWcodeWproduct": pa.Column(str, required=False),
        "onTheGo": pa.Column(bool),
        "householdWaste": pa.Column(bool),
        "depositReturnSchemes": pa.Column(pa.String, checks=pa.Check(lambda s: s.isin(deposit_return_scheme_controlled_list))),
        "completePackagingEndOfLifeRoutes": pa.Column(list, required=False),
        "recyclability": pa.Column(bool, required=False),
        "recyclabilityClaims": pa.Column(list, required=False),
        "height": pa.Column(int, required=False),
        "heightDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern), required=False),
        "width": pa.Column(int, required=False),
        "widthDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern), required=False),
        "depth": pa.Column(int, required=False),
        "depthDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern), required=False),
        "volume": pa.Column(int, required=False),
        "volumeDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern), required=False),
        "weight": pa.Column(int),
        "weightTolerance": pa.Column(int),
        "weightToleranceType": pa.Column(str),
        "weightDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern), required=False),
        "servingCapacity": pa.Column(int, required=False),
        "servingCapacityDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern), required=False),
        "partOfMultipack": pa.Column(bool),
        "certification": pa.Column(bool, required=False),
        "certificationClaims": pa.Column(list, required=False),
        "manufacturedCountry": pa.Column(int, required=False),
        "updateDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern)),
        "releaseDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern), required=False),
        "discontinueDate": pa.Column(pa.String, checks=pa.Check.str_matches(iso8601_date_pattern), required=False),
    },
    strict=True,
    coerce=True
)


def validate_and_log_data(data):
    log_filename = 'validation_errors.log'
    with open(log_filename, 'w') as log_file:
        log_file.write("Schema Errors:\n")

    for row_index, (_, row) in enumerate(data.iterrows(), start=1):
        try:
            schema.validate(row.to_frame().T, lazy=True)
        except pa.errors.SchemaErrors as err:
            with open(log_filename, 'a') as log_file:
                log_file.write(f"Error #{row_index}:\n")
                log_file.write("Schema errors and failure cases:\n")
                log_file.write(f"{err.failure_cases.to_string()}\n")
                log_file.write("\nDataFrame object that failed validation:\n")
                log_file.write(f"{err.data.to_string()}\n")
                log_file.write("\n")  # Add a separator between rows


# Define a function to read the log file contents
def read_log_file_contents():
    log_filename = 'validation_errors.log'
    try:
        with open(log_filename, 'r') as log_file:
            log_contents = log_file.read()
        return log_contents
    except FileNotFoundError:
        return "Log file not found"
