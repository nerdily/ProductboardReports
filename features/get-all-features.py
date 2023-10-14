import pandas as pd
import requests
import sys
import argparse
import time


def main():
    parser = argparse.ArgumentParser(prog="get-all-features.py", description="Query ProductBoard for a list of all features")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-t", "--token", required=True,help="JWT bearer token used for authentication")
    args = parser.parse_args()

    req_url = 'https://api.productboard.com/features'
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{args.token}"
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

        # Cool. Export the dataframe to a CSV. Everyone wants a CSV
        print("Done fetching features")
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp for our filename
        all_features_df.to_csv('features-' + timestamp + '.csv')
        print('Saved to \'features-' + timestamp + '.csv\'')

    else:
        print(response)


if __name__ == "__main__":
    sys.exit(main())
