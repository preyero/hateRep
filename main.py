import os

import scripts.dataCollect as dc
from scripts.dataCollect import load_hateRep

PROJ_DIR = os.getcwd()
U_PATH = os.path.join(PROJ_DIR, 'annotators')
D_PATH = os.path.join(PROJ_DIR, 'data')


################################################
# Import data
################################################

data, samples, annot, users = load_hateRep(u_path=U_PATH, d_path=D_PATH)

print('Imported data with samples, annotations, and user tables')


# TODO: two phases with user info and context

################################################
# Agreement
################################################




################################################
# Confidence
################################################



################################################
# Coverage
################################################





################################################
# Quality
################################################
