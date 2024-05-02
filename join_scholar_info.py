################################################################
#
# Usage: python join_scholar_info.py Collaborators_2020-onward_25apr2024.txt Collaborator_institutions.txt
#
#   First argument is lastname, firstname one per line
#   Second argument is output from fetch_scholar_info.py
##
# Written with ChatGPT 4, May 2, 2024
# Couldn't get ChatGPT to get it right with a long description, so I broke it into
# pieces and edited/revised/debugged appropriately.
#
# NOTE: the weird "firstname, lastname" format assumed in the 2nd file is there because I misspecified the format
# for ChatGPT when writing fetch_scholar_info.py. Just rolling with it here rather than bothering to fix it there.
#
################################################################
import sys
import re
import pandas as pd

def process_scholar_info(filename):
    # Regular expression to match the name and extract the components
    name_regex = re.compile(r'^(\S+),\s(\S+)')
    # Regular expression to find the organization after any separator (,;@&)
    org_regex = re.compile(r'[,;@&](.*)$')

    # Initialize an empty list to hold the data tuples
    data = []

    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                try:
                    if '\t' in line:
                        name, work_info = line.split("\t")
                    else:
                        # Skip lines that don't have tab-separated columns
                        continue
                    
                    # Extract the name parts using the regex
                    name_match = name_regex.search(name)
                    if not name_match:
                        raise ValueError("Name format error")

                    firstname, lastname = name_match.groups()
                    new_name = f"{lastname}, {firstname[0]}"

                    # Find the organization using the regex
                    org_match = org_regex.search(work_info)
                    if org_match:
                        organization = org_match.group(1).strip()
                    else:
                        # If no separator, the organization is the full work_info
                        organization = work_info

                    # Append the new_name and organization as a tuple to the data list
                    data.append((new_name, organization))

                except Exception as e:
                    # Optionally handle or log errors, could append an error row or skip
                    sys.stderr.write(f"Error: {str(e)} in line: {line}\n")

    except FileNotFoundError:
        sys.stderr.write(f"Error: File '{filename}' not found.\n")
        return pd.DataFrame()  # Return an empty DataFrame in case of file not found

    # Create a DataFrame from the list of tuples
    df = pd.DataFrame(data, columns=['key', 'organization'])
    return df


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: python script.py <namefile> <scholarfile> > stdout\n")
        sys.exit(1)

    # Read in the file with collaborator names as lastname, firstname
    # Create the key by extracting lastname and first initial
    df_people = pd.read_csv(sys.argv[1], sep=', ', header=None, names=['lname','fname'], engine='python')
    df_people['first_init'] = df_people['fname'].apply(lambda x: f"{x[0]}")
    df_people['key']        = df_people['lname'] + ', ' + df_people['first_init']
    df_people['name']       = df_people['lname'] + ', ' + df_people['fname']

    # Read in the file with name as 'fname, lname' <tab> work_info
    # Create dataframe with the same format key (lastname, first_initial) and work_info
    filename = sys.argv[2]
    df_scholar = process_scholar_info(filename)

    # Create the desired data, which is the original name and the organization
    merged_df = pd.merge(df_people, df_scholar, on='key', how='inner')
    result_df = merged_df[['name', 'organization']]

    # Output the result to stdout in CSV format without the index
    result_df.to_csv(sys.stdout, index=False)

    
