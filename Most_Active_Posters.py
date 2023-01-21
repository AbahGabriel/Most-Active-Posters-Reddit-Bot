import praw
import datetime

#Connects to Reddit's API and creates a Reddit object
#which allows me to perform various actions
reddit = praw.Reddit('MostActivePosters')

#Gets info
subreddit_name = input("Enter subreddit name: ")
time_range = float(input("Time period (in days): "))

#Creates subreddit instance of specified subreddit
subreddit = reddit.subreddit(subreddit_name)

#Retrieves all new posts from subreddit
posts = subreddit.new()
timeRange = datetime.timedelta(days=time_range) #Sets a time range of 7 days
filteredPosts = []
for post in posts:
    #Checks if post was created between the current time and 7 days ago
    post_creation_date = datetime.datetime.fromtimestamp(post.created_utc)
    if (post_creation_date > (datetime.datetime.today() - timeRange)):
        filteredPosts.append(post)
    else:
        break

#Keeps track of how many posts each user made within the past week
#Creates a list for each user
dictionary = {}
for post in filteredPosts:
    dictionary[post.author] = []

#Uses list to keep track of all user's posts
for post in filteredPosts:
    for key in dictionary:
        if (post.author == key):
            dictionary[key].append(post)

#Prints out users and the number of their posts
sortedDict = dict(sorted(dictionary.items(), key=lambda item: len(item[1]), reverse=True))
for key in sortedDict:
    print(f"{key.name}: {len(dictionary[key])} posts")
