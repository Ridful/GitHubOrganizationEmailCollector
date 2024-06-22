import requests
import json
from lxml import html
from time import sleep
import re

theheaders = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1)'}

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

def get_email_from_patch_url(patch_url):
    try:
        print(patch_url)
        sleep(4.5)
        
        r = requests.get(url=patch_url)
        if r.status_code != 200:
            raise Exception(F"Failed to load page {patch_url}")
        
        match = re.search(r'From: .* <(.*?)>', r.text)
        
        if match:
            email = match.group(1)
            print("Email address:", email)
            return email
        else:
            print("No email address found")
            return None
        
    except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
    except Exception as err:
        print(f"An error has occurred: {err}")

        
def get_member_repo_branch_name(member_repo_url):
    try:
        sleep(2.25)
        member_repo_commits_url = member_repo_url + "/commits"
        
        r = requests.get(url=member_repo_commits_url, headers=theheaders)
        if r.status_code != 200:
            raise Exception(F"Failed to load page {member_repo_commits_url}")
        
        tree = html.fromstring(r.content)
        
        # Defines where in the html the branch name is
        branch_name_xpath = '//*[@id="branch-picker-commits"]/span/span[1]/div/div[2]/span/text()[2]'
        branch_name = tree.xpath(branch_name_xpath)[0]
        #print(branch_name)
        
        #xpath_expr = "//*[contains(@id, ':-list-view-container')]/ul//*[contains(@id, ':-list-view-node-:')]/div[1]/h4/span/a"
        # Extract the matching elements
        #elements = tree.xpath(xpath_expr)
        
        # Iterate over the found elements and print their href attribute and text content
        #for element in elements:
        #    member_commit_patch = "https://github.com" + element.get("href")
        #    print(f'Link: \"{member_commit_patch}\".')
        
        sleep(1)
        return branch_name
                    
    except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
    except Exception as err:
        print(f"An error has occurred: {err}")

def try_get_member_repos(member_id: str):
    sleep(5.5)
    try:
        gh_org_member_repos = f"https://github.com/{member_id}?tab=repositories&q=&type=source"
        
        r = requests.get(url=gh_org_member_repos)
        if r.status_code != 200:
            raise Exception(F"Failed to load page {gh_org_member_repos}")
        
        member_repos_content = r.content
        
        tree = html.fromstring(member_repos_content)
        
        repos_xpath = '//*[@id="user-repositories-list"]/ul/li/div[1]/div[1]/h3/a'
        repo_elements = tree.xpath(repos_xpath)
        
        repositories_urls = []
        for repo in repo_elements:
            repo_url = repo.get('href')
            repositories_urls.append(repo_url)
        
        #if len(repositories_urls) > 0:
        for repo_url in repositories_urls:
            repo_url = "https://github.com" + repo_url
            print(f"URL: {repo_url}")
            yield repo_url
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as err:
        print(f"An error has occurred: {err}")
    
    print("-----------")


def main():
    #runelite  #Maldev-Academy
    #organization_name = "Maldev-Academy"
    organization_name = "runelite"
    
    ghorg = GitHubOrg(organization_name)

    res_content = get_github_org_content(ghorg.full_url)
    
    if isinstance(res_content, bytes):
        ghorg.org_members.extend(list(fetch_members(res_content)))
    else:
        print("no")
    
    print(len(ghorg.org_members))
    if len(ghorg.org_members) > 0:
        
        # Get all repos created by each and every Member of the organization.
        member_repos_urls = []
        for member in ghorg.org_members:
            member_repos_urls.extend(list(try_get_member_repos(member)))
        
        repo_branch_patch_url_list = []
        for member_repo_url in member_repos_urls:
            #print(f"try_get_member_email_from_repo : URL: {member_repo_url}")
            member_repo_branch_name = get_member_repo_branch_name(member_repo_url)
            
            member_repo_commit_branchname_patch_url = f"{member_repo_url}/commit/{member_repo_branch_name}.patch"
            print(member_repo_commit_branchname_patch_url) ######
            
            repo_branch_patch_url_list.append(member_repo_commit_branchname_patch_url)
            
        print("söt")
        unique_emails = set()
        for patch_url in repo_branch_patch_url_list:
            res = get_email_from_patch_url(patch_url)
            print(f"Email: {res}  |  URL/Repository: {patch_url}")
            unique_emails.add(res)
            
        print(unique_emails)
        for eemail in unique_emails:
            print(eemail)
    print("done")

if __name__ == "__main__":
    
    main()