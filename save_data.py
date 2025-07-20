from F1Scaper import getWDC, getWCC
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise Exception("Missing Supabase environment variables.")

supabase = create_client(url, key)

def save_to_supabase(all_data):
    response = supabase.table('f1_data').insert({"data": all_data}).execute()
    if response.error:
        print("Error inserting data:", response.error)
    else:
        print("Data inserted successfully")

def save_data():
    wdc = getWDC()
    wcc = getWCC()
    all_data = {
        "drivers_championship": wdc,
        "constructors_championship": wcc,
    }
    save_to_supabase(all_data)

if __name__ == "__main__":
    save_data()
