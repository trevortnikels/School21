import json


def main():
    try:
        with open("src/exercise6/input.txt",  encoding="utf-8") as f:
            content = f.read()

            if not content.strip():
                print("Empty file")
                return

            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format")
                return

            if "list1" not in data or "list2" not in data:
                print("Error: JSON must contain 'list1' and 'list2' keys")
                return

            list1 = data["list1"]
            list2 = data["list2"]

            if not isinstance(list1, list) or not isinstance(list2, list):
                print("Error: 'list1' and 'list2' must be lists")
                return

            for movie_list, list_name in [(list1, "list1"), (list2, "list2")]:
                for movie in movie_list:
                    if not isinstance(movie, dict):
                        print(f"Error: All items in '{list_name}' must be objects")
                        return

                    if "title" not in movie or "year" not in movie:
                        print(
                            f"Error: All items in '{list_name}' must have 'title' and 'year' properties"
                        )
                        return

                    if not isinstance(movie["title"], str):
                        print(
                            f"Error: 'title' property in '{list_name}' must be a string"
                        )
                        return

                    if not isinstance(movie["year"], int):
                        print(
                            f"Error: 'year' property in '{list_name}' must be an integer"
                        )
                        return

            merged_list = list1 + list2
            merged_list.sort(key=lambda x: x["year"])

            output = {"list0": merged_list}

            print(json.dumps(output, indent=4))

    except FileNotFoundError:
        print("Error: File input.txt not found")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
