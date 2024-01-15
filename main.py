import os

from scripts.dataCollect import load_hateRep

PROJ_DIR = os.getcwd()
U_PATH = os.path.join(PROJ_DIR, 'annotators')
D_PATH = os.path.join(PROJ_DIR, 'data')

# Import data

samples, annot, users = load_hateRep(u_path=U_PATH, d_path=D_PATH)

print('Imported data samples, annotations, and user tables')