import pandas as pd
from sqlalchemy import create_engine

# Step 1: Read CSV files
stolen_vehicles_df = pd.read_csv(r"C:\Users\ADMIN\Downloads\Motor+Vehicle+Thefts+CSV\stolen_vehicles.csv")
make_details_df = pd.read_csv(r"C:\Users\ADMIN\Downloads\Motor+Vehicle+Thefts+CSV\make_details.csv")
location_df = pd.read_csv(r"C:\Users\ADMIN\Downloads\Motor+Vehicle+Thefts+CSV\locations.csv")

# Step 2: MySQL connection parameters
username = 'root'
password = 'Augengneiss@8189'
host = 'localhost'
port = '3306'
database = 'motor_vehicle_theftdb'

# Step 3: Create SQLAlchemy engine
engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}')

# Step 4: Export data to MySQL
stolen_vehicles_df.to_sql('stolen_vehicles', con=engine, if_exists='replace', index=False)
make_details_df.to_sql('make_details', con=engine, if_exists='replace', index=False)
location_df.to_sql('location', con=engine, if_exists='replace', index=False)

print("Data successfully exported to MySQL!")
 