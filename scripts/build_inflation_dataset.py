import os
import csv
import argparse
import requests
from datetime import date
from dotenv import load_dotenv

load_dotenv()

def fetch_cpi_data_by_range(startYear, endYear):
  api_key = os.getenv('BLS_API_KEY')
  if not api_key:
    raise ValueError("API Key not found. Please check your .env file. Registration is free on BLS website.")
  
  url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
  payload = {
      "seriesid": ["CUUR0000SA0"],
      "startyear": str(startYear),
      "endyear": str(endYear),
      "registrationkey": api_key
  }

  response = requests.post(url, json=payload)
  return response.json()['Results']['series'][0]['data']

def build_cpi_csv_for_last(years):
  YEARS_PER_BATCH = 10

  current_year = date.today().year
  oldest_requested_year = current_year - years

  cpi_array = []
  endYear = current_year
  while endYear > oldest_requested_year:
    startYear = max(endYear - YEARS_PER_BATCH + 1, oldest_requested_year)
    data = fetch_cpi_data_by_range(startYear, endYear)
    cpi_array += list(filter(lambda x: x['period'] == 'M01', data))
    endYear -= YEARS_PER_BATCH
  
  cpi_array.sort(key=lambda x: x['year'])

  oldest_year = oldest_requested_year
  if int(cpi_array[0]['year']) > oldest_requested_year:
    oldest_year = cpi_array[0]['year']
    print(f"Oldest entry found was {oldest_year}")

  output_path = f"./data/january_cpi_{oldest_year}_to_{current_year}.csv"

  with open(output_path, mode='w', newline='') as csv_file:
    fieldnames = ['year', 'cpi']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for row in cpi_array:
      writer.writerow({'year': row['year'], 'cpi': row['value']})

  print(f"File created successfully at: {output_path}")

def main():
  parser = argparse.ArgumentParser(description="Generate a CSV of January CPI data.")
    
  parser.add_argument("-y", "--years", type=int, default=100, help="Number of years to look back from the current year (default: 10)")

  args = parser.parse_args()

  build_cpi_csv_for_last(args.years)

if __name__ == "__main__":
    main()