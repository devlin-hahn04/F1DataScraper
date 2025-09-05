from F1Scaper import getWDC, getWCC, nextrace, getDriverPhotos
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
    next_gp = nextrace()
    driver_photos = getDriverPhotos()

    # Sort both dictionaries
    wdc_sorted = sorted(wdc.items(), key=lambda item: item[1]["points"], reverse=True)
    wdc_sorted_list = [
        {"driver": k, "team": v["team"], "points": v["points"]}
        for k, v in wdc_sorted
    ]

    wcc_sorted = sorted(wcc.items(), key=lambda item: int(item[1]), reverse=True)
    wcc_sorted_list = [{"team": k, "points": int(v)} for k, v in wcc_sorted]

    all_data = {
        "drivers_championship": wdc_sorted_list,
        "constructors_championship": wcc_sorted_list,
        "next_race": next_gp,
        "driver_photos": driver_photos   # stays as separate dict
    }

    save_to_supabase(all_data)



if __name__ == "__main__":
    save_data()
