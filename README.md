# MarchMadness 🏀
This repository hosts a model for predicting if a given March Madness matchup will result in an upset. Using this model, an entire bracket can be filled out with predictions 
(either the game results in an upset or the superior-seeded team wins). The model was trained on a dataset of 995 March Madness games (every game from *2008-2023*), which includes 
various statistics for each of the teams in the matchup. This project is not yet complete. See below for details.

# Data Collection
## Team Stats
Statistics for each team participating in March Madness from *2008-2023* were downloaded from this Kaggle Dataset 
([Team Stats](https://www.kaggle.com/datasets/nishaanamin/march-madness-data?select=Tournament+Team+Data+%28Including+2023%29.csv)). In addition to identifying each team by its 
name, seed, and the tournament year, the dataset provides the following team statistics:

- **ROUND** (*The furthest round the team made it to in that year's tournament*)
- **KENPOM ADJUSTED EFFICIENCY**
- **KENPOM ADJUSTED OFFENSE**
- **KENPOM ADJUSTED DEFENSE**
- **KENPOM ADJUSTED TEMPO**
- **KENPOM ADJUSTED EFFICIENCY**
- **BARTTORVIK ADJUSTED EFFICIENCY**
- **BARTTORVIK ADJUSTED OFFENSE**
- **BARTTORVIK ADJUSTED DEFENSE**
- **BARTHAG**
- **ELITE SOS**
- **BARTTORVIK ADJUSTED TEMPO**
- **2PT %**
- **3PT %**
- **FREE THROW %**
- **EFG %**
- **FREE THROW RATE**
- **3PT RATE**
- **ASSIST %**
- **OFFENSIVE REBOUND %**
- **DEFENSIVE REBOUND %**
- **BLOCK %**
- **TURNOVER %**
- **2PT % DEFENSE**
- **3PT % DEFENSE**
- **FREE THROW % DEFENSE**
- **EFG % DEFENSE**
- **FREE THROW RATE DEFENSE**
- **3PT RATE DEFENSE**
- **OP ASSIST %**
- **OP O REB %**
- **OP D REB %**
- **BLOCKED %**
- **TURNOVER % DEFENSE**
- **WINS ABOVE BUBBLE**
- **WIN %**
- **POINTS PER POSSESSION OFFENSE**
- **POINTS PER POSSESSION DEFENSE**

See the Kaggle page for descriptions of each of the statistics listed above.

## Game Results
### 1985-2021
Results of each March Madness game from *1985-2021* were downloaded from this Kaggle dataset 
([1985-2021 Results](https://www.kaggle.com/datasets/woodygilbertson/ncaam-march-madness-scores-19852021)). The dataset provides the following information for each matchup:

- **YEAR**
- **ROUND**
- **WSEED**
- **WTEAM**
- **WSCORE**
- **LSEED**
- **LTEAM**
- **LSCORE**

See the Kaggle page for descriptions of each of the statistics listed above.

### 2022-2023
The *2022* & *2023* tournament game results were not included in the above Kaggle dataset, so those results were scraped from NCAA.com 
([2022 Results](https://www.ncaa.com/news/basketball-men/article/2022-07-12/2022-ncaa-bracket-mens-march-madness-scores-stats-records),
 [2023 Results](https://www.ncaa.com/news/basketball-men/article/2023-04-18/2023-ncaa-bracket-scores-stats-march-madness-mens-tournament)). The scraping of this data was accomplished 
 using Python's `requests` and `Beautiful Soup` libraries. See [Notebooks/data_collection.ipynb](Notebooks/data_collection.ipynb).

 # Preprocessing
 The following steps were taken to prepare the data for use in model training. See [Notebooks/preprocessing.ipynb](Notebooks/preprocessing.ipynb) for details.

 ## Drop Columns
 The following columns were dropped from the team stats dataset:

 - **ROUND** (*introduces data leakage since at the time of prediction, we won't know how far the team will make it in the tournament*)
 - **TEAM.1** (*redundant column included at the end of the dataset*)

 ## Filter Data
 Due to only having team statistics for teams beginning in the *2008* tournament, game results from *1985-2007* were dropped from the dataset.

 ## Standardize Naming Conventions
 Across the 3 sources of data (2 separate Kaggle datasets and data scraped from NCAA.com), various naming conventions were used for the teams involved (e.g. Michigan St. versus 
 Michigan State, USC versus Southern California, etc.). To avoid the problems this would create when joining the datasets together, consistent naming conventions were applied across 
 all datasets.

 ## Fix Errors
 On a few rare occasions, errors or typos were introduced into the datasets (incorrect seeds or team names), so measures were taken to correct these mistakes.

 ## Feature Engineering
 The game results dataset differentiates the teams in the matchup as the winning team versus the losing team. However, the whole point of the model is to predict a winner and a loser 
 (more specifically if the better- or worse-seeded team will win), so the features `WSEED`, `WTEAM`, `WSCORE`, `LSEED`, `LTEAM`, and `LSCORE` were dropped and the following features 
 were defined:

 - **BETTER_SEED:** *Seed of the team with the superior seeding (lower number)*
 - **BETTER_TEAM:** *Name of the team with the superior seeding (lower number)*
 - **WORSE_SEED:** *Seed of the team with the inferior seeding (higher number)*
 - **WORSE_TEAM:** *Name of the team with the inferior seeding (higher number)*
 - **UPSET:** *Whether the worse seed beat the better seed (**this is the model target**)*

In the event of a matchup between two teams with equal seeds (a scenario only possible in the First Four, Final Four, or Championship Round), `WIN %` was used as the tiebreaker, 
with the team having the higher winning % being awarded the labels of `BETTER_SEED` and `BETTER_TEAM` respectively.

## Feature Selection
This is the point the project is currently at. Before training and evaluating the model, testing will be performed to determine the optimal combination of features to use in the 
model.
