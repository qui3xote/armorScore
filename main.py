import time
import itertools
import re
import argparse

from armorScore import armorScorer
import pandas as pd

def cleanOldScore(note):
    return re.sub("{armorscore[^}]*}", '', note, flags=re.I)

#test comment
def main():
    parser = argparse.ArgumentParser(description="Score armor for potential usefulness")
    parser.add_argument("filename", type=str, help="DIM export file to be processed.")
    parser.add_argument("-o", "--outputfile", type=str, default=None, help="Where to store the results.")
    parser.add_argument("-b", "--includeblue", action="store_true", default=False,
                        help="Incude uncommon (blue) items in the scoring.")
    parser.add_argument("-t", "--tierstats", action="store_true", default=False,
                        help="Choose winners based on stat tier rather than raw stats. Less aggressive culling.")
    parser.add_argument("-e", "--exotics", type=str, choices=['pin', 'prefer', 'ignore'], default='prefer',
                        help="""If 'pin', only look at loadouts that include an exotic. If 'ignore'. look at all valid
                        loadouts and pick the highest stats. If 'prefer', run both modes and combine the scores. By
                        default, armorScore runs 'prefer'.""")
    #parser.add_argument("-p", "--pinstats", type=str, default=None, nargs='+', choices=['I','M','D','S','Rc','Rs','Class'],
    #                     help="Only consider stat combinations that include the chosen stat(s).")
    parser.add_argument("-l", "--limit", type=int, default=None, help="For testing only. Limit number of rows iterated")
    parser.add_argument("-c", "--clear", action="store_true", default=False,
                        help="Just clean out armorscores from notes column and exit")
    args = parser.parse_args()

    dimDF = pd.read_csv(args.filename)

    dimDF['Notes'] = dimDF['Notes'].fillna('').astype(str)
    dimDF['Notes'] = dimDF['Notes'].apply(lambda x: cleanOldScore(x))

    if args.clear is True:
        dimDF.to_csv(args.outputfile)
        return

    if args.includeblue is True:
        rarity = ['Uncommon', 'Legendary', 'Exotic']
    else:
        rarity = ['Legendary', 'Exotic']

    # Get rid of class armor & lower tier items
    dimDF = dimDF[dimDF['Tier'].isin(rarity)]

    characters = dimDF['Equippable'].unique().tolist()

    scoreFrames = []
    for character in characters:
        scorer = armorScorer(dimDF[dimDF['Equippable']==character], exoticMethod=args.exotics)
        scoreFrames.append(scorer.score(args.tierstats))
        print("Found {} winning loadouts for {}".format(scorer.winnerCount, character))

    scoreDF = pd.concat(scoreFrames,axis=0)
    dimDF = dimDF.join(scoreDF, on='Id', how='left')
    dimDF['armorScore'] = dimDF['armorScore'].fillna(0.0)
    dimDF['armorScore'] = dimDF['armorScore'].round(2)
    dimDF['Notes'] = "{armorScore: " + dimDF['armorScore'].astype(str) + "}" + dimDF['Notes']

    dimDF.to_csv(args.outputfile)


if __name__ == '__main__':
    main()
