import praw
import datetime

#Connects to Reddit's API and creates a Reddit object
#which allows me to perform various actions
reddit = praw.Reddit('MostActivePosters')

#Gets info
subreddit_name = input("Enter subreddit name: ")

#Creates subreddit instance of specified subreddit
subreddit = reddit.subreddit(subreddit_name)

#Retrieves all new posts from subreddit
posts = subreddit.new()
timeRange = datetime.timedelta(days=7) #Sets a time range of specified days
filteredPosts = []
for post in posts:
    #Checks if post was created between the current time and the specified range
    post_creation_date = datetime.datetime.fromtimestamp(post.created_utc)
    if (post_creation_date > (datetime.datetime.today() - timeRange)):
        filteredPosts.append(post)
    else:
        break

#Keeps track of how many posts each user made within the specified range
#Creates a list for each user
dictionary = {}
flairs = []
for flair in subreddit.flair.templates:
    flairs.append(flair['text'])

for post in filteredPosts:
    if post.author_flair_text not in flairs:
        dictionary[post.author] = []

#Uses list to keep track of all user's posts
for post in filteredPosts:
    for key in dictionary:
        if (post.author == key):
            dictionary[key].append(post)

#Prints out users and the number of their posts
sortedDict = dict(sorted(dictionary.items(), key=lambda item: len(item[1]), reverse=True))
topposters = ""
num = 1
for key in sortedDict:
    if num <= 5:
        try:
            topposters += f"{num}. {key.name}: {len(dictionary[key])} posts\n\n"
            num += 1
        except Exception:
            continue
    else:
        break

exit()
