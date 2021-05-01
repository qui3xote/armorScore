import time
import itertools
import argparse

import pandas as pd

REQUIRED = ['Name','Hash','Tier','Type','Equippable','Mobility (Base)',
    'Recovery (Base)','Discipline (Base)',
    'Intellect (Base)','Strength (Base)','Total (Base)']
STATS = ['Mobility (Base)', 'Recovery (Base)','Discipline (Base)',
    'Intellect (Base)','Strength (Base)','Total (Base)']
ARMOR_TYPES = ['Helmet','Chest Armor','Gauntlets','Leg Armor']

# group = parser.add_mutually_exclusive_group()
# group.add_argument("-v", "--verbose", action="store_true")
# group.add_argument("-q", "--quiet", action="store_true")
#parser.add_argument("x", type=int, help="the base")
#parser.add_argument("y", type=int, help="the exponent")


def main():
    parser = argparse.ArgumentParser(description="Score armor for potential usefulness")
    parser.add_argument("-f", "--filename", type=str, help="DIM export file to be processed.")
    parser.add_argument("-o", "--outputfile", type=str, default=None, help="Where to store the results.")
    parser.add_argument("-l", "--limit", type=int, default=None, help="For testing only. Limit number of rows iterrated")
    parser.add_argument("-c", "--clear", action="store_true", default=False, help="For testing only. Clear notes column.")
    args = parser.parse_args()

    df = pd.read_csv(args.filename)
    for r in REQUIRED:
        if r not in df.columns.values:
            print("Input file is missing required column: {}".format(r))
            print("Use ArmorScore.py -h to view list of required columns")
            return
    if args.clear is True:
        df['Notes'] = ''

    df['score'] = pd.Series([0.0 for x in range(len(df.index))], index=df.index)
    df = df[df['Type'].isin(ARMOR_TYPES)] #Get rid of class armor

    characters = df['Equippable'].unique().tolist()
    combined_stat_columns = []
    
    #Generate all possible combinations of stats
    for n in range(2,7):
        combined_stat_columns.append(list(set([tuple(sorted(x)) for x in itertools.permutations(STATS,n)])))

    combined_stat_columns = [list(item) for sublist in combined_stat_columns for item in sublist]
    combined_stat_column_names = [" | ".join(x) for x in combined_stat_columns]


    for character in characters:
        df.set_index('Id',inplace=True)
        print('Scoring {num} {char} armor pieces'.format(num=df[df['Equippable']==character].shape[0], char=character))
        start = time.time()
        
        #Get all the armor permutations and create a dataframe
        armor = {t:df.loc[(df['Equippable']==character) & (df['Type']==t)].index.values.tolist() for t in ARMOR_TYPES}
        armor_permutations_df = pd.DataFrame(list(itertools.product(*armor.values())), columns=[k for k in armor.keys()])


        if args.limit is not None:
            armor_permutations_df = armor_permutations_df.loc[[x for x in range(args.limit)]]

        #Getthe stats for each armor piece for each permutation.
        frames = []
        for type in ARMOR_TYPES:
            frames.append(armor_permutations_df.set_index(type).join(df[STATS]).reset_index())
            
        #Is there a better way to prevent index resetting from losing the name?
        for d in zip(frames,ARMOR_TYPES):
            d[0].rename(columns={'index':d[1]},inplace=True)

        #Recombine indivudal armor dfs and use groupby to sum into final loadout stats
        armor_permutations_df = pd.concat(frames)
        armor_permutations_df = armor_permutations_df.groupby(ARMOR_TYPES).sum().reset_index()

        #build a df with one column for every stat combination and fill in with the sums from armor_permutations
        #This can probably be done without a seperate dataframe
        combine_df = pd.DataFrame(columns=combined_stat_column_names)
        for c in zip(combined_stat_columns,combined_stat_column_names):
            combine_df[c[1]] = armor_permutations_df[c[0]].sum(axis=1)

        #Append the combined stats on tto he armor permutations.
        armor_permutations_df = pd.concat([armor_permutations_df, combine_df],axis=1)

        #not sure why these aren't numeric to start with, but what's another for loop between friends?
        for col in STATS + combined_stat_column_names:
            armor_permutations_df[col] = pd.to_numeric(armor_permutations_df[col])

        #Get all the armor pieces in each winning permutation
        winning_ids = []
        for stat in STATS + combined_stat_column_names:
            winning_ids.append(armor_permutations_df.loc[armor_permutations_df[stat].idxmax()][ARMOR_TYPES].values.tolist())

        #Add up the scores and put them back on the original data frame
        df.reset_index(inplace=True)
        for i in [item for sublist in winning_ids for item in sublist]:
            df.iloc[df.index[df['Id']==i],df.columns.get_loc('score')] += 1/len(STATS + combined_stat_column_names)

        print('{num} {char} armor combinations scored in {seconds} seconds'.format(num=armor_permutations_df.shape[0], char=character, seconds = time.time() - start))

    #Put the scores into the notes column and write it out to file....
    df['score'] = df['score'].round(2)
    df['score'] = "{ArmorScore: " + df['score'].astype(str) + "}"
    df['Notes'] = df['Notes'].fillna('').astype(str)
    df['Notes'] = df['score'] + df['Notes']

    df.to_csv(args.outputfile)


if __name__ == '__main__':
   main()
