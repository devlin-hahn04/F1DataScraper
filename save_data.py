from F1Scaper import getWDC, getWCC, getDriverPhotos, get_next_race_details
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
    print("Getting WDC data...")
    wdc = getWDC()
    
    print("\nGetting WCC data...")
    wcc = getWCC()
    
    print("\nGetting next race details...")
    next_race_details = get_next_race_details()
    
    print("\nGetting driver photos...")
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
        "next_race": next_race_details,  # Now an object instead of a string
        "driver_photos": driver_photos,  
    }

    save_to_supabase(all_data)
    print(f"\n✅ Data saved successfully!")
    print(f"\n📅 Next Race Details:")
    print(f"   Name: {next_race_details['name']}")
    print(f"   Circuit: {next_race_details['circuit']}")
    print(f"   Location: {next_race_details['location']}")
    print(f"   Date: {next_race_details['date']}")
    print(f"   Time: {next_race_details['time']}")
    print(f"   Coordinates: {next_race_details['lat']}, {next_race_details['lng']}")


if __name__ == "__main__":
    save_data()
