import csv
import re
from os import path, listdir
from collections.abc import Iterable
import numpy as np
from pandas import DataFrame

# Code to get df from CellProfiler output csv files

class MatcherSet(set[str]):
    '''
    Collects multiple patterns for string matching.
    Patterns are treated as regex expressions (see https://docs.python.org/3/library/re.html#module-re).
    Creating a MatcherSet with one pattern can be done with: MatcherSet("pattern")
    For multiple elements you must do: MatcherSet(["p1", "p2"])
    '''

    def __init__(self, itr: Iterable[str] = []) -> None:
        # normally this will turn it into a set of individual characters.
        # override that behavior because it is a pain to deal with for single string patterns (which are quite common)
        if isinstance(itr, str):
            itr = [itr]
        super().__init__(itr)

    @classmethod
    def coerce(cls, patterns: Iterable[str]) -> 'MatcherSet':
        ''' Converts to MatcherSet if input is not already a MatcherSet '''
        if isinstance(patterns, cls):
            return patterns
        return cls(patterns)

    def matches(self, string: str) -> bool:
        '''
        Returns true if the the passed string contains any of the stored regex patterns
        If empty, it will return False. To unconditionally return True, add a pattern with an empty string ''
        '''
        for pattern in self:
            if re.search(pattern, string):
                return True
        return False

def filterdict(d: dict, filters: list[MatcherSet]) -> dict:
    '''
    Recursive multilevel dictionary filterer - returns a new dictionary containing only the items that match.
    Each level of depth has an associated MatcherSet object that keys are checked against.
    Keys are unconditionally added when we run out of filters
    '''
    if len(filters) > 0 and filters[0]:
        res = {}
        for k, v in d.items():
            if filters[0].matches(k):
                if isinstance(v, dict):
                    res[k] = filterdict(v, filters[1:])
                else:
                    res[k] = v
        return res
    return d.copy()

class MarkerFeatures(dict[str, float]):
    ''' Represents a collection of features associated with a single cell and marker; i.e a single row in a single csv file '''
    @classmethod
    def fromFile(cls, filepath: str, featurematchers: Iterable[str]='') -> list['MarkerFeatures']:
        '''
        Helper to simplify importing.
        Returns a list of MarkerFeatures corresponding to each of the rows in the given files (cells)
        '''
        featurematchers = MatcherSet.coerce(featurematchers)
        res = []
        with open(filepath) as file:
            for row in csv.DictReader(file):
                features = cls()
                for k, v in filterdict(row, [featurematchers]).items():
                    features[k] = float(v)
                res.append(features)
        return res

class CellMarkers(dict[str, MarkerFeatures]):
    '''
    Represents a collection of markers associated with a single cell;
    i.e. all rows of the same index across files with the same celltype prefix
    '''

    @classmethod
    def fromFiles(cls, filepaths: list[str], markermatchers: Iterable[str]='', featurematchers: Iterable[str]='') -> list['CellMarkers']:
        '''
        Helper to simplify importing
        Returns a list of CellMarkers, each row corresponding to a single cell
        '''
        markermatchers = MatcherSet.coerce(markermatchers)
        res = []
        for fp in filepaths:
            basename, _ = path.splitext(path.basename(fp))
            splitname = basename.split("_")
            if len(splitname) < 2 or not markermatchers.matches(splitname[1]):
                print(f"skipping csv file '{basename}'")
                continue

            markername = splitname[1].upper()
            allmarkerfeatures = MarkerFeatures.fromFile(fp, featurematchers=featurematchers)

            if len(res) == 0:
                numcells = len(allmarkerfeatures)
                if numcells == 0:
                    return []

                for _ in range(numcells):
                    res.append(cls())

            if markername in res[0]:
                raise Exception(f"Found duplicate marker: {markername}")

            j = 0
            markerindices = []
            
            for i, markerfeatures in enumerate(allmarkerfeatures):
                if markerfeatures['ImageNumber'] not in markerindices:
                    markerindices.append(markerfeatures['ImageNumber'])
                    res[j][markername] = markerfeatures
                    j += 1
                    
            """
            See if the number is repeating
            if repeating, append them all
            """
                

        return res

class Cells(dict[str, CellMarkers]):
    ''' Represents a collection of cells '''

    @classmethod
    def fromDir(cls, dirpath: str, cellmatchers: Iterable[str]='',
            markermatchers: Iterable[str]='', featurematchers: Iterable[str]='') -> 'Cells':
        '''
        Gets all cells from csvs in a directory.
        cellmatchers, markermatchers, and featurematchers can be specified to ignore unnecessary data
        '''
        cellmatchers = MatcherSet.coerce(cellmatchers)
        cells = cls()
        if not path.isdir(dirpath):
            raise Exception(f'{dirpath} is not a directory')

        cellfiles = {}
        for filename in listdir(dirpath):
            rawname, ext = path.splitext(filename)
            if ext != ".csv":
                continue
            
            splitname = rawname.split("_")
            if len(splitname) < 3 or not cellmatchers.matches(splitname[0]):
                print(f"skipping csv file '{filename}'")
                continue

            cellfiles.setdefault(splitname[0], []).append(path.join(dirpath, filename))
        
        for cellname, files in cellfiles.items():
            cellmarkers = CellMarkers.fromFiles(files, markermatchers=markermatchers, featurematchers=featurematchers)
            for i, markers in enumerate(cellmarkers):
                cells[cellname+str(i)] = markers

        return cells

    def filter(self, cellmatchers: Iterable[str]='', markermatchers: Iterable[str]='', featurematchers: Iterable[str]='') -> 'Cells':
        return Cells(filterdict(self, [MatcherSet.coerce(matchers) for matchers in [cellmatchers, markermatchers, featurematchers]]))

    def getFeatureDataFrame(self, cellmatchers: Iterable[str]='', markermatchers: Iterable[str]='', featurematchers: Iterable[str]='') -> DataFrame:
        '''
        Returns a pandas.DataFrame object using cells as indices (rows) and markers as columns.
        Supports the normal filtering. After filters apply, you should have only 1 feature per column.
        The feature names don't necessarily need to be the same, so use with caution.
        '''
        filtered = self.filter(cellmatchers, markermatchers, featurematchers)
        if len(filtered) == 0:
            return DataFrame()
        cellnames = list(filtered.keys())
        markernames = list(filtered[cellnames[0]].keys())
        data = np.zeros((len(cellnames), len(markernames)))

        for i, cellname in enumerate(cellnames):
            for j, markername in enumerate(markernames):
                featurevals = list(filtered[cellname][markername].values())
                if len(featurevals) != 1:
                    raise Exception("Should be exactly 1 feature, found " + str(len(featurevals)))
                data[i, j] = featurevals[0]

        return DataFrame(data, index=cellnames, columns=markernames)

if __name__ == "__main__":
    c = Cells.fromDir("../All Data 2-24-22")
    df = c.getFeatureDataFrame(featurematchers="AreaShape_Area", markermatchers=["at", "cona"], cellmatchers="[1-4]")
    df = df.sort_index(ascending=False)
    print(df)
    m = MatcherSet("help")
    print(MatcherSet(m))
