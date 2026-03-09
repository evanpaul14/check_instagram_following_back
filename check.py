import json

following_list = input("Path to following.json: ")
followers_list = input("Path to followers_1.json: ")

with open(following_list) as f:
    following = json.load(f)['relationships_following']
with open(followers_list) as f:
    followers = json.load(f)

print(following[0]['title'])
following_usernames = [f['title'] for f in following]
followers_usernames = [f['string_list_data'][0]['value'] for f in followers]
not_following_back = [f for f in following_usernames if f not in followers_usernames]

count = 1
for user in not_following_back:
    print(f"{count}. {user} link: https://www.instagram.com/{user}/") 
    count += 1