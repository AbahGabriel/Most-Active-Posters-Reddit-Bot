import praw
import itertools
import datetime
import prawcore.exceptions
import os
import re

#Ensure that this bot is a moderator, or it won't work
def main():
    #File path
    path = "C:\\Users\\Gabriel\\source\\repos\\API_Practice\\TestTopPosters\\flairs.txt"

    #Go to subreddit
    reddit = praw.Reddit('MostActivePosters')
    subreddit_name = 'babesfrom1996'
    subreddit = reddit.subreddit(subreddit_name)
    
    #Retrieve all posts made within the past week
    lastWeekPosts = getPostsMadeWithinPastWeek(subreddit)

    #Get author of each post and assign them a numberOfPosts value
    authorsAndPosts = setPostNumberForEachAuthor(lastWeekPosts)

    #Deletes flairs used for previous week
    #Had to place it here to allow it to accept authorsAndPosts as an argument
    deletePreviousFlairs(subreddit, reddit, path, authorsAndPosts)

    #Filter out authors who currently have flairs
    authorsAndPosts = removeFlairedAuthors(authorsAndPosts, lastWeekPosts)

    #Sorts dictionary in descending order
    authorsAndPosts = sortDictionaryInDescendingOrder(authorsAndPosts)

    #Keeps top 5 Users
    authorsAndPosts = keepTopFivePosters(authorsAndPosts)

    #Create five new flairs labelled: "#{num} Poster for Week {currentDay}"
    #Note - Account must be a moderator for this part
    createdFlairs = createNewFlairs(subreddit)

    #Sets user flairs
    setUserFlairs(authorsAndPosts, createdFlairs, subreddit)

    #Saves the newly created flairs
    saveNewFlairs(path, createdFlairs)

def getPostsMadeWithinPastWeek(subreddit):
    #All new posts in the subreddit
    allNewPosts = subreddit.new()

    #Posts within past week
    timeRange = datetime.timedelta(days=7)
    filteredPosts = []
    for post in allNewPosts:
        #Checks if post was created between the current time and the past week
        post_creation_date = datetime.datetime.fromtimestamp(post.created_utc)
        if (post_creation_date > (datetime.datetime.today() - timeRange)):
            filteredPosts.append(post)
        else:
            break

    return filteredPosts

def setPostNumberForEachAuthor(lastWeekPosts):
    dictionary = {}

    print("Getting posts from past week...")
    #Counts number of posts for each author
    for post in lastWeekPosts:
        if post.author in dictionary:
            dictionary[post.author] += 1
        else:
            dictionary[post.author] = 1
    
    return dictionary

def deletePreviousFlairs(subreddit, reddit, path, authorsAndPosts):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return
    
    print("Deleting flairs from past week...")
    #Clears user flairs
    userList = []
    for author in authorsAndPosts:
        userList.append(author)
    deleteUserFlairs(userList, subreddit)

    #Deletes flairs from subreddit
    with open(path, 'r') as file_in:
        for line in file_in: #Each line is a flair
            subreddit.flair.templates.delete(line[158:194])

    #Clears file
    with open(path, 'r+') as file_in:
        file_in.truncate(0)
           
def deleteUserFlairs(userList, subreddit):
    subreddit.flair.update(userList, text='')

def removeFlairedAuthors(authorDictionary, lastWeekPosts):
    #Check if any author currently has a flair
    for post in lastWeekPosts:
        if post.author_flair_text != (None or ''):
            try:
                del authorDictionary[post.author] #Remove if yes
            except KeyError: #Handles duplicate posters
                continue
    
    return authorDictionary
    
def sortDictionaryInDescendingOrder(dictionary):
    print("Sorting users based on post count...")
    #Sorts dictionary according to the values (x[1])
    dictionary = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)
    return dictionary

def keepTopFivePosters(authorsAndPosts):
    # Converts dict to tuple
    # Get first N items in dictionary
    authorTuple = tuple(authorsAndPosts)
    topFivePosters = dict(list(authorTuple)[0: 5]) 

    return topFivePosters

def createNewFlairs(subreddit):
    print("Creating new flairs...")
    #Creates five new flairs that can only be assigned by moderators
    for i in range(1, 6):
        text = f'#{i} Poster for Week {datetime.datetime.today()}'
        text = re.sub("\..*$","",text)
        subreddit.flair.templates.add(text=text,
        allowable_content='text',
        mod_only=True,
        text_editable=False)
    
    #Tracks created flairs for future identification
    newFlairs = []
    for flair in subreddit.flair.templates:
        if "Poster for Week" in flair['text']:
            newFlairs.append(flair)
    newFlairs = sorted(newFlairs, key=lambda i: i['text'])

    return newFlairs

def setUserFlairs(authorsAndPosts, createdFlairs, subreddit):
    print("Setting flairs...")
    #Sets flairs for top 5 posters, in order
    i = 0
    for author in authorsAndPosts:
        if i > 5:
            break
        text = f'#{i+1} Poster for Week {datetime.datetime.today()}'
        text = re.sub("\..*$","",text),
        subreddit.flair.set(author.name, text=text,flair_template_id=createdFlairs[i]['id'])

def saveNewFlairs(path, createdFlairs):
    if not os.path.exists(path):
        open(path, "w").close()

    for flair in createdFlairs:
        with open(path, 'a') as openFile:
            openFile.write(f'{flair}\n')

main()
