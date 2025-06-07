import requests
import random
import time
import json
from fake_useragent import UserAgent
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def get_user_event():
    # Read token from file
    try:
        with open('token.txt', 'r') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: token.txt file not found")
        return None
    except Exception as e:
        print(f"{Fore.RED}Error reading token file: {e}")
        return None
    
    # Generate random user agent
    ua = UserAgent()
    user_agent = ua.chrome
    
    # API endpoint
    url = "https://mkpl-api.prod.myneighboralice.com/api/quests/user-event"
    
    # Headers
    headers = {
        "authority": "mkpl-api.prod.myneighboralice.com",
        "method": "GET",
        "path": "/api/quests/user-event",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "cache-control": "no-cache",
        "origin": "https://myneighboralice.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://myneighboralice.com/",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": user_agent
    }
    
    try:
        # Make the GET request
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json(), headers, user_agent
        else:
            print(f"{Fore.RED}Error: API request failed")
            return None, None, None
    except Exception as e:
        print(f"{Fore.RED}Error making API request: {e}")
        return None, None, None

def complete_quests():
    # Get user events and headers
    user_events, headers, user_agent = get_user_event()
    if not user_events:
        print(f"{Fore.RED}Failed to get user events")
        return
    
    # Read account ID from file
    try:
        with open('id.txt', 'r') as file:
            account_id = file.read().strip()
    except FileNotFoundError:
        print(f"{Fore.RED}Error: id.txt file not found")
        return
    except Exception as e:
        print(f"{Fore.RED}Error reading id file: {e}")
        return
    
    # Update headers for POST request
    headers["method"] = "POST"
    headers["content-type"] = "application/json"
    headers["user-agent"] = user_agent
    
    # Process each quest
    if 'quests' in user_events:
        quest_count = len(user_events['quests'])
        print(f"{Fore.GREEN}Found {quest_count} quests to complete")
        
        # Count already completed quests
        completed_count = 0
        incomplete_quests = []
        
        # First, check which quests are already completed
        for quest in user_events['quests']:
            quest_id = quest.get('id')
            if not quest_id:
                continue
                
            # Check if quest has tracks (already completed)
            if quest.get('tracks') and len(quest.get('tracks')) > 0:
                completed_count += 1
            else:
                incomplete_quests.append(quest)
        
        print(f"{Fore.BLUE}{completed_count} quests already completed")
        
        # Now process only incomplete quests
        if incomplete_quests:
            print(f"{Fore.CYAN}Processing {len(incomplete_quests)} incomplete quests")
            
            for i, quest in enumerate(incomplete_quests):
                quest_id = quest.get('id')
                
                # Update path in headers
                headers["path"] = f"/api/quests/{quest_id}/complete"
                
                # API endpoint for completing the quest
                url = f"https://mkpl-api.prod.myneighboralice.com/api/quests/{quest_id}/complete"
                
                # Payload
                payload = {
                    "accountId": account_id
                }
                
                try:
                    print(f"{Fore.YELLOW}Attempting to complete quest ID: {quest_id}")
                    # Make the POST request
                    response = requests.post(url, headers=headers, json=payload)
                    
                    # Check if the request was successful
                    if response.status_code == 201:
                        print(f"{Fore.GREEN}Successfully completed quest ID: {quest_id}")
                    elif response.status_code == 400 and "Quest already completed" in response.text:
                        print(f"{Fore.BLUE}Quest ID {quest_id} already completed")
                    else:
                        print(f"{Fore.RED}Failed to complete quest ID: {quest_id}")
                    
                    # Delay before next request (except for the last one)
                    if i < len(incomplete_quests) - 1:
                        print(f"{Fore.MAGENTA}Waiting 10 seconds before next request...")
                        time.sleep(10)
                    
                except Exception as e:
                    print(f"{Fore.RED}Error completing quest ID {quest_id}: {e}")
            
            print(f"{Fore.GREEN}All incomplete quests processed!")
        else:
            print(f"{Fore.GREEN}No incomplete quests to process!")
    else:
        print(f"{Fore.RED}No quests found in the response")

if __name__ == "__main__":
    complete_quests()
