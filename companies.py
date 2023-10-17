import pandas as pd
import requests
import sys
import argparse
import time


def get_company(token, company_id):
    # Get a single company and return a dataframe of it
    req_url = 'https://api.productboard.com/companies/' + company_id
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{token}"
    }

    company_df = pd.DataFrame()  # set an initial empty dataframe
    response = requests.request("GET", req_url, headers=headers)
    if response.status_code == 200:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
        print(timestamp + f": Company list success {response}")
        response = response.json()
        company_dict = response['data']
        company_df = pd.DataFrame(company_dict, index=[0])
    else:
        print(response)

    company_df = company_df.rename(columns={"id": "company_id", "name": "company_name"})
    return company_df


def get_all_companies(token):
    # Get all the customers and return a dataframe of them
    req_url = 'https://api.productboard.com/companies'
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{token}"
    }
    all_companies_df = pd.DataFrame()  # set an initial empty dataframe to append each customer data pull to

    # Initial retrieval of customers
    response = requests.request("GET", req_url, headers=headers)
    if response.status_code == 200:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
        print(timestamp + f": Companies list success {response}")
        response = response.json()
        companies_dict = response['data']
        next_url = response['links']['next']
        companies_df = pd.DataFrame.from_dict(companies_dict)
        all_companies_df = pd.concat([all_companies_df, companies_df], ignore_index=True)

        while next_url is not None:
            req_url = next_url
            response = response = requests.request("GET", req_url, headers=headers)
            if response.status_code == 200:
                timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
                print(timestamp + f": Companies list success {response}")
                response = response.json()
                companies_dict = response['data']
                next_url = response['links']['next']
                companies_df = pd.DataFrame.from_dict(companies_dict)
                all_companies_df = pd.concat([all_companies_df, companies_df], ignore_index=True)
            else:
                print(response)
    else:
        print(response)
    all_companies_df = all_companies_df.rename(columns={"id": "company_id", "name": "company_name"})
    return all_companies_df


def main():
    parser = argparse.ArgumentParser(prog="companies.py", description="Query ProductBoard for a list of all companies")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-t", "--token", required=True,help="JWT bearer token used for authentication")
    args = parser.parse_args()

    # Set a dataframe name and fetch the customers, passing the authorization token
    all_companies_df = get_all_companies(args.token)

    # Cool. Export the dataframe to a CSV. Everyone wants a CSV
    print("Done fetching companies")
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp for our filename
    all_companies_df.to_csv('companies-' + timestamp + '.csv')
    print('Saved to \'companies-' + timestamp + '.csv\'')


if __name__ == "__main__":
    sys.exit(main())
