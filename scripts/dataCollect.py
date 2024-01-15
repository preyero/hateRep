import glob, ast
import pandas as pd


def import_users(u_path: str):
    """ Import annotator tables (hateRep/annotators)"""

    # Import prolific tables using info from phase 1 
    f_users, users = glob.glob(f'{u_path}/*p1_prolific*'), []
    for f in f_users:
        u = pd.read_csv(f, keep_default_na=False)
        # include only approved submissions (e.g. others are 'ACTIVE', 'REJECTED', 'RETURNED', 'TIMED-OUT')
        u = u.loc[u.Status.isin(['APPROVED'])] 
        # add group and subgroup tags
        fname = f.split('/')[-1]
        for i, tag in enumerate(['group', 'subgroupA', 'subgroupB']):
            u[tag] = fname.split('_')[i] 
        users.append(u)
    users = pd.concat(users, ignore_index=True)
    users.rename(columns={'Participant id': 'User'}, inplace=True) 
    
    return users


def import_data(d_path: str):
    """ Import data samples, data annotations (hateRep/data), and user questions table """

    # Annotations
    annot = [pd.read_csv(f, keep_default_na=False) for f in glob.glob(f'{d_path}/annotations*')]
    annot = pd.concat(annot, ignore_index=True)

    # Data samples
    samples = pd.read_csv(f'{d_path}/database.csv')
    samples['box_entity'] = samples['box_entity'].apply(lambda x: ast.literal_eval(x))
    samples['context'] = samples['box_entity'].apply(lambda x: ', '.join(x))

    # User additional info
    questions = pd.read_csv(d_path + '/users.csv', keep_default_na=False)


    return samples, annot, questions


def load_hateRep(u_path: str, d_path: str):

    # Import Prolific data
    users = import_users(u_path)

    # Import survey data
    samples, annot, user_qs = import_data(d_path)

    
    # fix users that added prolific ID incorreclty
    to_replace = [id for id in users['User'] if id not in annot.User.to_list()]
    if len(to_replace) > 1:
        raise Exception(f'Update list that need fixing a typo: {to_replace}')
    to_replace = {'605212ecea6f5a8c7909f293@email.prolific.com': '605212ecea6f5a8c7909f293'}
    annot['User'].replace(to_replace=to_replace, inplace=True)
    user_qs['User'].replace(to_replace=to_replace, inplace=True)

    # keep unique user table with relevant info
    users = pd.merge(users, user_qs, on='User', how='inner')

    # add group tags labels
    annot = pd.merge(annot, users[['User', 'group', 'subgroupA', 'subgroupB']], on='User', how='inner')

    # TODO: one-hot encoding of annoations (distinguising '' values)
    for g in ['gender', 'sexuality']:
        annot[f'About {g}'].replace(to_replace={'': f'no_{g}'})
        ...
    return samples, annot, users

    


    