import pandas as pd
import companies
import features
import notes
import components
import argparse
import time
import sys


def main():
    # Logging:
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sys.stdout = open('reports/log-'+timestamp+'.txt', 'wt')  # Redirect all console (print etc) to a file for logging. Comment this out if you want console data instead.

    parser = argparse.ArgumentParser(prog="create_report.py", description="Query ProductBoard and create a feature request report")
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument("-t", "--token", required=True,help="JWT bearer token used for authentication")
    args = parser.parse_args()

    # Set a dataframe of our feature status meanings
    # initialize list of lists
    statuses = [['New Idea', "Our product team has added the idea to our backlog. Additional information as to why this is important to your organization will further help prioritize the request"],
                ['Problem Discovery', "Our Product team is exploring this idea. If you have any feedback about it - how it would help you or help solve problems you have or would you be willing to talk to the product team - we're happy to pass that feedback along to the product team"],
                ['Ready for Init Ops Team', "Our Product team is exploring this idea. Do you have any feedback about it - how it would help you or help solve problems you have or would you be willing to talk to the product team? We’d be happy to pass that feedback along to the product team"],
                ['Analysis', "Our teams are hard at work investigating and designing. However, it’s still early and there’s a lot things that could change. Delivery timeframe uncertain at this time."],
                ['Prioritized', "Our teams are hard at work investigating and designing. However, it’s still early and there’s a lot things that could change. Delivery timeframe uncertain at this time."],
                ['In Progress', "We are actively developing this feature right now."],
                ['Code Complete', "Coding work is complete and we are scheduling a ship date"],
                ['Shipped', "Feature has been released"],
                ['Blocked,' "A pre-requisite must be completed first before we could work on this request."]]

    # Create the pandas DataFrame
    status_df = pd.DataFrame(statuses, columns=['Status', 'Meaning'])

    # Set a dataframe name and fetch the companies, passing the authorization token
    all_companies_df = companies.get_all_companies(args.token)
    all_companies_df = all_companies_df[['company_id', 'company_name']]  # Keep only the columns we need


    # Set a dataframe name and fetch all features
    all_features_df = features.get_all_features(args.token)
    all_features_df = all_features_df[['feature_id', 'feature_name', 'feature_type', 'feature_status', 'feature_parent']]  # retain only the columns we need

    # Add columns to the dataframe we'll need:
    all_features_df['feature_parent_type'] = ''
    all_features_df['feature_parent_id'] = ''

    all_features_df['feature_status'] = all_features_df["feature_status"].apply(lambda x: x.get("name", "default-value"))

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


    # Link subfeatures to features to products:
    # link subfeatures to features
    subfeature_hierarchy_df = all_subfeatures_df.merge(all_features_df, how="left", left_on="feature_parent_id", right_on="feature_id")
    # rename columns and drop ones we no longer need
    subfeature_hierarchy_df = subfeature_hierarchy_df.rename(columns={"feature_id_x": "subfeature_id", "feature_name_x": "subfeature_name", "feature_status_x":"subfeature_status", "feature_id_y":"feature_id", "feature_name_y":"feature_name", "feature_status_y": "feature_status", "feature_parent_id_y": "feature_parent_id"})
    subfeature_hierarchy_df = subfeature_hierarchy_df.drop(columns={"feature_type_x", "feature_parent_x", "feature_parent_type_x", "feature_parent_id_x", "feature_type_y", "feature_parent_y", "feature_parent_type_y"})
    # link features to components
    subfeature_hierarchy_df = subfeature_hierarchy_df.merge(all_components_df, how="left", left_on="feature_parent_id", right_on="component_id")
    # drop columns we don't need
    subfeature_hierarchy_df = subfeature_hierarchy_df.drop(columns={"feature_id", "component_id", "feature_parent_id", "component_parent"})

    # Link features to components
    feature_hierarchy_df = all_features_df.merge(all_components_df, how="left", left_on="feature_parent_id", right_on="component_id")
    # drop columns we don't need
    feature_hierarchy_df = feature_hierarchy_df.drop(columns={"feature_parent", "feature_parent_id", "component_id", "component_parent"})



    # Okay let's churn through each company and match up their feature requests!
    for i, row in all_companies_df.iterrows():

        # Set a dataframe name and fetch all the notes for a single company
        company_id = all_companies_df.loc[i, 'company_id']
        company_name = all_companies_df.loc[i, 'company_name']

        company_name = str(company_name).replace("/", "-")  # replace any forward slashes in company names with a dash - file paths use them
        company_name = str(company_name).replace("?", "")   # remove any question mark characters - OneDrive can't use them
        print("Working on " + company_name)
        company_notes_df = notes.get_company_notes(args.token, company_id)
        company_notes_df = company_notes_df[['note_id', 'displayUrl', 'note_created_date', 'note_title', 'note_content', 'note_pm', 'note_company', 'note_linked_features']]
        company_notes_df = company_notes_df.explode('note_linked_features', ignore_index=True)  # Flatten company notes as the 'note_linked_features' can have multiple entries.
        company_notes_df['note_linked_feature_type'] = ''  # Add column for linked feature type
        company_notes_df['note_linked_feature_id'] = ''  # Add column for linked feature ID
        company_notes_df.dropna(axis=0, how='any', inplace=True)  # remove rows with no linked notes.
        company_notes_df['note_pm'] = company_notes_df['note_pm'].apply(lambda y: y.get("name", "default-value"))  # Pull the note owner's name
        company_notes_df['note_linked_feature_type'] = company_notes_df['note_linked_features'].apply(lambda y: y.get("type", "default-value"))  # Pull linked feature type out.
        company_notes_df['note_linked_feature_id'] = company_notes_df['note_linked_features'].apply(lambda y: y.get("id", "default-value"))  # Pull linked feature ID out.
        company_notes_df.drop(columns={"note_company", "note_linked_features"}, inplace=True)  # Drop columns we don't need

        # Notes linked to subfeatures: (done - data looks good)
        # Split off company notes that are linked to subfeatures, features, and components into their own dataframes and merge with subfeature/feature/component info
        company_notes_subfeatures_df = company_notes_df.loc[company_notes_df['note_linked_feature_type'] == "subfeature"]
        company_notes_subfeatures_df = company_notes_subfeatures_df.reset_index(drop=True)
        company_notes_subfeatures_df = company_notes_subfeatures_df.merge(subfeature_hierarchy_df, how="left", left_on="note_linked_feature_id", right_on="subfeature_id")
        company_notes_subfeatures_df = company_notes_subfeatures_df.drop(columns={"note_linked_feature_id", "subfeature_id"})

        # Notes linked to features:
        company_notes_features_df = company_notes_df.loc[company_notes_df['note_linked_feature_type'] == "feature"]
        company_notes_features_df = company_notes_features_df.reset_index(drop=True)
        company_notes_features_df = company_notes_features_df.merge(feature_hierarchy_df, how="left", left_on="note_linked_feature_id", right_on="feature_id")
        company_notes_features_df = company_notes_features_df.drop(columns={"note_linked_feature_id", "feature_id", "feature_type", "feature_parent_type"})
        company_notes_features_df.insert(loc=6, column='subfeature_status', value='n/a')
        company_notes_features_df.insert(loc=6, column='subfeature_name', value='n/a')

        # Notes linked directly to components:
        company_notes_components_df = company_notes_df.loc[company_notes_df['note_linked_feature_type'] == "component"]
        company_notes_components_df = company_notes_components_df.reset_index(drop=True)
        company_notes_components_df = company_notes_components_df.merge(all_components_df, how="left", left_on="note_linked_feature_id", right_on="component_id")
        company_notes_components_df = company_notes_components_df.drop(columns={"note_linked_feature_id", "component_id"})
        company_notes_components_df = company_notes_components_df.rename(columns={"component_parent": "component_parent_type"})
        try:
            for i, row in company_notes_components_df.iterrows():
                if "component" in company_notes_components_df.loc[i, 'component_parent_type']:
                    company_notes_components_df.loc[i, 'component_parent_type'] = 'component'
                elif "product" in company_notes_components_df.loc[i, 'component_parent_type']:
                    company_notes_components_df.loc[i, 'component_parent_type'] = 'product'
        except:
            company_notes_components_df.loc[i, 'component_parent_type'] = 'none'
        # Join our features and subfeatures dataframes
        all_company_features_df = pd.concat([company_notes_features_df, company_notes_subfeatures_df], axis=0)
        all_company_features_df = all_company_features_df.drop(columns=["note_id"])
        # Reset the index
        all_company_features_df = all_company_features_df.reset_index(drop=True)
        # Rename our displayUrl column
        all_company_features_df = all_company_features_df.rename(columns={"displayUrl": "noteURL"})


        # Export it!
        if all_company_features_df.shape[0] != 0:
            timestamp = time.strftime("%Y%m%d-%H%M%S")  # create a timestamp for our filename
            xlwriter = pd.ExcelWriter('reports/' + company_name + '-' + timestamp + '.xlsx', engine="xlsxwriter")
            all_company_features_df.to_excel(xlwriter, sheet_name="Feature Requests", index=False)
            status_df.to_excel(xlwriter, sheet_name="Status Explanations", index=False)
            xlwriter.close()
        else:
            print(company_name + " has no feature requests")
    print("Done")


if __name__ == "__main__":
    sys.exit(main())
