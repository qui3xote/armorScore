###############################################################################
# ArmorScore O.1b
# This tool takes an exported csv of armor from DIM and runs an algorithm
# to determine how valuable each piece is relative to the rest of your armor.
# ArmorScore works by looking at every possible permutation of armor and
# every combination of 1,2,3,4,5 and 6 stats to determine which combination has
# the highest score. If a piece of armor is in the 'best' combination then it
# receives 1 point.  At the end, each piece's score is divided by the total
# number of winning combinations. So a helmet with a score of '.25' was present
# 25% of winning combinations.
#
# vO.1: Takes exported file and runs the algorithm above. It exports 1 final
# score and apends it to the 'notes' column (leaving existing notes intact).
# This can be reviewed in excel or reimported directly to DIM.
################################################################################


# Dev notes
# CL args: filename, class
# Read file in to pandas
# Get lists of armor by type FOR A SPECIFIC CHARACTER TYPE (exclude class item)
# - how to handle exotics? Maybe filter out for v0.1?
# Generate crossproduct of all pieces that can be combined
# Generate crossproduct of possible stat combinations
# For each stat combo, find the top scoring combo. +1 to scores for each piece
# in that set
# Divide scores by sum of scores
# Append (pre-append?) to notes: {ArmorScore:0.25}
# write to {filename}_scored_{timestamp}.csv

# Future iterations:
# 'Exclude Blue' filter
# Handle exotics: allow in but eliminate unequippable combinations
# Prefer Exotics: run additional 'bests' for each exotic (flag)
# Specific Exotics: Pick which pieces you want to Prefer (flag)
# Specify stat combos or specific stats (flag)
# Rules based tagging?
# Flag to clean out ArmorScore from notes
# on re-run, overwrite existing scores

import time
import itertools
import argparse

import pandas as pd

REQUIRED = ['Name','Hash','Tier','Type','Equippable','Mobility (Base)',
    'Recovery (Base)','Discipline (Base)',
    'Intellect (Base)','Strength (Base)','Total (Base)']
STATS = ['Mobility (Base)', 'Recovery (Base)','Discipline (Base)',
    'Intellect (Base)','Strength (Base)','Total (Base)']
VALID_TYPES = ['Helmet','Chest Armor','Gauntlets','Leg Armor']
# group = parser.add_mutually_exclusive_group()
# group.add_argument("-v", "--verbose", action="store_true")
# group.add_argument("-q", "--quiet", action="store_true")
#parser.add_argument("x", type=int, help="the base")
#parser.add_argument("y", type=int, help="the exponent")

# args = {}
# args['filename'] = './destinyArmor.csv'
# args['limit'] = None
# args['outputfile'] = './test.csv'
# character = 'Hunter'

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
            #return
    if args.clear is True:
        df['Notes'] = ''

    df['score'] = pd.Series([0.0 for x in range(len(df.index))], index=df.index)
    df = df[df['Type'].isin(VALID_TYPES)]

    characters = df['Equippable'].unique().tolist()
    combine_columns = []
    for n in range(2,7):
        combine_columns.append(list(set([tuple(sorted(x)) for x in itertools.permutations(STATS,n)])))

    combine_columns = [list(item) for sublist in combine_columns for item in sublist]
    combine_column_names = [" | ".join(x) for x in combine_columns]


    armor_frames = []

    for character in characters:
        df.set_index('Id',inplace=True)
        print('Scoring {num} {char} armor pieces'.format(num=df[df['Equippable']==character].shape[0],char=character))
        start = time.time()
        armor = {t:df.loc[(df['Equippable']==character) & (df['Type']==t)].index.values.tolist() for t in VALID_TYPES}
        armor_df = pd.DataFrame(list(itertools.product(*armor.values())), columns=[k for k in armor.keys()])


        if args.limit is not None:
            armor_df = armor_df.loc[[x for x in range(args.limit)]]

        stat_sums = pd.DataFrame(columns=STATS)

        combine_df = pd.DataFrame(columns=combine_column_names)

        frames = []
        for type in VALID_TYPES:
            frames.append(armor_df.set_index(type).join(df[STATS]).reset_index())

        for d in zip(frames,VALID_TYPES):
            d[0].rename(columns={'index':d[1]},inplace=True)

        armor_df = pd.concat(frames)
        armor_df = armor_df.groupby(VALID_TYPES).sum().reset_index()

        for c in zip(combine_columns,combine_column_names):
            combine_df[c[1]] = armor_df[c[0]].sum(axis=1)

        armor_df = pd.concat([armor_df, combine_df],axis=1)

        for col in STATS + combine_column_names:
            armor_df[col] = pd.to_numeric(armor_df[col])

        winning_ids = []
        for stat in STATS + combine_column_names:
            winning_ids.append(armor_df.loc[armor_df[stat].idxmax()][VALID_TYPES].values.tolist())

        df.reset_index(inplace=True)
        for i in [item for sublist in winning_ids for item in sublist]:
            df.iloc[df.index[df['Id']==i],df.columns.get_loc('score')] += 1/len(STATS + combine_column_names)


        print('{num} {char} armor combinations scored in {seconds} seconds'.format(num=armor_df.shape[0], char=character, seconds = time.time() - start))

    df['score'] = df['score'].round(2)
    df['score'] = "{ArmorScore: " + df['score'].astype(str) + "}"
    df['Notes'] = df['Notes'].fillna('').astype(str)
    df['Notes'] = df['score'] + df['Notes']

    df.to_csv(args.outputfile)


if __name__ == '__main__':
   main()
