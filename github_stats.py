import os
import requests

# Your Secret Token
TOKEN = os.getenv("GH_STATS_TOKEN")
USERNAME = "samwaseee"

def get_stats():
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
        }
        repositoriesContributedTo(first: 100) {
          totalCount
        }
        pullRequests(first: 1) {
          totalCount
        }
        issues(first: 1) {
          totalCount
        }
        repositories(first: 100, ownerAffiliations: OWNER) {
          nodes {
            stargazerCount
          }
        }
      }
    }
    """
    headers = {"Authorization": f"bearer {TOKEN}"}
    response = requests.post("https://api.github.com/graphql", 
                             json={"query": query, "variables": {"login": USERNAME}}, 
                             headers=headers)
    
    data = response.json()["data"]["user"]
    stars = sum(repo["stargazerCount"] for repo in data["repositories"]["nodes"])
    
    return {
        "Commits": data["contributionsCollection"]["totalCommitContributions"],
        "Stars": stars,
        "PRs": data["pullRequests"]["totalCount"],
        "Issues": data["issues"]["totalCount"]
    }

def update_readme(stats):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Define the template for your native stats card
    stats_markdown = f"""
| Stat | Count |
| :--- | :--- |
| ⭐ Total Stars | {stats['Stars']} |
| 🚀 Total Commits | {stats['Commits']} |
| ⚓ Pull Requests | {stats['PRs']} |
| 🛠️ Issues | {stats['Issues']} |
"""
    
    # EXACT tags that match your README markers
    start_tag = ""
    end_tag = ""
    
    # This logic splits the README and replaces only the section between the tags
    parts = content.split(start_tag)
    if len(parts) < 2:
        print("Start tag not found in README.md")
        return
        
    after_start = parts[1].split(end_tag)
    if len(after_start) < 2:
        print("End tag not found in README.md")
        return

    new_content = parts[0] + start_tag + "\n" + stats_markdown + "\n" + end_tag + after_start[1]
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    stats_data = get_stats()
    update_readme(stats_data)