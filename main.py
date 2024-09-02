from dateutil import parser
from datetime import datetime, timezone
import requests
import pandas as pd
import time

GITHUB_TOKEN = "PUT_YOUR_TOKEN_HERE"
GITHUB_GRAPHQL_API_URL = "https://api.github.com/graphql"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

query = """
query($cursor: String) {
  search(query: "stars:>1000", type: REPOSITORY, first: 25, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        name
        stargazerCount
        owner {
          login
        }
        createdAt
        pullRequests(states: MERGED) {
          totalCount
        }
        releases {
          totalCount
        }
        updatedAt
        primaryLanguage {
          name
        }
        issues {
          totalCount
        }
        closedIssues: issues(states: CLOSED) {
          totalCount
        }
      }
    }
  }
}
"""

def run_query(query, variables):
    response = requests.post(GITHUB_GRAPHQL_API_URL, json={'query': query, 'variables': variables}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run and returned code: {response.status_code}. Text: {response.text}")

def find_string_in_list(lst, string):
    try:
        # Return the index if the string is found in the list
        return lst.index(string)
    except ValueError:
        # Return None if the string is not found
        return None

repositories_data = []
cursor = None  # Cursor para paginação
progress = 0
current_time = datetime.now(timezone.utc)
language_list = []

while progress < 1000:
    variables = {"cursor": cursor}
    result = run_query(query, variables)
    progress += 25
    print(f"({(progress/1000) * 100}% Progress) Running query with cursor: {cursor}")
    repositories = result["data"]["search"]["nodes"]
    
    # Processar os dados de cada repositório e adicionar à lista
    for repo in repositories:
        primary_language = repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else None
        language_index_on_list = find_string_in_list(language_list, primary_language) if (primary_language is not None and len(language_list) != 0)  else None

        if language_index_on_list is None and primary_language not in language_list and primary_language is not None:
            language_index_on_list = len(language_list)
            language_list.append(primary_language)
        repo_data = {
            "name": repo["name"],
            "owner": repo["owner"]["login"],
            "stargazerCount": repo["stargazerCount"],
            "created_at": repo["createdAt"],
            "time_since_created_at_in_seconds": (current_time - parser.parse(repo["createdAt"])).total_seconds(),
            "pull_requests_accepted": repo["pullRequests"]["totalCount"],
            "releases_count": repo["releases"]["totalCount"],
            "last_updated": repo["updatedAt"],
            "current_date": current_time,
            "time_since_last_update_in_seconds": (current_time - parser.parse(repo["updatedAt"])).total_seconds(),
            "primary_language": primary_language,
            "primary_language_mapping": int(language_index_on_list) if primary_language is not None else None,
            "total_issues": repo["issues"]["totalCount"],
            "closed_issues": repo["closedIssues"]["totalCount"],
        }
        repositories_data.append(repo_data)
    
    if result["data"]["search"]["pageInfo"]["hasNextPage"]:
        cursor = result["data"]["search"]["pageInfo"]["endCursor"]
        time.sleep(8)
    else:
        with open("language_list.txt", "w") as outfile:
            outfile.write("\n".join(language_list))
        print("Dados de linguagens salvos em 'language_list.txt'.")
        top_ten_most_popular_languages = ["JavaScript", "Python", "TypeScript", "Java", "C#", "C++", "PHP", "C", "Shell", "Go"] # Ordenado da mais popular à menos popular
        most_popular_languages = [str(language_list.index(language)) for language in top_ten_most_popular_languages]
        with open("most_popular_languages_indexes.txt", "w") as outfile:
            outfile.write("\n".join(most_popular_languages))
        print("Indexes das linguagens mais populares salvos em 'most_popular_languages_indexes.txt'.")
        break

# Converter a lista de dados em um DataFrame do pandas
df = pd.DataFrame(repositories_data)

# Calcular o percentual de issues fechadas
df['closed_issues_ratio'] = df['closed_issues'] / df['total_issues']

# Salvar o DataFrame em um arquivo CSV
df.to_csv('github_repositories_data.csv', index=False)

print("Dados salvos em 'github_repositories_data.csv'.")
