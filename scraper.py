import re
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    #links = search(url, links, resp)
    return [link for link in links if is_valid(link)]

#this function is a similarity search that returns an updated list of the next links without links that are too similar(90% token similarity)
def search(url, nextLinks, scraperResp):
    #parse through the url text
    soup = BeautifulSoup(scraperResp, features="html.parser", from_encoding="iso-8859-1")
    text = soup.get_text()

    #initializes list to return at end of function which contains all next links with no similarities
    linksNoSimilarities = []
    #number of tokens in our url
    url_tokens = 0  
    #dictionary that will keep track of all tokens in our url and how many times they show up
    tokenDict = {} 

    #copied code from recorder.py to get a list of all tokens in the url
    # Mapping all the words from the line to be lowercase while also spiting the word into a list by whitespace
    resp_words = list(map(lambda x: x.lower().strip(), text.split(' ')))
    # filtering out all the non alphanumeric chars
    resp_words = list(map(lambda word: ''.join(list(filter(lambda x: x.isalnum(), [char for char in word]))), resp_words))
    resp_words = list(filter(lambda word: len(word) > 1, resp_words))

    #iterate through list of tokens if new token found put the new token as a key in dictionary and urlTokens++
    for word in resp_words:
        if word in tokenDict.keys() == False:
            tokenDict.add(word, 1)
            url_tokens+=1
        else:
            tokenDict[word]+=1

    #iterate through all of the nextLinks
    for nextLinkUrl in nextLinks:
        #parse through the nextLink url text
        nxt_link_soup = BeautifulSoup(resp, features="html.parser", from_encoding="iso-8859-1")
        nxt_link_text = nxt_link_soup.get_text()

        #copied code from recorder.py to get a list of all tokens in the url
         # Mapping all the words from the line to be lowercase while also spiting the word into a list by whitespace
        nxt_link_resp_words = list(map(lambda x: x.lower().strip(), nxt_link_text.split(' ')))
        # filtering out all the non alphanumeric chars
        nxt_link_resp_words = list(map(lambda word: ''.join(list(filter(lambda x: x.isalnum(), [char for char in word]))), resp_words))
        nxt_link_resp_words = list(filter(lambda word: len(word) > 1, resp_words))

        #int that keeps track of number of tokens in the url
        same_token_ct = 0

        #a set of all tokens in the url of the next link
        nxt_link_token_set = set(next_link_resp_words)

        for token in nxt_link_token_set:
        #   if tokenDict contains the token in nxtLinkTokenSet as a key increment
            if tokenDict.has_key(token):
                    same_token_ct+=1
        #if 90% of tokens are the same do not add the url to the new list
        if same_token_ct >= (.9 * url_tokens): 
            continue
        else:
            linksNoSimilarities.add(nextLinkUrl)
    #returns the new list of next Links with no similarities
    return linksNoSimilarities

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
            if(base_link in parsed.netloc):
                uci_link = True

        if(not uci_link):
            return False

        if('/pdf/' in parsed.path.lower()):
            return False

        # Being used to detect calaneder links that go on for too long
        if('wics' in parsed.netloc.lower() and bool(re.search('/events/.*?/', parsed.path.lower()))):
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