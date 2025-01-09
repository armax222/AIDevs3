# Standard library imports
import requests
from collections import deque

# Local imports
from utilities.common import AIDevsClient
from utilities.config import AI_DEVS_API_KEY, S03E05_TASK_URL, S03E05_REPORT_URL

# =========================================================
# Configuration
# =========================================================
TASK_NAME = "connections"
DB_TASK_NAME = "database"
API_URL = S03E05_TASK_URL
SUBMIT_URL = S03E05_REPORT_URL

# =========================================================
# Data Fetching Functions
# =========================================================
def fetch_data(api_url, api_key):
    """Fetch users and connections data from MySQL."""
    users_query = {
        "task": DB_TASK_NAME,
        "apikey": api_key,
        "query": "SELECT * FROM users"
    }
    connections_query = {
        "task": DB_TASK_NAME,
        "apikey": api_key,
        "query": "SELECT * FROM connections"
    }
    
    users_response = requests.post(api_url, json=users_query).json()
    connections_response = requests.post(api_url, json=connections_query).json()
    
    return {
        "users": users_response["reply"],
        "connections": connections_response["reply"]
    }

# =========================================================
# Graph Building Functions
# =========================================================
def build_graph(data):
    """Build user mappings and connection graph."""
    id_to_username = {}
    username_to_id = {}
    
    for user in data["users"]:
        user_id = int(user["id"])
        user_name = user["username"]
        id_to_username[user_id] = user_name
        username_to_id[user_name.lower()] = user_id
    
    graph = {}
    for conn in data["connections"]:
        src = int(conn["user1_id"])
        tgt = int(conn["user2_id"])
        graph.setdefault(src, []).append(tgt)
    
    return id_to_username, username_to_id, graph

# =========================================================
# Path Finding Functions
# =========================================================
def bfs_shortest_path(graph, start_id, goal_id):
    """Find shortest path between two users using BFS."""
    visited = set()
    queue = deque([[start_id]])

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == goal_id:
            return path

        if node not in visited:
            visited.add(node)
            neighbors = graph.get(node, [])
            for neighbor in neighbors:
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return []

# =========================================================
# Main Execution
# =========================================================
def main():
    """Main execution function."""
    # Initialize client
    client_aidevs = AIDevsClient()
    
    # Fetch data
    data = fetch_data(API_URL, AI_DEVS_API_KEY)
    print("Users:", len(data["users"]))
    print("Connections:", len(data["connections"]))
    
    # Build graph
    id_to_username, username_to_id, graph = build_graph(data)
    
    # Find path
    start_username = "Rafał"
    target_username = "Barbara"
    
    start_id = username_to_id.get(start_username.lower())
    target_id = username_to_id.get(target_username.lower())
    
    if start_id is None or target_id is None:
        print(f"No user found: {start_username} or {target_username}")
        return
    
    path_ids = bfs_shortest_path(graph, start_id, target_id)
    if not path_ids:
        print(f"No path found between {start_username} and {target_username}")
        return
    
    path_usernames = [id_to_username[user_id] for user_id in path_ids]
    result_string = ", ".join(path_usernames)
    print("Shortest path:", result_string)
    
    print(client_aidevs.submit_answer(
        answer={"task": TASK_NAME, "apikey": AI_DEVS_API_KEY, "answer": result_string},
        submit_url=SUBMIT_URL
    ))

if __name__ == "__main__":
    main()