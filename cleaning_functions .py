"""
Cleaning functions for the Shark Attacks Quest.

Each function takes a DataFrame and returns a DataFrame (never mutates
in place only). Call order matters for two functions: keep_relevant_columns
and remove_duplicates run first (right after loading the data), and
clean_column_names always runs last, after every column has been cleaned
under its original (capitalized) name.

Usage from the notebook:

    import pandas as pd
    from cleaning_functions import (
        keep_relevant_columns, remove_duplicates,
        clean_activity, clean_state,
        clean_sex, clean_country, clean_year,
        clean_location, clean_injury, clean_fatal,
        clean_time, clean_date,
        clean_column_names,
    )

    df = pd.read_excel('sharks.xls', engine='xlrd')
    df = keep_relevant_columns(df)
    df = remove_duplicates(df)
    df = clean_activity(df)
    df = clean_state(df)
    df = clean_sex(df)
    df = clean_country(df)
    df = clean_year(df)
    df = clean_location(df)
    df = clean_injury(df)
    df = clean_fatal(df)
    df = clean_time(df)
    df = clean_date(df)
    df = clean_column_names(df)
"""

import re
import numpy as np
import pandas as pd


# --- Setup: run first, right after loading the data -------------------

def keep_relevant_columns(df):
    """Keep only the columns relevant to our hypotheses and business case."""
    columns_to_keep = ['Date', 'Year', 'Country', 'State', 'Location',
                        'Activity', 'Sex', 'Injury', 'Fatal Y/N', 'Time']
    df = df[columns_to_keep]
    return df


def remove_duplicates(df):
    """Drop fully duplicate rows."""
    print('Duplicates found:', df.duplicated().sum())
    df = df.drop_duplicates()
    return df


# --- Pariya: Activity, State --------------------------------------------

def clean_activity(df):
    """Fix whitespace/casing in Activity, standardize missing values."""
    df['Activity'] = df['Activity'].str.strip().str.title()
    df['Activity'] = df['Activity'].fillna('Unknown')
    return df


def clean_state(df):
    """Fix whitespace in State (no title-case: would break names like 'KwaZulu-Natal')."""
    df['State'] = df['State'].str.strip()
    df['State'] = df['State'].fillna('Unknown')
    return df


# --- Miguel: Sex, Country, Year -----------------------------------------

def clean_sex(df):
    """Standardize Sex to M / F / Unknown."""
    df['Sex'] = df['Sex'].str.strip().str.upper()
    df['Sex'] = df['Sex'].where(df['Sex'].isin(['M', 'F']), 'Unknown')
    return df


def clean_country(df):
    """Fix whitespace/casing in Country, standardize missing values."""
    df['Country'] = df['Country'].str.strip().str.title()
    df['Country'] = df['Country'].fillna('Unknown')
    return df


def clean_year(df):
    """Fill missing Year with 0 (matches the dataset's own convention for undated old cases) and convert to int."""
    df['Year'] = df['Year'].fillna(0)
    df['Year'] = df['Year'].astype(int)
    return df


# --- Effie: Location, Injury, Fatal Y/N ----------------------------------

def clean_location(df):
    """Fix whitespace in Location, standardize missing values."""
    df['Location'] = df['Location'].str.strip()
    df['Location'] = df['Location'].fillna('Unknown')
    return df


def clean_injury(df):
    """Fix whitespace/quotes in Injury, standardize repeated phrases and missing values."""
    df['Injury'] = (
        df['Injury'].astype(str).str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip('"')
    )
    df['Injury'] = df['Injury'].replace(
        {'No Injury': 'No injury', ' No injury': 'No injury', 'No injuries': 'No injury', 'nan': np.nan}
    )
    df['Injury'] = df['Injury'].fillna('Unknown')
    return df


def clean_fatal(df):
    """Standardize Fatal Y/N to Yes / No / Unknown, cleaning junk values like '2017', 'Y x 2'.
    Where the raw value is missing/junk, infer from keywords in the (already-cleaned) Injury text,
    then 'Unknown' for anything still unresolved."""
    fatal = df['Fatal Y/N'].astype(str).str.strip().str.upper()
    fatal = fatal.replace({'Y X 2': 'Y'})
    fatal = fatal.where(fatal.isin(['Y', 'N']))  # anything else (junk, 'UNKNOWN', 'nan') -> NaN

    fatal_keywords = [
        "fatal", "death", "died", "killed", "body not recovered", "remains",
        "drown", "scaveng", "perish", "murder", "skeleton",
        "post mortem", "post-mortem",
        "body recovered", "bones recovered", "human hand recovered",
        "human foot recovered", "human head recovered", "torso recovered",
        "human casualties", "disappeared", "missing", "body washed up on",
        "body found", "corps",
    ]
    nonfatal_keywords = [
        "no injury", "no injuries", "survived", "minor",
        "bitten", "laceration", "abrasion", "puncture", "bruis", "scratch",
        "hoax", "never happened", "fiction", "not a shark attack",
        "no attack", "not shark", "superficial injuries", "recovering",
        "painfully injured",
    ]

    def infer(idx):
        if pd.notna(fatal.loc[idx]):
            return fatal.loc[idx]
        text = str(df.loc[idx, 'Injury']).lower()
        if any(k in text for k in fatal_keywords):
            return 'Y'
        if any(k in text for k in nonfatal_keywords):
            return 'N'
        return np.nan

    fatal = pd.Series([infer(i) for i in df.index], index=df.index)

    df['Fatal Y/N'] = fatal.map({'Y': 'Yes', 'N': 'No'}).fillna('Unknown')
    return df


# --- Zahid: Time, Date ----------------------------------------------------

def clean_time(df):
    """Parse messy Time text (e.g. '1015hrs', '13h00', '9:30') into HH:MM where possible."""
    def parse_time(val):
        val = str(val).strip().lower()
        if val in ['nan', '', 'none', 'unknown']:
            return 'Unknown'
        four_digits = re.search(r'\d{4}', val)
        if four_digits:
            clean_digits = re.sub(r'\D', '', val)[:4]
            return f"{clean_digits[:2]}:{clean_digits[2:]}"
        h_match = re.search(r'(\d{1,2})h(\d{2})', val)
        if h_match:
            return f"{int(h_match.group(1)):02d}:{h_match.group(2)}"
        colon_match = re.search(r'(\d{1,2}):(\d{2})', val)
        if colon_match:
            return f"{int(colon_match.group(1)):02d}:{colon_match.group(2)}"
        return val.title()
    df['Time'] = df['Time'].apply(parse_time)
    return df


def clean_date(df):
    """Combine Date text with Year and try to parse a full date; unparseable rows fall back to 'Unknown'."""
    def parse_date_row(row):
        date_str = str(row['Date']).strip()
        year_str = str(row['Year']).strip()
        if date_str.lower() in ['unknown', 'nan', 'none', '']:
            return None
        if year_str.endswith('.0'):
            year_str = year_str[:-2]
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str, flags=re.IGNORECASE)
        return f"{date_str} {year_str}"
    raw_dates = df.apply(parse_date_row, axis=1)
    converted_dates = pd.to_datetime(raw_dates, format='%d %B %Y', errors='coerce')
    df['Date'] = converted_dates.dt.strftime('%Y-%m-%d').fillna('Unknown')
    return df


# --- Final step: always run last -----------------------------------------

def clean_column_names(df):
    """Lowercase and underscore all column names. Run this last, after every
    column has been cleaned under its original (capitalized) name."""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df
