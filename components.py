import pandas as pd
import requests
import sys
import argparse
import time


def get_all_components(token):
    # Get all the components and return a dataframe of them
    req_url = 'https://api.productboard.com/components'
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{token}"
    }
    all_components_df = pd.DataFrame()  # set an initial empty dataframe to append each component data pull to

    # Initial retrieval of components
    response = requests.request("GET", req_url, headers=headers)
    if response.status_code == 200:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
        print(timestamp + f": Components list success {response}")
        response = response.json()
        components_dict = response['data']
        next_url = response['links']['next']
        components_df = pd.DataFrame.from_dict(components_dict)
        all_components_df = pd.concat([all_components_df, components_df], ignore_index=True)

        # Use the next_url to paginate through customers until next_url is empty (meaning we've fetch all components)
        while next_url is not None:
            req_url = next_url
            response = requests.request("GET", req_url, headers=headers)
            if response.status_code == 200:
                timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
                print(timestamp + f": Components list success {response}")
                response = response.json()
                components_dict = response['data']
                next_url = response['links']['next']
                components_df = pd.DataFrame.from_dict(components_dict)
                all_components_df = pd.concat([all_components_df, components_df], ignore_index=True)
            else:
                print(response)
    else:
        print(response)

    all_components_df = all_components_df.rename(columns={"id": "component_id", "name":"component_name", "parent":"component_parent"})
    return all_components_df


def main():
    parser = argparse.ArgumentParser(prog="components.py", description="Query ProductBoard for a list of all components")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-t", "--token", required=True,help="JWT bearer token used for authentication")
    args = parser.parse_args()

    # Set a dataframe name and fetch the features, passing the authorization token
    all_components_df = get_all_components(args.token)

    # Cool. Export the dataframe to a CSV. Everyone wants a CSV
    print("Done fetching components")
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp for our filename
    all_components_df.to_csv('components-' + timestamp + '.csv')
    print('Saved to \'components-' + timestamp + '.csv\'')


if __name__ == "__main__":
    sys.exit(main())
