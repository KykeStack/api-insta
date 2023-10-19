from pathlib import Path, PurePath
from typing import List, Optional, Any
from pydantic import BaseModel
import instaloader
import time
import random
import csv
import os
import sys 
import random

CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
class FunctionStatus(BaseModel):
    status: bool
    content: Optional[Any] = None
    
ROOT = str(Path().cwd())
L = instaloader.Instaloader()
CREDENTIALS_FILE_PATH =  PurePath(ROOT, "content/credentials.txt") 
relevant_keys = [
    'username',
    'full_name',
    'followers',
    'followees',
]

# 'followed_by_me',
# 'followed_me',
# 'external_url',
# 'business_email',
# 'business_category_name'
# 'business_phone_number'

def generate_string(length):
    result = ""
    characters_length = len(CHARACTERS)
    for _ in range(length):
        result += CHARACTERS[random.randint(0, characters_length - 1)]
    return result

def genrate_pat_csv():
    route = f"static/follow_list{generate_string(10)}.csv"
    path = PurePath(ROOT, route)
    return path, route

def save_credentials(username: str, password: str, path: str):
    with open(path, 'w') as file:
        file.write(f"{username}\n{password}")

def save_to_csv(follow_list, csv_file, relevant_keys):
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=relevant_keys)
        writer.writeheader()

        # Write the data from follow_list
        for item in follow_list:
            relevant_data = {key: item.get(key) for key in relevant_keys}
            # Write the relevant data as a row
            writer.writerow(relevant_data)

def load_credentials(path: str):
    if not os.path.exists(path):
        return None
    
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()
    return None

def prompt_credentials(path: str):
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password, path)
    return username, password

def scrape_followers(username, user_limit, follow_list, filter_by_followers):
    profile = instaloader.Profile.from_username(L.context, username)
    count = 0
    max_await = 20
    for followee in profile.get_followers():
        try:
            if count == user_limit: break
            print(f'data_object {count}')
            print(f'FIRST AWAIT {max_await}')
            count = count + 1
            max_await = max_await - 1
            
            if max_await == 0:
                time.sleep(random.randint(10)) 
                
            time.sleep(random.randint(1, 2)) 
            
            if followee.followers < filter_by_followers: continue
            
            data_object = followee.__dict__['_node']
            data_object['followees'] = followee.followees
            data_object['followers'] = followee.followers
            data_object['followed_by_me'] = followee.followed_by_viewer
            data_object['followed_me'] = followee.follows_viewer
            follow_list.append(data_object)
            
        except Exception as error:
            print('Error: ', error)
            continue


def scrape_from_api(
    *, 
    username: str,
    password: str,
    profiles: List[str], 
    minimun: int,
    filter: int
) -> FunctionStatus:
    follow_list = []
    if (profiles[0] == ''): profiles[0] = username
    try: 
        CSV_FILE_PATH = genrate_pat_csv()
        L.login(username, password)
        
        for user in profiles:
            user = user.strip()
            print(f"Searching for user: {user}")
            scrape_followers(user, minimun, follow_list, filter)
            
        save_to_csv(follow_list, CSV_FILE_PATH[0], relevant_keys)
        
        return FunctionStatus(status=True, content=CSV_FILE_PATH[1])
    
    except Exception as error: 
        print(f"Error on scrape_from_api: {error}")
        return FunctionStatus(status=False, content=str(error))

def scrape():
    CSV_FILE_PATH = genrate_pat_csv()
    print(CSV_FILE_PATH)
    follow_list = []
    credentials = load_credentials(CREDENTIALS_FILE_PATH)

    if credentials is None:
        username, password = prompt_credentials(CREDENTIALS_FILE_PATH)
    else:
        username, password = credentials
    try:
        user_input = int(input('[Required] - How many followers do you want to scrape (100-2000 recommended): '))
        # If the input is successfully converted to an integer, it's an integer.
        print(f"Reading number of users: {user_input}")
    except ValueError:
        print("Input is not an Number. Please enter a valid Number.")
        sys.exit()
    usernames = input("Enter the OTHER Instagram usernames you want to scrape (separated by commas): ").split(",")
    try:
        filter_by_followers = int(input("Enter the minimum number of followers: "))
        # If the input is successfully converted to an integer, it's an integer.
        print(f"Filtering by number of followers: {filter_by_followers}")
    except ValueError:
        print("Input is not an Number. Please enter a valid Number.")
        sys.exit()

    if (usernames[0] == ''): usernames[0] = username
    L.login(username, password)
    for user in usernames:
        user = user.strip()
        print(f"Searching for user: {user}")
        scrape_followers(user, user_input, follow_list, filter_by_followers)
        
    save_to_csv(follow_list, CSV_FILE_PATH[0], relevant_keys)

if __name__ == '__main__':
    TIMEOUT = 15
    scrape()
