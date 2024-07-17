[![Python](https://upload.wikimedia.org/wikipedia/commons/5/50/Blue_Python_3.12%2B_Shield_Badge.svg)](https://www.python.org/downloads/release/python-3120/)
[![DOI](https://zenodo.org/badge/730161779.svg)](https://zenodo.org/doi/10.5281/zenodo.12687196)


Data Repository: [![ORDO - 10.21954/ou.rd.26212604.v1](https://img.shields.io/badge/ORDO-10.21954/ou.rd.26212604.v1-2ea44f)](https://doi.org/10.21954/ou.rd.26212604.v1)

Paper Preprint: [![ORO-198676](https://img.shields.io/badge/ORO-oro.open.ac.uk/98676/-2ea49f)](https://oro.open.ac.uk/98676/)

# Semantic-Enhanced Crowdsourcing Study for Target Group Identification - Code


This is the source code to reproduce the paper: **Enhancing Hate Speech Annotations with Background Semantics (ECAI 2024): https://oro.open.ac.uk/98676/**

The Data repository is available in Open Research Data Online ([ORDO](https://doi.org/10.21954/ou.rd.26212604.v1)). 


## Repo structure

The raw data is organised in the following folders: 

* *Annotators*: anonymised demographic tables from [Prolific](https://www.prolific.com/). Each participant appears in one file only, subject to being (i) heterosexual cis men (M_MH), (ii) heterosexual cis women (W_WH), or LGBTQ+ member because of their (iii) gender (trans, G_T, or non-binary, G_NB) or (iv) sexuality (non-heterosexual, S_H). 


* *Data*: contains semantic and crowdsourcing annotations. Crowdsourcing annotations were collected as shown in the example [figure](#hate-speech-annotations) and full [documentation](documentation/Survey_Questionnaire.pdf). 

* *Semantic_annotation*: Jupyter notebooks to provide background knowledge to the hate speech sample using a knowledge graph, i.e., the [GSSO](https://github.com/Superraptor/GSSO) (`pruned_concepts.csv`) and other linguistic resources (`missing_concepts.csv`).

* *Documentation*: contains the approved Ethics Application Form and Participant Information Sheet.

Source code is in *scripts*, specifically in the Python files:

* *dataCollect.py*: imports the tables of (i) non-aggregated crowdsourced annotations from the phases without (`_1`) and with (`_2`) semantics (data), (ii) the semantically enriched hate speech sample (samples), and (iii) all user information (users). 

* *agreement.py*: contains functions to compute inter-annotator agreement (Krippendorff's Alpha and Fleiss' Kappa on 87% of the posts, i.e., with 6 annotations).

* *helper.py*: helper functions to analyse alignment (Pearson's correlation) and change after semantics (categorisation by agreement and decision made on target groups).

* *utils.py*: functions for table plot (agreement and correlation, Figure 2), horizontal bar and Sankey diagram (frequency and shifts, Figure 3) and, heatmap (categories overlap, Figure 4).

All files used for evaluation in the paper are in folder *results*.

## Run files

The code runs in Python version 3.12 using packages in `requirements.txt`:

```commandline
    hateRep <user-login>$ python main.py
```

## Phase 2 Annotation Example (with semantics)

There is a [PDF](documentation/Survey_Questionnaire.pdf) showing the full annotation study with examples provided by participants. 

Texts in Phase 2 were annotated as shown below:

<p align="center">
 <img src="data/survey_items.png" alt="drawing" width="400" class="center"/>
</p>

In Phase 1, the same layout is presented but without underlined terms in the post and with an empty column on the left.


