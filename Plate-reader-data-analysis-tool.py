import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import sys

#####
# MICROPLATE INFO
# Peripheral wells filled with water to avoid edge effect

# Rows with samples
sample_row = ["B", "C", "D"]
# Columns with samples
sample_col = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

# Rows with blanks
blank_row = ["E", "F", "G"]
# Columns with blanks
blank_col = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

######

# Read the entire file into a DataFrame
all_data = pd.read_csv(sys.argv[1], header=None)

# Searate metadata (first 10 rows) from absorbane data (rows 13-110)
metadata = all_data.iloc[:10, 0]
absorbance_data = all_data.iloc[12:]

# Check data has been imported correctly
#print(metadata)
print(absorbance_data.head())

# Rename columns to row 1 of absorbance_data
absorbance_data.columns = absorbance_data.iloc[0]
absorbance_data = absorbance_data[1:]

absorbance_data.iat[0, 0] = "Well"
absorbance_data.iat[0, 2] = "Group"

print(absorbance_data.head())

# Rename rows to column 1
absorbance_data.set_index("Well", inplace=True)

print(absorbance_data.head())

# Delete Blank corrected raw data as it was calculated 
# based on the absorbance of the peripheral water
cleaned_data = absorbance_data.drop(columns = ["Group", "Blank corrected based on Raw Data (600)", "Content"])
#print(cleaned_data.head())

# Rename column names to row 1 (containing time)
cleaned_data.columns = cleaned_data.iloc[0]
cleaned_data = cleaned_data[1:]

print(cleaned_data.head())

# Delete absorbance of peripheral water blanks
# Define wells of peripheral water blanks
def identify_peripheral_water():
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    water_wells = []
    for row in rows:
        for col in range(1, 13):
            if row == "A" or row == "H":
                well = row + str(f"{col:02d}")
            else:
                if col == 1 or col == 12:
                    well = row + str(f"{col:02d}")
            if well not in water_wells:
                water_wells.append(well)
    return water_wells

#print(identify_peripheral_water())
peripheral_water = identify_peripheral_water()

cleaned_data = cleaned_data.drop(index = peripheral_water)


# Check if data are of correct data type
def correct_dtype(df):
    col_to_check = df.columns.tolist()

    for col in col_to_check:
        if col != "Group":
            if not is_numeric_dtype(df[col]):
                try:
                    # First try converting directly to float
                    df[col] = df[col].astype(float)
                except ValueError as e:
                    # Replace non-numeric values with Nan
                    pd.to_numeric(df[col], errors="coerce")
    return df

cleaned_data = correct_dtype(cleaned_data)


# Check that Group column has sensible Group IDs
#def check_GroupID(df):
#    IDs = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", 
#          "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
#          "U", "V", "X", "Y", "Z"]

#    sample_IDs = df["Group"].values.tolist()

#    for i in range(len(sample_IDs)):
#        if df.iat[i, 0] not in IDs:
#            df.iat[i, 0] = np.nan

#    return df 
            
# cleaned_data = check_GroupID(cleaned_data)


# Check if all cells in DataFrame contain data (it should)
def check_missing_data(df):
    col_to_check = df.columns.tolist()

    for col in col_to_check:
        # Check for NaN values
        nan_count = df[col].isna().sum()
        nan_idx = df.index[df[col].isna()].tolist()

        if nan_count > 0:
            print(f"Warning: {col} has {nan_count} missing values.")
            print(f"Missing values in wells: {nan_idx}")

check_missing_data(cleaned_data)

print(cleaned_data.head())


# Calculate average of the absorbance values of blanks
def calculate_blank_average(df, rows, columns):
    averages = {}

    for col in columns:
        # Get column IDs
        wells = []
        for row in rows:
            col_ID = str(f"{col:02d}")
            well = row + col_ID
            wells.append(well)
        
        # Subset replicates for each sample blank
        blank_rep = df.loc[wells]

        # Calculate aveage of each column
        average = blank_rep.mean().to_dict()

        # Append averages to a dictionary
        averages[col_ID] = average

    return averages

print(calculate_blank_average(cleaned_data, blank_row, blank_col))


# Subtract absorbance of blanks from sample absorbance
