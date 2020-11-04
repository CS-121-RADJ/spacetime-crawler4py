import re
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    #links = search(url, links, resp)
    return [link for link in links if is_valid(link)]


def search(url, nextLinks, scraperResp):
    linksNoSimilarities = []
    #number of tokens in our url
    urlTokens = 0  
    #dictionary of all tokens in our url
    tokenDict = {} 
    #parse url if new token found put the new token as a key in dictionary and urlTokens++

    #iterate through all of the nextLinks
    for nextLinkUrl in the nextLinks:
        #int that keeps track of number of tokens in the url
        int sameTokenCt = 0

        #nxtLinkTokenSet = [] a set of every token in the comparison url

        for token in nxtLinkTokenSet:
        #   if tokenDict contains the token in nxtLinkTokenSet as a key increment
            if tokenDict.has_key(token)
                    sameTokenCt+=1
        #if 90% of tokens are the same do not add the url to the new list
        if sameTokenCt >= (.9 * urlTokens) 
            continue
        else
            linksNoSimilarities.add(nextLinkUrl)
    #returns the new list of nextLinks with no similarities
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