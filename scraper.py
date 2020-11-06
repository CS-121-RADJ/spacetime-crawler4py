import re
import requests
import json
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse

#global variable keeps track of number of urls that we have scraped/number of txt files of token data in urlTokenData 
urlNum = 0

def scraper(url, resp):
    # parsed the pages and compare it with document store
    # if similar enough return emptry list  `return []`
    cleanCloseDups = search(url, resp)
    return [link for link in cleanCloseDups if is_valid(link)]

#this function is a similarity search that only returns the next links if current url is not similar to any document that has so far already been scraped
def search(url, scraperResp):
    #parse through the url text
    # print(scraperResp.raw_response.content)
    soup = BeautifulSoup(scraperResp.raw_response.content, features="html.parser", from_encoding="iso-8859-1")
    text = soup.get_text()
    
    #copied code from recorder.py to get a list of all tokens in the url
    # Mapping all the words from the line to be lowercase while also spiting the word into a list by whitespace
    resp_words = list(map(lambda x: x.lower().strip(), text.split(' ')))
    # filtering out all the non alphanumeric chars
    resp_words = list(map(lambda word: ''.join(list(filter(lambda x: x.isalnum(), [char for char in word]))), resp_words))
    resp_words = list(filter(lambda word: len(word) > 1, resp_words))

    #remove duplicates from our list of tokens
    tokenSet = set(resp_words)
    #convert back into a list so we can json.dump it on line 65(got error when we tried json.dump with a et)
    tokenList = list(tokenSet)
    #number of tokens of our current url
    url_tokens = len(tokenSet)
    #boolean value that tells us whether to get next links or not, if extract still == true after the loop we will extract next links
    extract = True
    #creates empty list of next links to return at end if cuurent url is not similar to any previously scraped url
    nxtLinks = list()

    global urlNum

    #iterate through all the previous urlTokenData txt files which contain all tokens in previously scraped urls and add each token into a list of tokens
    for i in range(urlNum):
        #txt file of url we are compaing our current url to that contains all tokens of previously scraped url
        comparefile = open("urlTokenData/url{}.txt".format(i), 'r')
        #puts all tokens from above file into a list
        compareFileTknList = [line.split(',') for line in comparefile.readlines()]
        #integer to keep track of how many of the tokens are the same
        same_token_ct = 0

        #iterate through the list of previously scraped url's tokens and check if tokens are in the current url tokenSet
        for j in range(len(compareFileTknList)):
            if compareFileTknList.index(j) in tokenSet:
                #if token from previously scraped url found in current url tokenSet increment same_tkn_ct by 1
                same_token_ct+=1
        #if we find a similar url in the database, set extract to false so we know not to get next links
        if same_token_ct / url_tokens > 0.9: 
            extract = False
            #exits loop because current url has been deemed a similarity, no reason to keep checking
            break

    #if no similar urls found, extract will still == true so we get the next links of the current url and put into list
    if extract == True:
        nxtLinks = extract_next_links(url, scraperResp)

    #add to utlTokenData folder a txt file containing all tokens in current url named url{currentNumberUrl}.txt Example: first url called 'url1.txt', next url called 'url2.txt'... and so on
    #now for url we scrape, tokens for this url are in the database of previous url tokens to check for similarity
    fileName = "urlTokenData/url{}.txt".format(urlNum)
    with open(fileName, 'w') as outfile:
        json.dump(tokenList, outfile)
    #increment 1 to global variable urlNum
    urlNum+=1
    
    #if current url similar to a previously scraped url, list will be empty, if not, list will contain next links
    return nxtLinks

def extract_next_links(url, resp):
    return_list = []

    if (resp.raw_response is None or resp.status != 200):
        return list()
    # Parse the html but only parse the URLs to make it more effiecent
    # SoupStrainer code found https://www.crummy.com/software/BeautifulSoup/bs4/doc/#soupstrainer
    soup = BeautifulSoup(resp.raw_response.content, parse_only=SoupStrainer("a"), features="html.parser", from_encoding="iso-8859-1")
    for link in soup:
        if link.has_attr("href") and is_valid(link["href"]):
            return_list.append(link["href"])

    return return_list

def is_valid(url):
    valid_sites = [
        ".ics.uci.edu",
        ".cs.uci.edu",
        ".informatics.uci.edu",
        ".stat.uci.edu",
        "today.uci.edu/department/information_computer_sciences"
    ]
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        uci_link = False
        for base_link in valid_sites:
            if(base_link in parsed.netloc + parsed.path):
                uci_link = True

        if(not uci_link):
            return False

        if('/pdf/' in parsed.path.lower()):
            return False

        # Being used to detect calaneder links that go on for too long
        if('wics' in parsed.netloc.lower() and bool(re.search('/events/.*?/', parsed.path.lower()))):
            return False

        if('today' in parsed.netloc.lower() and bool(re.search('/calender/.*?/', parsed.path.lower()))):
            return False
        
        # There are fragments that that just give the browser direction and can be thrown out
        if(parsed.fragment != ''):
            return False

        # Queries can make too many pages that are too similiar so they will be thrown out
        if(parsed.query != ''):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise