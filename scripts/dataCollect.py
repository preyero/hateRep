import glob, ast
from datetime import datetime
from typing import List
import pandas as pd

# Dataset features
CATEG = {'c1': 'group', 'c2': 'subgroupA', 'c3': 'subgroupB'}
FACT = {
    'f0': 'Lgbtq+',
    # sexuality
    'f1': 'Sexual orientation', 
    # sex and gender
    'f2': 'Cisgender and transgender', 'f3': 'Gender', 'f4': 'Sex'
    }
COFACT = {
    # annotator performance
    'f0': 'Time taken', 'f0.1_1': 'Complete_1_M', 'f0.1_2': 'Complete_2_M', 
    'f1':'Total approvals', 
    # annotator's background
    'f2':'Age', 
    'f3': 'Language', 
    'f4.1':'Country of birth', 'f4.2':'Country of residence', 'f4.3':'Ethnicity simplified', 'f4.4':'Nationality', 
    'f5.1':'Employment status', 'f5.2': 'Student status',
    # annotator's experience
    'f6': 'Personal Experience', 'f6.1': 'personally', 'f6.2': 'witnessed', 'f6.3': 'unsure', 'f6.4': 'none',
    # annotator and reasoning
    'f7': 'User', 'f7.1': 'Justify Gender', 'f7.2': 'Justify Sexuality',
    'f8': 'justify_change', 'f8.1': 'justify_change_gender', 'f8.2': 'justify_change_sexuality',
    # semantics
    'f9': 'context',
    'f8': 'context_accept', 'f8.1': 'context_accept_gender', 'f8.2': 'context_accept_sexuality',
    # data provenance
    'f9': 'dataset', 
    'f10': 'Question ID',
    }

# Experiment setup
PHASES = ['1', '2']

HATE_QS = ['Hate speech?', 'Is the hate speech targeting?']
HATE_LABELS = {1: 'hateful', 2:'not-hateful', 3:'unclear'}

TARGET_GROUPS = ['gender', 'sexuality']
# individual binary encodings
TARGET_LABELS = {}

def import_users(u_path: str):
    """ Import annotator tables from (hateRep/annotators) folder """

    # Import prolific tables using info from phase 1 
    f_users, users = glob.glob(f'{u_path}/*p1_prolific*'), []
    for f in f_users:
        u = pd.read_csv(f, keep_default_na=False)
        # include only approved submissions (e.g. others are 'ACTIVE', 'REJECTED', 'RETURNED', 'TIMED-OUT')
        u = u.loc[u.Status.isin(['APPROVED'])] 
        # add group and subgroup categories
        fname = f.split('/')[-1]
        for i, tag in enumerate(CATEG.values()):
            u[tag] = fname.split('_')[i] 
        users.append(u)
    users = pd.concat(users, ignore_index=True)
    users.rename(columns={'Participant id': 'User'}, inplace=True) 
    
    return users


def import_survey(d_path: str):
    """ Import data samples, data annotations, and user questions table from (hateRep/data) folder """

    # Annotations
    annot = [pd.read_csv(f, keep_default_na=False) for f in glob.glob(f'{d_path}/annotations*')]
    annot = pd.concat(annot, ignore_index=True)
    annot[HATE_QS] = annot[HATE_QS].replace(to_replace=HATE_LABELS)

    # Data samples
    samples = pd.read_csv(f'{d_path}/database.csv')
    samples['box_entity'] = samples['box_entity'].apply(lambda x: ast.literal_eval(x))
    samples['context'] = samples['box_entity'].apply(lambda x: ', '.join(x))

    # User additional info
    questions = pd.read_csv(d_path + '/users.csv', keep_default_na=False)
    questions.rename(columns={'Consent Time': 'Phase 1 Started'}, inplace=True)
    # time to complete each phase
    for p in PHASES:
        for t in ['Started', 'Finished']:
           questions[f'Phase {p} {t}'] = questions[f'Phase {p} {t}'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")) 
        questions[f'Complete_{p}'] = questions[f'Phase {p} Finished'] - questions[f'Phase {p} Started'] 
        questions[f'Complete_{p}_M'] = questions[f'Complete_{p}'].apply(lambda x: round(x.total_seconds()/60), 2) 


    return samples, annot, questions


def scale_encoding(value: str, scale: List[str]) -> float:
    """ Encode as number a string on a scale of 3 """
    if value == scale[0]:
        return 0
    elif value == scale[1]:
        return 0.5
    elif value == scale[2]:
        return 1
    
def one_hot_encoding(df: pd.DataFrame, col: str):
    """ Expand a df with binary encodings of column with list of string values """

    from sklearn.preprocessing import MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    df[mlb.classes_] = mlb.fit_transform(df[col])
    return df, mlb.classes_.tolist()


def stemmatize(text: str) -> List[str]:
    """ tokenize, lower-case, and stem filter """
    from whoosh.analysis import StemmingAnalyzer
    stemmer = StemmingAnalyzer(stoplist=None) 
    return [token.text for token in stemmer(text)]


def excOuterJoin(reasons1: str, reasons2: str, verbose: bool = False) -> List[str]:
    """ Returns exclusive full outer join """
    # TOkenize
    tokens1 = stemmatize(reasons1)
    tokens2 = stemmatize(reasons2)
    # return not in intersection
    not_intersection = list(set(tokens1) ^ set(tokens2))
    if verbose:
        print(f"{tokens1}|{tokens2}->{not_intersection}")
    return not_intersection


def innerJoin(reasons1: str, reasons2: str, verbose: bool = False) -> List[str]:
    """ Returns intersection """
    # TOkenize
    tokens1 = stemmatize(reasons1)
    tokens2 = stemmatize(reasons2)
    # return in intersection
    intersection = list(set(tokens1) & set(tokens2))
    if verbose:
        print(f"{tokens1}∩{tokens2}->{intersection}")
    return intersection


def load_hateRep(u_path: str, d_path: str):

    # Prolific data
    users = import_users(u_path)

    # Survey data
    samples, annot, questions = import_survey(d_path)

    
    # ... fix users that added prolific ID incorreclty
    to_replace = [id for id in users['User'] if id not in annot.User.to_list()]
    to_replace = {'605212ecea6f5a8c7909f293@email.prolific.com': '605212ecea6f5a8c7909f293'}
    annot['User'].replace(to_replace=to_replace, inplace=True)
    questions['User'].replace(to_replace=to_replace, inplace=True)

    # ... one-hot encodings of user info
    questions['Personal Experience'] = questions['Personal Experience'].apply(lambda labels: str(labels).split(','))
    questions, _ = one_hot_encoding(questions, 'Personal Experience')
    # ... one-hot encodings of annotations
    for g in TARGET_GROUPS:
        c_no, c_yes = f'{g.capitalize()} Unclear/Not-Referring', f'About {g}?'
        # unclear/not referring
        annot[c_no].replace(to_replace={'not-referring': f'{g}_not-referring', 'unclear': f'{g}_unclear'}, inplace=True)
        annot[c_no] = annot[c_no].apply(lambda x: [] if x == '' else [x])
        # target group labels
        annot[c_yes] = annot[c_yes].apply(lambda labels: [f'{g}_other' if l == 'other' else l for l in str(labels).split(', ')]
                                          if labels != '' else [])
        # annot[f'{g}_bin'] = annot[c_yes].apply(lambda labels: 0 if not labels else 1)
        annot[g] = annot.apply(lambda x: 'referring' if x[c_yes] else x[c_no][0].split('_')[-1], axis=1)
        annot[f'{g}_bin'] = annot[g].apply(lambda label: scale_encoding(label, ['not-referring', 'unclear', 'referring']))
        # individual binary encodings
        annot[f'{g}_cat'] = annot.apply(lambda x: x[c_yes] + x[c_no], axis=1)
        annot, TARGET_LABELS[g] = one_hot_encoding(annot, f'{g}_cat')
    # rename transgender column
    annot.rename(columns={'yes': 'transgender'}, inplace=True)
    TARGET_LABELS['gender'] = ['transgender' if x == 'yes' else x for x in TARGET_LABELS['gender']]
    # other labels:
    for hate_q in HATE_QS:
        annot[f'{hate_q}_bin'] = annot[hate_q].apply(lambda label: scale_encoding(label, ['not-hateful', 'unclear', 'hateful']))


    # ... keep unique user table with relevant info
    users = pd.merge(users, questions, on='User', how='inner')

    # merge by phases 
    annot = pd.merge(annot.loc[annot.Phase==1], annot.loc[annot.Phase==2], on=['User', 'Question ID', 'Question'], how='inner', suffixes=['_1', '_2'])
    # and with semantic context
    annot = pd.merge(samples.drop(columns=['Question']), annot, on=['Question ID'], how='inner')
    for g in TARGET_GROUPS:
        # change in justifications across phase
        annot[f'justify_change_{g}'] = annot.apply(lambda x: ', '.join(excOuterJoin(x[f'Justify {g.capitalize()}_1'], x[f'Justify {g.capitalize()}_2'])), axis=1)
        # get if context explains the change
        annot[f'context_accept_{g}'] = annot.apply(lambda x: innerJoin(x[f'justify_change_{g}'], x[f'context']), axis=1)
    annot['justify_change'] = annot.apply(lambda x: 0 if x['justify_change_gender'] + x['justify_change_sexuality'] == '' else 1, axis = 1)
    annot['context_accept'] = annot.apply(lambda x: 0 if len(x['context_accept_gender']) + len(x['context_accept_sexuality']) == 0 else 1, axis = 1)
    
    # Final dataset
    data = pd.merge(annot, users, on='User', how='inner')

    return data, samples, users

    


    