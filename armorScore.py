import itertools
import numpy as np
import pandas as pd
#test comment
class armorScorer():
    def __init__(self, armordf, exoticMethod='prefer', statpins=None):
        self.armorDF = armordf.set_index('Id')
        self.stats = ['Mobility (Base)', 'Recovery (Base)', 'Discipline (Base)',
                 'Intellect (Base)', 'Strength (Base)', 'Total (Base)']
        self.required = ['Name', 'Hash', 'Tier', 'Type', 'Equippable', 'Mobility (Base)',
                    'Recovery (Base)', 'Discipline (Base)',
                    'Intellect (Base)', 'Strength (Base)', 'Total (Base)']
        self.armorTypes = ['Helmet', 'Chest Armor', 'Gauntlets', 'Leg Armor']
        self.exoticMethod = exoticMethod
        self.statpins = statpins

        for r in self.required:
            if r not in self.armorDF.columns.values:
                print("Input file is missing required column: {}".format(r))
                print("Use ArmorScore.py -h to view list of required columns")
                return

    def armorDictToDF(self, armordict):
        df = pd.DataFrame(list(itertools.product(*armordict.values())), columns=[k for k in armordict.keys()])
        return df

    def permuteStats(self):
        combinedStats = []
        for n in range(2, 7):
            combinedStats.append(list(set([tuple(sorted(x)) for x in itertools.permutations(self.stats, n)])))

        self.combinedStats = [list(item) for sublist in combinedStats for item in sublist]
        self.combinedStatNames = [" | ".join(x) for x in self.combinedStats]
        return

    def buildArmorDict(self, df):
        return {t: df.loc[(df['Type'] == t)].index.values.tolist() for t in self.armorTypes}

    def appendStats(self, df):
        frames = []
        for type in self.armorTypes:
            tempdf = df.set_index(type).join(self.armorDF[self.stats]).reset_index()
            tempdf.rename(columns={'index': type}, inplace=True)
            frames.append(tempdf)

        newdf = pd.concat(frames)
        return newdf.groupby(self.armorTypes).sum().reset_index()

    def permuteArmor(self):
        nonExoticDict = self.buildArmorDict(self.armorDF[self.armorDF['Tier'] !='Exotic'])

        exoticDict = self.buildArmorDict(self.armorDF[self.armorDF['Tier'] == 'Exotic'])

        exoticFrames = []
        for e in exoticDict.keys():
            d = {t: (exoticDict[t] if t == e else nonExoticDict[t]) for t in self.armorTypes}
            exoticFrames.append(self.armorDictToDF(d))
        exoticDF = pd.concat(exoticFrames,axis=0)
        exoticDF = self.appendStats(exoticDF)

        if self.exoticMethod == 'pin':
            self.permutedFrames = [exoticDF]
        elif self.exoticMethod == 'prefer':
            nonExoticDF = self.armorDictToDF(nonExoticDict)
            nonExoticDF = self.appendStats(nonExoticDF)
            self.permutedFrames = [exoticDF, pd.concat([exoticDF, nonExoticDF], axis=0)]
        else:
            nonExoticDF = self.armorDictToDF(nonExoticDict)
            nonExoticDF = self.appendStats(nonExoticDF)
            self.permutedFrames = [pd.concat([exoticDF, nonExoticDF], axis=0)]

    def score(self, tierstats):
        if not hasattr(self, 'permutedFrames'):
            self.permuteArmor()

        if not hasattr(self, 'combinedStatNames'):
            self.permuteStats()

        self.winningIDs = []
        self.winnerCount = 0

        for frame in self.permutedFrames:

            for c in zip(self.combinedStats, self.combinedStatNames):
                frame[c[1]] = pd.to_numeric(frame[c[0]].sum(axis=1))

            if tierstats is True:
                frame[self.stats] = frame[self.stats].divide(10).apply(np.floor).multiply(10)

            for c in zip(self.combinedStats, self.combinedStatNames):
                frame[c[1]] = pd.to_numeric(frame[c[0]].sum(axis=1))


            for stat in self.stats + self.combinedStatNames:
                winners = frame.loc[[frame[stat].idxmax()]]
                for index, row in winners.iterrows():
                    self.winningIDs.append(row[self.armorTypes].values.tolist())
                    self.winnerCount += 1

        self.winningIDs = [item for sublist in self.winningIDs for item in sublist]
        self.scores = pd.DataFrame(dict(Id=self.winningIDs, armorScore=[1/self.winnerCount for n in self.winningIDs]))
        self.scores = self.scores.groupby('Id').sum()
        return self.scores




