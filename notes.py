import pandas as pd
import requests
import sys
import argparse
import time


def get_company_notes(token, company_id):
    # Get all the notes associated with a company and return a dataframe of them
    req_url = 'https://api.productboard.com/notes?pageLimit=2000&companyId=' + company_id
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{token}"
    }
    all_company_notes_df = pd.DataFrame()  # set an initial empty dataframe to append each customer data pull to

    # Initial retrieval of notes
    response = requests.request("GET", req_url, headers=headers)
    if response.status_code == 200:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
        print(timestamp + f": Company notes list success {response}")
        response = response.json()
        company_notes_dict = response['data']
        if response['pageCursor'].__str__() is not None:
            cursor = response['pageCursor']  # This API uses a 'cursor' to paginate through results. Grab it, and add it to the next_url
            next_url = f"{req_url}" + "&pageCursor=" + str(cursor)
        company_notes_df = pd.DataFrame.from_dict(company_notes_dict)
        all_company_notes_df = pd.concat([all_company_notes_df, company_notes_df], ignore_index=True)

        while response['pageCursor'] is not None:
            response = requests.request("GET", next_url, headers=headers)
            if response.status_code == 200:
                timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
                print(timestamp + f": Company notes list success {response}")
                response = response.json()
                company_notes_dict = response['data']
                cursor = response['pageCursor']  # This API uses a 'cursor' to paginate through results. Grab it, and add it to the next_url
                next_url = f"{req_url}" + "&pageCursor=" + cursor
                company_notes_df = pd.DataFrame.from_dict(company_notes_dict)
                all_company_notes_df = pd.concat([all_company_notes_df, company_notes_df], ignore_index=True)
            else:
                print(response)
    else:
        print(response)

    all_company_notes_df = all_company_notes_df.rename(columns={"id": "note_id", "title": "note_title", "content":"note_content", "company":"note_company", "features":"note_linked_features"})
    return all_company_notes_df


def get_all_notes(token):
    # Get all the notes and return a dataframe of them
    req_url = 'https://api.productboard.com/notes?pageLimit=2000'
    headers = {
        "X-Version": "1",
        "Authorization": "Bearer " f"{token}"
    }
    all_notes_df = pd.DataFrame()  # set an initial empty dataframe to append each customer data pull to

    # Initial retrieval of notes
    response = requests.request("GET", req_url, headers=headers)
    if response.status_code == 200:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
        print(timestamp + f": Notes list success {response}")
        response = response.json()
        notes_dict = response['data']
        cursor = response['pageCursor']  # This API uses a 'cursor' to paginate through results. Grab it, and add it to the next_url
        next_url = f"{req_url}" + "&pageCursor=" + cursor
        notes_df = pd.DataFrame.from_dict(notes_dict)
        all_notes_df = pd.concat([all_notes_df, notes_df], ignore_index=True)

        while response['data'].__str__() != '[]':
            response = requests.request("GET", next_url, headers=headers)
            if response.status_code == 200:
                timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
                print(timestamp + f": Notes list success {response}")
                response = response.json()
                notes_dict = response['data']
                cursor = response['pageCursor']
                next_url = f"{req_url}" + "&pageCursor=" + cursor
                notes_df = pd.DataFrame.from_dict(notes_dict)
                all_notes_df = pd.concat([all_notes_df, notes_df], ignore_index=True)
            else:
                print(response)
    else:
        print(response)

    all_notes_df = all_notes_df.rename(columns={"id": "note_id", "title": "note_title", "content":"note_content"})
    return all_notes_df


def main():
    parser = argparse.ArgumentParser(prog="notes.py", description="Query ProductBoard for a list of all notes")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-t", "--token", required=True,help="JWT bearer token used for authentication")
    args = parser.parse_args()

    # Set a dataframe name and fetch the notes, passing the authorization token
    all_notes_df = get_all_notes(args.token)

    # Cool. Export the dataframe to a CSV. Everyone wants a CSV
    print("Done fetching notes")
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp
    all_notes_df.to_csv('notes-' + timestamp + '.csv')
    print('Saved to \'notes-' + timestamp + '.csv')


if __name__ == "__main__":
    sys.exit(main())
