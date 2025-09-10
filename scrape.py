import requests
import json
import os

# API endpoint and parameters
url = "https://cms.vitap.ac.in/api/faculty-profiles"
params = {
    "populate[Patents][populate]": "*",
    "populate[Awards_and_Recognitions][populate]": "*",
    "populate[Projects][populate]": "*",
    "populate[Photo][populate]": "*",
    "filters[Employee_Id][$eq]": "1.70004"
}

headers = {
    "Accept": "application/json, text/plain, */*",
    "Authorization": "Bearer 3e602eb0ea823444179f1baf562a6e3ef4b260b83908ba8ada025e67f8f279493f69268174f966c8cfabcf50396a50cb59db8f12cb369a5d5e86aa253551c030c98e1f0f940efb018185dd359a5461a8b472c1bca7b0da7b04ebd60b33019c22afe8a5ffdd05450b11e059a342ff9711c17a5e30bda15e120a895d9786ac254f",
    "Origin": "https://vitap.ac.in",
    "Referer": "https://vitap.ac.in/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

# Send request
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    faculty_list = data.get("data", [])

    if not faculty_list:
        print("No faculty found.")
    else:
        # Extract all attributes
        faculty = faculty_list[0].get("attributes", {})

        # Clean/flatten nested structures if necessary
        # Example: Photo URL
        photo_data = faculty.get("Photo")
        if isinstance(photo_data, dict):
            faculty["Photo_URL"] = photo_data.get("url", "")
        elif isinstance(photo_data, list) and photo_data:
            faculty["Photo_URL"] = photo_data[0].get("url", "")
        else:
            faculty["Photo_URL"] = ""

        # Ensure all list fields are simple lists of titles (optional)
        for field in ["Patents", "Projects", "Awards_and_Recognitions"]:
            items = faculty.get(field, [])
            if isinstance(items, list):
                simple_list = []
                for item in items:
                    if isinstance(item, dict):
                        # Some CMS APIs wrap attributes inside 'attributes'
                        if "attributes" in item:
                            simple_list.append(item["attributes"])
                        else:
                            simple_list.append(item)
                    else:
                        simple_list.append(item)
                faculty[field] = simple_list

        # Save to JSON file
        os.makedirs("output", exist_ok=True)
        with open("output/faculty_1.70004.json", "w", encoding="utf-8") as f:
            json.dump(faculty, f, indent=4, ensure_ascii=False)

        print("Faculty data saved to output/faculty_1.70004.json")

else:
    print("Error:", response.status_code, response.text)
