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
    if response.data:
        print("Data inserted successfully:", response.data)
    else:
        print("Insert may have failed. Raw response:", response)


def save_data():
    wdc = getWDC()
    wcc = getWCC()

    # Sort both dictionaries by descending point values
    wdc_sorted = dict(sorted(wdc.items(), key=lambda item: int(item[1]), reverse=True))
    wcc_sorted = dict(sorted(wcc.items(), key=lambda item: int(item[1]), reverse=True))

    all_data = {
        "drivers_championship": wdc_sorted,
        "constructors_championship": wcc_sorted,
    }

    save_to_supabase(all_data)


if __name__ == "__main__":
    save_data()
