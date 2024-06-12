import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Stores states that we haven't explored yet
    # Also defines our strategy for exploration
    # In this case we are going DFS
    frontier = QueueFrontier()

    # Store the initial state as a Node
    start_node: Node = Node(
        state=source,
        parent=None,
        action=None
    )

    # Add initial state to frontier to explore
    frontier.add(start_node)

    # Dictionaries of {person_id: Node}
    # We use this to check what states we've already explored
    nodes_db: dict = {}

    # We loop until we no longer have any states to explore
    while not frontier.empty():
        # Retrieve state to explore
        current: Node = frontier.remove()

        # Store state in nodes_db if it hasn't been explored yet
        if current.state not in nodes_db:
            nodes_db[current.state] = current

        # If the state we are exploring is our target, we stop the loop
        if current.state == target:
            break

        neighbors = neighbors_for_person(current.state)

        # We loop through each neighbor and add it to the frontier to explore later
        for neighbor in neighbors:
            # Avoid exploring the same state more than once
            if neighbor[1] in nodes_db:
                continue

            # Store state as a node
            next_node: Node = Node(
                state=neighbor[1],
                parent=current.state,
                action=neighbor[0]
            )

            # Add state to the frontier
            frontier.add(next_node)

            # Store state in nodes_db
            nodes_db[next_node.state] = next_node

    # Since we add all our explored state in nodes_db,
    # we can be sure that if we haven't explored the target,
    # there is no possible path to it from the source
    if target not in nodes_db:
        return None

    # We backtrack starting from the target state
    current: Node = nodes_db[target]

    ret = []

    # We loop until we are back to our initial state
    while current.state != start_node.state:
        person_id = current.state
        movie_id = current.action

        ret.append((movie_id, person_id))

        # Follow the path that we used to get to the current state
        current = nodes_db[current.parent]

    # Since we backtracked starting from target state,
    # we now have to reverse it to make sure we present the
    # path starting from the initial state
    ret.reverse()

    return ret


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
