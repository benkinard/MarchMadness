import dill
import pandas as pd

ROUND_NAMES = ['First Four', 'Round of 64', 'Round of 32', 'Sweet 16', 'Elite 8', 'Final Four', 'National Championship']


def compute_difference_in_stats(matchups: pd.DataFrame):
    for bs_col in matchups.columns[5:27]:
        ws_col = bs_col.replace("_BS", "_WS")

        better_seed_stat = matchups[bs_col]
        worse_seed_stat = matchups[ws_col]
        matchups.drop(columns=[bs_col, ws_col], inplace=True)

        col = bs_col[:-3]
        matchups[col] = better_seed_stat - worse_seed_stat


def id_better_and_worse_team(matchups: pd.DataFrame) -> pd.DataFrame:
    better_seeds = []
    better_teams = []
    worse_seeds = []
    worse_teams = []

    for row in matchups.iterrows():
        row = row[1]
        if row['SEED_A'] == row['SEED_B']:
            if row['WIN % TEAM_A'] < row['WIN % TEAM_B']:
                better_seeds.append(row['SEED_B'])
                better_teams.append(row['TEAM_B'])
                worse_seeds.append(row['SEED_A'])
                worse_teams.append(row['TEAM_A'])
            else:
                better_seeds.append(row['SEED_A'])
                better_teams.append(row['TEAM_A'])
                worse_seeds.append(row['SEED_B'])
                worse_teams.append(row['TEAM_B'])
        elif row['SEED_A'] < row['SEED_B']:
            better_seeds.append(row['SEED_A'])
            better_teams.append(row['TEAM_A'])
            worse_seeds.append(row['SEED_B'])
            worse_teams.append(row['TEAM_B'])
        else:
            better_seeds.append(row['SEED_B'])
            better_teams.append(row['TEAM_B'])
            worse_seeds.append(row['SEED_A'])
            worse_teams.append(row['TEAM_A'])

    matchups['BETTER_SEED'] = better_seeds
    matchups['BETTER_TEAM'] = better_teams
    matchups['WORSE_SEED'] = worse_seeds
    matchups['WORSE_TEAM'] = worse_teams

    return matchups.copy()[['ROUND', 'BETTER_SEED', 'BETTER_TEAM', 'WORSE_SEED', 'WORSE_TEAM']]


def main():
    team_stats = pd.read_csv('TeamStats_2026.csv')
    tournament_matchups = pd.read_csv('RoundOf64_2026.csv')

    while len(tournament_matchups) > 0:
        print(f"{ROUND_NAMES[tournament_matchups['ROUND'][0]]}", "-" * 25, sep="\n")

        # Determine which team in the matchup should be considered the better seed
        win_pct = team_stats.copy().loc[:, ['SEED', 'TEAM', 'WIN %']]
        tournament_matchups = tournament_matchups.join(win_pct.set_index(['SEED', 'TEAM']), on=['SEED_A', 'TEAM_A'])
        tournament_matchups = tournament_matchups.join(win_pct.set_index(['SEED', 'TEAM']), on=['SEED_B', 'TEAM_B'],
                                                       lsuffix=' TEAM_A', rsuffix=' TEAM_B')
        tournament_matchups = id_better_and_worse_team(tournament_matchups)

        # Print information to console
        for index, row in tournament_matchups.iterrows():
            print(f"{row['BETTER_SEED']}. {row['BETTER_TEAM']} vs. {row['WORSE_SEED']}. {row['WORSE_TEAM']}")

        # Join team stats data
        tournament_matchups = tournament_matchups.join(team_stats.set_index(['SEED', 'TEAM']),
                                                       on=['BETTER_SEED', 'BETTER_TEAM'])
        tournament_matchups = tournament_matchups.join(team_stats.set_index(['SEED', 'TEAM']),
                                                       on=['WORSE_SEED', 'WORSE_TEAM'], lsuffix='_BS', rsuffix='_WS')

        # Replace the individual team statistics as features with the difference between each team's stats
        compute_difference_in_stats(tournament_matchups)

        # Drop the team names from the dataset
        X = tournament_matchups.drop(columns=['BETTER_TEAM', 'WORSE_TEAM'])

        # Load the model & make predictions
        with open('Data/model.pkl', 'rb') as pickle:
            model = dill.load(pickle)

        upsets = model.predict(X)

        # Set up the next round of matchups based on upset predictions
        if len(tournament_matchups) == 1:
            if upsets[0] == 1:
                champions = {'SEED': tournament_matchups.iloc[0, list(tournament_matchups.columns).index('WORSE_SEED')],
                             'TEAM': tournament_matchups.iloc[0, list(tournament_matchups.columns).index('WORSE_TEAM')]}
            else:
                champions = {'SEED': tournament_matchups.iloc[0, list(tournament_matchups.columns).index('BETTER_SEED')],
                             'TEAM': tournament_matchups.iloc[0, list(tournament_matchups.columns).index('BETTER_TEAM')]}
            tournament_matchups = pd.DataFrame()
        else:
            next_round_matchups = pd.DataFrame(columns=['ROUND', 'SEED_A', 'TEAM_A', 'SEED_B', 'TEAM_B'])
            next_round_matchups['ROUND'] = [tournament_matchups['ROUND'][0] + 1] * (len(tournament_matchups) // 2)
            for idx, isUpset in enumerate(upsets):
                row = idx // 2
                start_col_pos = (idx % 2) * 2
                if isUpset:
                    next_round_matchups.iloc[row, start_col_pos + 1] = tournament_matchups.iloc[idx, list(tournament_matchups.columns).index('WORSE_SEED')]
                    next_round_matchups.iloc[row, start_col_pos + 2] = tournament_matchups.iloc[idx, list(tournament_matchups.columns).index('WORSE_TEAM')]
                else:
                    next_round_matchups.iloc[row, start_col_pos + 1] = tournament_matchups.iloc[idx, list(tournament_matchups.columns).index('BETTER_SEED')]
                    next_round_matchups.iloc[row, start_col_pos + 2] = tournament_matchups.iloc[idx, list(tournament_matchups.columns).index('BETTER_TEAM')]

            tournament_matchups = next_round_matchups.copy()
        print()

    print(f"National Champions\n{champions['SEED']}. {champions['TEAM']}")


if __name__ == "__main__":
    main()
