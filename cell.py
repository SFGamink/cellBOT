import requests
import json
import time
from datetime import datetime, timedelta
import pytz  # Import pytz library for timezone handling

# Function to read authorization token from auth.txt file
def read_auth_from_file():
    try:
        with open('auth.txt', 'r') as f:
            authorization = f.read().strip()
            return authorization
    except FileNotFoundError:
        print("Error: auth.txt file not found.")
        return None

# Function to fetch user details
def user_detail():
    url = "https://cellcoin.org/users/session"
    
    # Read authorization token from auth.txt
    authorization = read_auth_from_file()
    if not authorization:
        return None
    
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": authorization,
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "x-time-zone": "Asia/Bangkok",
        "Referer": "https://cell-frontend.s3.us-east-1.amazonaws.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for bad responses (4xx or 5xx)
        
        # Assuming the response contains JSON data, you can access it using response.json()
        data = response.json()
        
        # Example: Extracting user information from the JSON response
        user_id = data.get('user', {}).get('ID', '')
        nama = data.get('user', {}).get('first_name', '')
        balance = data.get('cell', {}).get('balance', '')
        energy_amount = data.get('cell', {}).get('energy_amount', '')
        click = data.get('cell', {}).get('click_level', '')
        energy = data.get('cell', {}).get('energy_level', '')
        mining_speed = data.get('cell', {}).get('mining_speed_level', '')
        multiplier = data.get('cell', {}).get('multiplier_level', '')
        storage = data.get('cell', {}).get('storage_level', '')
        storage_fill = data.get('cell', {}).get('storage_fills_at', '')
        
        # Return whatever information you need
        return {
            'user_id': user_id,
            'nama': nama,
            'balance': balance,
            'energy_amount': energy_amount,
            'click': click,
            'energy': energy,
            'mining_speed': mining_speed,
            'multiplier': multiplier,
            'storage': storage,
            'storage_fill': storage_fill  # Added storage_fill to return
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user details: {e}")
        return None

# Function to perform automatic mining
def auto_mining(clicks_amount=None):
    url = "https://cellcoin.org/cells/submit_clicks"
    
    # Read authorization token from auth.txt
    authorization = read_auth_from_file()
    if not authorization:
        return None
    
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": authorization,
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "x-time-zone": "Asia/Bangkok",
        "Referer": "https://cell-frontend.s3.us-east-1.amazonaws.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    try:
        while True:
            # Fetch user details to get current energy_amount
            user_info = user_detail()
            if not user_info:
                return None
            
            current_energy = user_info['energy_amount']
            
            # Determine clicks_amount to use
            if clicks_amount is None:
                # Use current energy if clicks_amount not provided
                clicks_amount = current_energy
            else:
                # Use provided clicks_amount, but ensure it does not exceed current_energy
                clicks_amount = min(clicks_amount, current_energy)
            
            # Ensure clicks_amount is not less than or equal to 0
            if clicks_amount <= 0:
                print("Energy habis. Berhenti mining otomatis.")
                break
            
            data = {
                "clicks_amount": clicks_amount
            }
            
            # Convert Python dictionary to JSON string
            json_data = json.dumps(data)
            
            # Send POST request for auto mining
            response = requests.post(url, headers=headers, data=json_data)
            response.raise_for_status()  # Raise exception for bad responses (4xx or 5xx)
            
            # Assuming you want to log or print something based on the response
            print("Auto mining successful for", clicks_amount, "clicks.")
            
            # Optional: Sleep for a while before next auto mining request
            time.sleep(10)  # Sleep for 10 seconds
            
    except requests.exceptions.RequestException as e:
        print(f"Error sending auto mining request: {e}")
        return None

# Function to claim storage after a delay
def claim_storage_delayed():
    url = "https://cellcoin.org/cells/claim_storage"
    
    # Read authorization token from auth.txt
    authorization = read_auth_from_file()
    if not authorization:
        return None
    
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": authorization,
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "x-time-zone": "Asia/Bangkok",
        "Referer": "https://cell-frontend.s3.us-east-1.amazonaws.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    try:
        # Fetch user details to get storage_fill time
        user_info = user_detail()
        if not user_info:
            return None
        
        storage_fill = user_info['storage_fill']
        
        # Parse the storage_fill time into a timezone-aware datetime object
        storage_fill_time = datetime.fromisoformat(storage_fill).replace(tzinfo=pytz.timezone('Asia/Bangkok'))
        
        # Calculate the delay time (2 hours from now)
        claim_time = storage_fill_time + timedelta(hours=2)
        
        # Make datetime.now() timezone-aware in the same timezone
        now = datetime.now(pytz.timezone('Asia/Bangkok'))
        
        # Calculate the difference in seconds between now and claim_time
        delay_seconds = (claim_time - now).total_seconds()
        
        # If the delay is negative, it means it's already time to claim storage
        if delay_seconds <= 0:
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise exception for bad responses (4xx or 5xx)
            
            # Assuming you want to print or return the response data
            print("Claim storage request successful.")
            print(response.json())  # Print response data
            
            # Provide confirmation if claim storage is successful
            if response.json().get('success', False):
                print("Storage claimed successfully!")
            else:
                print("Failed to claim storage.")
            
            return response.json()
        
        else:
            # Wait for the delay time before claiming storage
            print(f"Waiting {delay_seconds} seconds before claiming storage...")
            time.sleep(delay_seconds)
            
            # Now claim storage after the delay
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise exception for bad responses (4xx or 5xx)
            
            # Assuming you want to print or return the response data
            print("Claim storage request successful.")
            
            # Provide confirmation if claim storage is successful
            if response.json().get('success', False):
                print("Storage claimed successfully!")
            else:
                print("Failed to claim storage.")
            
            return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending claim storage request: {e}")
        return None

# Main function to run the script
def main():
    try:
        # Ask user if they want to claim storage before proceeding
        claim_choice = input("\nApakah Anda ingin klaim storage ? (y/n): ").strip().lower()

        if claim_choice == 'y':
            claim_storage_delayed()  # Claim storage after a delay

        user_info = user_detail()
        if user_info:
            print("\n============== Detail Akun ===============")
            print("Nama          :", user_info['nama'])
            print("ID            :", user_info['user_id'])
            print("Balance       :", user_info['balance'])
            print("Energy        :", user_info['energy_amount'])
            print("============== Detail Level ===============")
            print("Click         :", user_info['click'])
            print("Energy        :", user_info['energy'])
            print("Mining Speed  :", user_info['mining_speed'])
            print("Multiplier    :", user_info['multiplier'])
            print("Storage       :", user_info['storage'])
            print("============== Auto Mining ===============")

            # Example usage of auto_mining function
            auto_mining(1)  # Send 100 clicks

        else:
            print("Failed to fetch user details.")

    except KeyboardInterrupt:
        print("\nProses dihentikan oleh pengguna.")

# Entry point of the script
if __name__ == "__main__":
    main()
