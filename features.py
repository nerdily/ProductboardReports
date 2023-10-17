import pandas as pd
import requests
import sys
import argparse
import time


def get_feature(token, feature_id):
    # Get a single feature and return a dataframe of it
    req_url = 'https://api.productboard.com/features/' + feature_id
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{token}"
    }

    feature_df = pd.DataFrame()  # set an initial empty dataframe
    response = requests.request("GET", req_url, headers=headers)
    if response.status_code == 200:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
        print(timestamp + f": Feature list success {response}")
        response = response.json()
        feature_dict = response['data']
        feature_df = pd.DataFrame(feature_dict, index=[0])
    else:
        print(response)

    return feature_df


def get_all_features(token):
    # Get all the features and return a dataframe of them
    req_url = 'https://api.productboard.com/features'
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{token}"
    }
    all_features_df = pd.DataFrame()  # set an initial empty dataframe to append each customer data pull to

    # Initial retrieval of customers
    response = requests.request("GET", req_url, headers=headers)
    if response.status_code == 200:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
        print(timestamp + f": Features list success {response}")
        response = response.json()
        features_dict = response['data']
        next_url = response['links']['next']
        features_df = pd.DataFrame.from_dict(features_dict)
        all_features_df = pd.concat([all_features_df, features_df], ignore_index=True)

        # Use the next_url to paginate through customers until next_url is empty (meaning we've fetch all customers)
        while next_url is not None:
            req_url = next_url
            response = requests.request("GET", req_url, headers=headers)
            if response.status_code == 200:
                timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
                print(timestamp + f": Features list success {response}")
                response = response.json()
                features_dict = response['data']
                next_url = response['links']['next']
                features_df = pd.DataFrame.from_dict(features_dict)
                all_features_df = pd.concat([all_features_df, features_df], ignore_index=True)
            else:
                print(response)
    else:
        print(response)

    return all_features_df


def main():
    parser = argparse.ArgumentParser(prog="features.py", description="Query ProductBoard for a list of all features")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-t", "--token", required=True,help="JWT bearer token used for authentication")
    args = parser.parse_args()

    # Set a dataframe name and fetch the features, passing the authorization token
    all_features_df = get_all_features(args.token)

    # Cool. Export the dataframe to a CSV. Everyone wants a CSV
    print("Done fetching features")
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp for our filename
    all_features_df.to_csv('features-' + timestamp + '.csv')
    print('Saved to \'features-' + timestamp + '.csv\'')


if __name__ == "__main__":
    sys.exit(main())
