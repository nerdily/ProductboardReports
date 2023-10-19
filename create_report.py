import numpy as np
import pandas as pd

import companies
import features
import notes
import components
import products
import pandas
import argparse
import time
import sys


def main():
    parser = argparse.ArgumentParser(prog="create_report.py", description="Query ProductBoard and create a feature request report")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-t", "--token", required=True,help="JWT bearer token used for authentication")
    args = parser.parse_args()

    # Set a dataframe name and fetch the companies, passing the authorization token
    all_companies_df = companies.get_all_companies(args.token)
    all_companies_df = all_companies_df[['company_id', 'company_name']]  # Keep only the columns we need


    # Set a dataframe name and fetch all features
    all_features_df = features.get_all_features(args.token)
    all_features_df = all_features_df[['feature_id', 'feature_name', 'feature_type', 'feature_status', 'feature_parent']]  # retain only the columns we need
    all_features_df['feature_status'] = all_features_df['feature_status'].str['name']  # re-populate the feature_status column values with just the status name
    # Add columns to the dataframe we'll need:
    all_features_df['feature_parent_type'] = ''
    all_features_df['feature_parent_id'] = ''
    # all_features_df['feature_parent_name'] = ''

    for i, row in all_features_df.iterrows():
        if "feature" in all_features_df.loc[i, 'feature_parent']:
            all_features_df.loc[i, 'feature_parent_type'] = 'feature'
            all_features_df.loc[i, 'feature_parent_id'] = all_features_df.loc[i, 'feature_parent'].get("feature").get("id")
        elif "component" in all_features_df.loc[i, 'feature_parent']:
            all_features_df.loc[i, 'feature_parent_type'] = 'component'
            all_features_df.loc[i, 'feature_parent_id'] = all_features_df.loc[i, 'feature_parent'].get("component").get("id")

    #  split all_features_df into all_features_df and all_subfeatures_df This way we can do a full merge on dataframes
    all_subfeatures_df = all_features_df.loc[all_features_df['feature_type'] == "subfeature"]
    all_subfeatures_df = all_subfeatures_df.reset_index(drop=True)


    all_features_df = all_features_df.loc[all_features_df['feature_type'] == "feature"]
    all_features_df = all_features_df.reset_index(drop=True)

    # Set a dataframe name and fetch all components
    all_components_df = components.get_all_components(args.token)
    all_components_df = all_components_df[['component_id', 'component_name', 'component_parent']]

    # link subfeatures to features
    hierarchy_df = all_subfeatures_df.merge(all_features_df, how="left", left_on="feature_parent_id", right_on="feature_id")
    # rename columns and drop ones we no longer need
    hierarchy_df = hierarchy_df.rename(columns={"feature_id_x": "subfeature_id", "feature_name_x": "subfeature_name", "feature_status_x":"subfeature_status", "feature_name_y":"feature_name", "feature_status_y": "feature_status", "feature_parent_id_y": "feature_parent_id"})
    hierarchy_df = hierarchy_df.drop(columns={"feature_type_x", "feature_parent_x", "feature_parent_type_x", "feature_parent_id_x", "feature_id_y", "feature_type_y", "feature_parent_y", "feature_parent_type_y"})
    # Columns to remove: feature_type_x, feature_parent_x, _feature_parent_type_x, feature_parent_id_x, feature_id_y, feature_type_y, feature_parent_y, feature_parent_type_y

    # link features to products
    hierarchy_df = hierarchy_df.merge(all_components_df, how="left", left_on= "feature_parent_id", right_on="component_id")
    # drop columns we don't need
    hierarchy_df = hierarchy_df.drop(columns={"feature_parent_id", "component_id"})


    # dump to csv
    hierarchy_df.to_csv('feature_hierarchy.csv')

    # Set a dataframe name and fetch all the notes for a single company
    company_id = '0a45ec55-ce76-4fbc-a576-c83626f42e1b'
    company_notes_df = notes.get_company_notes(args.token, company_id)
    company_notes_df = company_notes_df[['note_id', 'note_title', 'note_content', 'note_company', 'note_linked_features']]
    #  To do: need to flatten company notes as the 'note_linked_features' can have multiple entries.
    print("Done")



if __name__ == "__main__":
    sys.exit(main())
