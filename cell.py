import requests
import json
import time
import os
from datetime import datetime, timedelta
import pytz
from colorama import Fore, Style
import random

# Global headers variable
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
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

# Function to fetch user details
def user_detail(authorization):
    url = "https://cellcoin.org/users/session"
    
    headers['authorization'] = authorization  # Set authorization token
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for bad responses (4xx or 5xx)
        
        # Assuming the response contains JSON data, you can access it using response.json()
        data = response.json()
        
        # Example: Extracting user information from the JSON response
        user_id = data.get('user', {}).get('ID', '')
        first_name = data.get('user', {}).get('first_name', '')
        balance = data.get('cell', {}).get('balance', '')
        energy_amount = data.get('cell', {}).get('energy_amount', '')
        click_level = data.get('cell', {}).get('click_level', '')
        energy_level = data.get('cell', {}).get('energy_level', '')
        mining_speed_level = data.get('cell', {}).get('mining_speed_level', '')
        multiplier_level = data.get('cell', {}).get('multiplier_level', '')
        storage_level = data.get('cell', {}).get('storage_level', '')
        storage_fills_at = data.get('cell', {}).get('storage_fills_at', '')
        
        # Return relevant information
        return {
            'user_id': user_id,
            'first_name': first_name,
            'balance': balance,
            'energy_amount': energy_amount,
            'click_level': click_level,
            'energy_level': energy_level,
            'mining_speed_level': mining_speed_level,
            'multiplier_level': multiplier_level,
            'storage_level': storage_level,
            'storage_fills_at': storage_fills_at
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user details: {e}")
        return None

# Function to perform automatic mining
def auto_mining(authorization, clicks_amount=None):
    url = "https://cellcoin.org/cells/submit_clicks"
    
    headers['authorization'] = authorization  # Set authorization token
    
    try:
        while True:
            # Fetch user details to get current energy_amount
            user_info = user_detail(authorization)
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
            print(Fore.GREEN + f"Auto mining successful for {clicks_amount} clicks.")
            
            # Optional: Sleep for a while before next auto mining request
            time.sleep(10)  # Sleep for 10 seconds
            
    except requests.exceptions.RequestException as e:
        print(f"Error sending auto mining request: {e}")
        return None

# Function to claim storage after a delay
def claim_storage_delayed(authorization):
    url = "https://cellcoin.org/cells/claim_storage"
    
    headers['authorization'] = authorization  # Set authorization token
    
    try:
        # Fetch user details to get storage_fill time
        user_info = user_detail(authorization)
        if not user_info:
            return None
        
        storage_fill = user_info['storage_fills_at']
        
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
            print(Fore.GREEN + f"Claim storage successful.")
            
            return response.json()
        
        else:
            # Wait for the delay time before claiming storage
            print(f"Waiting {delay_seconds} seconds before claiming storage...")
            time.sleep(delay_seconds)
            
            # Now claim storage after the delay
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise exception for bad responses (4xx or 5xx)
            
            # Assuming you want to print or return the response data
            print(Fore.GREEN + f"Claim storage request successful.")
            
            # Provide confirmation if claim storage is successful
            if response.json().get('success', False):
                print(Fore.GREEN + f"Storage claimed successfully!")
            
            return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending claim storage request: {e}")
        return None

# Function to print welcome message
def print_welcome_message():
    """Function to print a welcome message."""
    print(r"""      

▒█▀▀▀█ █▀▀█ ░█▀█░ ▒█▄░▒█ 
░▀▀▀▄▄ ░░▀▄ █▄▄█▄ ▒█▒█▒█ 
▒█▄▄▄█ █▄▄█ ░░░█░ ▒█░░▀█
          """)
    print(Fore.GREEN + Style.BRIGHT + "CELL MEGA Wallet BOT")
    print(Fore.RED + Style.BRIGHT + "Jangan di edit la bang :)\n\n")

# Function to stop auto mining when user interrupts
def stop_auto_mining():
    """Function to stop auto mining when user interrupts."""
    print("\nMenghentikan auto mining dan menuju ke akun selanjutnya...")
    time.sleep(2)  # Optional: Add a small delay before clearing the screen
    
    # Clear screen using os.system('cls') for Windows or os.system('clear') for Linux/MacOS
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print welcome message again after clearing the screen
    print_welcome_message()

# Function to upgrade cell level
def upgrade_cell_level(authorization, upgrade_option):
    url = "https://cellcoin.org/cells/levels/upgrade"
    
    headers['authorization'] = authorization  # Set authorization token
    
    try:
        data = {
            "level_type": upgrade_option
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for bad responses (4xx or 5xx)
        
        if response.json().get('success', False):
            print(f"Upgrade {upgrade_option} berhasil!")
        else:
            print(f"Upgrade {upgrade_option} gagal.")
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Duit anda tidak cukup kocak !!!!")
        return None
    
# Function to perform automatic upgrade
def perform_auto_upgrade(authorization):
    upgrade_choices = ["click", "energy", "mining_speed", "multiplier", "storage"]
    
    for choice in upgrade_choices:
        upgrade_cell_level(choice, authorization)

# Function to print text in rainbow colors
def print_rainbow(text):
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    rainbow_text = ""
    for char in text:
        rainbow_text += random.choice(colors) + char
    print(rainbow_text + Style.RESET_ALL)            

# Main function to run the script
def main():
    print_welcome_message()

    try:
        # Read all authorization tokens from auth.txt
        auth_tokens = []
        try:
            with open('auth.txt', 'r') as f:
                for line in f:
                    authorization = line.strip()
                    auth_tokens.append(authorization)
        except FileNotFoundError:
            print("Error: auth.txt file not found.")
            return
        
        if not auth_tokens:
            print("No authorization tokens found. Exiting...")
            return
        
        for authorization in auth_tokens:
            confirm_upgrade = input(Fore.LIGHTBLACK_EX + f"Apakah Anda ingin melakukan upgrade otomatis? (y/n): ").strip().lower()
            
            if confirm_upgrade == 'y':
                perform_auto_upgrade(authorization)  # Perform automatic upgrade
            
            # After performing or skipping auto upgrade, ask if user wants to claim storage
            if input(f"Apakah Anda ingin klaim storage? (y/n): ").strip().lower() == 'y':
                claim_storage_delayed(authorization)  # Claim storage after a delay
            
             # Fetch user info before auto mining
            user_info = user_detail(authorization)
            if user_info:
                print("\n", end="")
                print_rainbow("============== Detail Akun ==============")
                print("")
                print("Nama          :", user_info['first_name'])
                print("ID            :", user_info['user_id'])
                print("Balance       :", user_info['balance'])
                print("Energy        :", user_info['energy_amount'])
                print("")
                print_rainbow("============== Detail Level ==============")
                print("")
                print("Click         :", user_info['click_level'])
                print("Energy        :", user_info['energy_level'])
                print("Mining Speed  :", user_info['mining_speed_level'])
                print("Multiplier    :", user_info['multiplier_level'])
                print("Storage       :", user_info['storage_level'])
                print("")
                print_rainbow("============== Auto Mining ==============")
                print("")

                try:
                    # Example usage of auto_mining function
                    auto_mining(authorization, 2000)  # Send 2000 clicks

                except KeyboardInterrupt:
                    stop_auto_mining()
                    continue  # Skip to the next account after stopping auto mining

            else:
                print("Failed to fetch user details for this authorization.")
            
            # Delay before proceeding to the next account
            print(f"Waiting 10 seconds before processing next account...")
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nTerima Kasih Telah Menggunakan BOT ini.")

# Entry point of the script
if __name__ == "__main__":
    main()
