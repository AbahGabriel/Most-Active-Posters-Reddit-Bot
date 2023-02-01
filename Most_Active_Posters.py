import praw
import datetime
import os

#This bot can function without being a moderator

#Grabs Top N Posters of the Week and PMs a moderator with their usernames
def main():
    #Go to subreddit
    reddit = praw.Reddit('MostActivePosters')
    subreddit_name = 'test'
    subreddit = reddit.subreddit(subreddit_name)
    
    #Retrieve all posts made within the past week
    lastWeekPosts = getPostsMadeWithinPastWeek(subreddit)

    #Get author of each post and assign them a numberOfPosts value
    authorsAndPosts = setPostNumberForEachAuthor(lastWeekPosts)

    #Sorts dictionary in descending order
    authorsAndPosts = sortDictionaryInDescendingOrder(authorsAndPosts)

    #Keeps top N Users
    authorsAndPosts = keepTopNPosters(authorsAndPosts)

    #PMs mod with Top N Posters' names
    sendPMToMod(authorsAndPosts, reddit, subreddit_name)

def getPostsMadeWithinPastWeek(subreddit):
    #All new posts in the subreddit
    allNewPosts = subreddit.new()

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
    
def sortDictionaryInDescendingOrder(dictionary):
    print("Sorting users based on post count...")
    #Sorts dictionary according to the values (x[1])
    dictionary = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)
    return dictionary

def keepTopNPosters(authorsAndPosts):
    # Converts dict to tuple
    # Get first N items in dictionary
    authorTuple = tuple(authorsAndPosts)
    topNPosters = dict(list(authorTuple)[0: 5]) 

    return topNPosters

def sendPMToMod(authorsAndPosts, reddit, subreddit_name):
    modName = ""

    #Constructs subject content
    subject = f"r/{subreddit_name}: Top Posters Of The Week"

    #Constructs message content
    message = ""
    i = 1
    for author in authorsAndPosts:
        message += f"{i}. {author}: {authorsAndPosts[author]} posts\n"
        i += 1
    
    reddit.redditor(modName).message(subject=subject, message=message)

main()
