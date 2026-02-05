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
    
    # Check if the API call was successful
    if response.status_code != 200:
        raise Exception(f"GitHub API failed with status {response.status_code}")

    res_json = response.json()
    if "data" not in res_json or res_json["data"]["user"] is None:
        raise Exception(f"Could not fetch data for user {USERNAME}. Check your Token.")

    data = res_json["data"]["user"]
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

    stats_markdown = f"""
| Stat | Count |
| :--- | :--- |
| ⭐ Total Stars | {stats['Stars']} |
| 🚀 Total Commits | {stats['Commits']} |
| ⚓ Pull Requests | {stats['PRs']} |
| 🛠️ Issues | {stats['Issues']} |
"""
    
    # Ensure these are EXACTLY as written below
    start_tag = ""
    end_tag = ""
    
    # Reconstruct the README with a guaranteed newline
    new_content = parts[0] + start_tag + "\n" + stats_markdown + "\n" + end_tag + after_start[1]
    
    parts = content.split(start_tag)
    if len(parts) < 2:
        print(f"Error: Could not find {start_tag}")
        return
        
    after_start = parts[1].split(end_tag)
    if len(after_start) < 2:
        print(f"Error: Could not find {end_tag}")
        return

    # Reconstruct the README with the new stats in the middle
    new_content = parts[0] + start_tag + "\n" + stats_markdown + "\n" + end_tag + after_start[1]
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    try:
        stats_data = get_stats()
        update_readme(stats_data)
        print("Successfully updated README.md with native stats!")
    except Exception as e:
        print(f"Failed to update: {e}")
