import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import sys

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

# Rename rows to oolumn 1
absorbance_data.set_index("Well", inplace=True)

print(absorbance_data.head())

# Delete Blank corrected raw data as it was calculated 
# based on the absorbance of the peripheral water
cleaned_data = absorbance_data.drop(columns = ["Blank corrected based on Raw Data (600)", "Content"])
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
print(cleaned_data.head())


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

correct_dtype(cleaned_data)

                

# Check if all cells in DataFrame contain data (it should)
if cleaned_data.isna().any(axis=None) == True:
    print("Missing data")