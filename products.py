import pandas as pd
import requests
import sys
import argparse
import time
import json


def get_all_products(token):
    # Get all the products and return a dataframe of them
    req_url = 'https://api.productboard.com/products'
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{token}"
    }
    all_products_df = pd.DataFrame()  # set an initial empty dataframe to append each component data pull to

    # Initial retrieval of products
    response = requests.request("GET", req_url, headers=headers)
    if response.status_code == 200:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
        print(timestamp + f": products list success {response}")
        response = response.json()
        products_dict = response['data']
        next_url = response['links']['next']
        products_df = pd.DataFrame.from_dict(products_dict)
        all_products_df = pd.concat([all_products_df, products_df], ignore_index=True)

        # Use the next_url to paginate through customers until next_url is empty (meaning we've fetch all products)
        while next_url is not None:
            req_url = next_url
            response = requests.request("GET", req_url, headers=headers)
            if response.status_code == 200:
                timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
                print(timestamp + f": products list success {response}")
                response = response.json()
                products_dict = response['data']
                next_url = response['links']['next']
                products_df = pd.DataFrame.from_dict(products_dict)
                all_products_df = pd.concat([all_products_df, products_df], ignore_index=True)
            else:
                print(response)
    else:
        print(response)

    all_products_df = all_products_df.rename(columns={"id": "product_id", "name":"product_name"})
    return all_products_df


def main():
    parser = argparse.ArgumentParser(prog="products.py", description="Query ProductBoard for a list of all products")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-t", "--token", required=True,help="JWT bearer token used for authentication")
    args = parser.parse_args()

    # Set a dataframe name and fetch the features, passing the authorization token
    all_products_df = get_all_products(args.token)

    # Cool. Export the dataframe to a CSV. Everyone wants a CSV
    print("Done fetching products")
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp for our filename
    all_products_df.to_csv('products-' + timestamp + '.csv')
    print('Saved to \'products-' + timestamp + '.csv\'')


if __name__ == "__main__":
    sys.exit(main())
