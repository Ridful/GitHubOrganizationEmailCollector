import requests
import json
from lxml import html
from time import sleep

#headers = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
#base_url = "https://github.com/orgs/{organization_name}/people"

class GitHubOrg:
    
    def __init__(self, organization_name) -> None:
        self.org_name = organization_name
        self.full_url = f"https://github.com/orgs/{self.org_name}/people"
        self.org_members = []

    def printorgurl(self):
        print(self.full_url)


def get_github_org_content(organization_name):
    
    r = requests.get(url=organization_name)
    if r.status_code != 200:
        raise Exception(F"Failed to load page {organization_name}")
        
    return r.content
    
def fetch_members(url_content):
    
    # Parse the HTML content
    tree = html.fromstring(url_content)
    
    # XPath for the target elements
    members_xpath = '//*[@id="org-members-table"]/ul//*[starts-with(@id, "member-")]'
    
    # Extract the elements
    members = tree.xpath(members_xpath)
    
    # Print the results
    for member in members:
        member_id = member.get('id').replace("member-", "")
        print(f"Found member with ID: {member_id}")
        yield member_id
        

# Function to recursively search for the email key when login matches member_id
def find_all_emails(json_data, member_id, key):
    results = set()  # Use a set to store unique values
    if isinstance(json_data, dict):
        # Check if the current dictionary has a matching "login" key
        if json_data.get("login") == member_id:
            # If "email" key exists, add its value to the results
            if key in json_data:
                results.add(json_data[key])
        
        # Recursively search the dictionary
        for k, v in json_data.items():
            results.update(find_all_emails(v, member_id, key))
    elif isinstance(json_data, list):
        # Recursively search each item in the list
        for item in json_data:
            results.update(find_all_emails(item, member_id, key))
    return results

def try_get_member_email(member_id: str):
    #print(f"Hello there: {member_id}")
    sleep(5.5)
    try:
        gh_api_member_events = f"https://api.github.com/users/{member_id}/events"
        
        r = requests.get(url=gh_api_member_events)
        if r.status_code != 200:
            raise Exception(F"Failed to load page {gh_api_member_events}")
        
        member_events_json = r.json()
        
        try:
            unique_emails = find_all_emails(member_events_json, member_id, "email")
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            
        print(len(unique_emails))
        print(type(unique_emails))
        for email in unique_emails:
            print(f"Found: {email}")
            
        print("----------")
        #member_events_obj = json.load(r.content)
        
    except Exception as err:
        print(f"An error has occurred: {err}")
    
    print(gh_api_member_events)

def main():
    organization_name = ""
    ghorg = GitHubOrg(organization_name)

    res_content = get_github_org_content(ghorg.full_url)
    
    #print(type(res_content))
    if isinstance(res_content, bytes):
        ghorg.org_members.extend(list(fetch_members(res_content)))
    else:
        #print(type(res_content))
        print("no")
    
    print(len(ghorg.org_members))
    if len(ghorg.org_members) > 0:
        for member in ghorg.org_members:
            #print(f"Hola  -  {member}")
            try_get_member_email(member)
            pass
    
    print("done")

if __name__ == "__main__":
    
    main()