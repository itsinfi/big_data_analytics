# Imports------------------------------------------------------------------------------------------------------------------------------------------------
import sys
import math
import shutil
from itertools import combinations
from collections import defaultdict


# Arguments------------------------------------------------------------------------------------------------------------------------------------------------
csv_rel_path = "data/warenkorb.csv"
"""
The relative path (based from the project root) to the csv file that shall be analyzed.
"""

min_support = 0.5
"""
The minimal support value. This is basically sets lowest relative frequency/occurence of one item set. Lower values will be ignored.
"""

min_conf = 0.75
"""
The minimal confidence value. This is basically sets lowest value of confidence for one association. Lower values will be ignored.
"""


# Read arguments------------------------------------------------------------------------------------------------------------------------------------------------
if len(sys.argv) > 2:    
    csv_rel_path = str(sys.argv[1])
    min_support = float(sys.argv[2])
    min_conf = float(sys.argv[3])


# Read and split CSV------------------------------------------------------------------------------------------------------------------------------------------------
def read_csv() -> str:
    """
    This function reads a csv file and returns the result as a string.
    This function does not support a header column for the CSV (only a list of entries per line that is seperated by ',' character)
    """
    file = open(file=csv_rel_path, mode="r")
    csv = file.read()
    file.close()
    return csv

def split_cells(csv: str) -> list[list[str]]:
    """
    This function splits the cells of a read csv string.
    The string is both split per line (to seperate the transactions) and per occurence of the character ',' (to seperate the items).
    """
    lines = csv.splitlines()
    cells = [line.split(sep=',') for line in lines]
    cells.remove(cells[0])
    for cell in cells:
        cell.sort()
    return cells


# Association analysis------------------------------------------------------------------------------------------------------------------------------------------------
def analyze_associations(cells: list[list[str]]) -> list[dict[str, any]]:
    """
    This function analyzes all possible associations and puts out all that exceed the min_support and min_conf values.
    """
    item_set_counts = count_item_sets(transactions=cells)
    total_transactions = len(cells)
    frequent_item_sets = filter_item_sets(item_set_counts=item_set_counts, total_transactions=total_transactions)
    return generate_rules(frequent_item_sets=frequent_item_sets, total_transactions=total_transactions)

def generate_item_sets(transaction: list[str], max_length: int) -> list[list[str]]:
    """
    This function generates all possible item set combinations.
    """
    item_sets = []
    for i in range(1, max_length + 1):
        item_sets.extend(combinations(iterable=transaction, r=i))
    return item_sets

def count_item_sets(transactions: list[list[str]]) -> dict[list[str], int]:
    """
    This function counts the item set frequency.
    """
    item_set_counts = defaultdict(int)
    for transaction in transactions:
        for item_set in generate_item_sets(transaction=transaction, max_length=len(transaction)):
            item_set_counts[item_set] += 1
    return item_set_counts

def filter_item_sets(item_set_counts: dict[list[str], int], total_transactions: int) -> dict[list[str], int]:
    """
    This function filters the item sets based on only those that are above the min_support value.
    """
    return {item_set: count for item_set, count in item_set_counts.items() if count / total_transactions >= min_support}

def generate_rules(frequent_item_sets: dict[list[str], int], total_transactions: int) -> list[dict[str, any]]:
    """
    This function generates all possible association rules.
    """
    rules = []
    for item_set in frequent_item_sets:
        for i in range(1, len(item_set)):
            antecedents = list(combinations(item_set, i))
            antecedentFreqProd = math.prod([frequent_item_sets[x] / total_transactions for x in antecedents])
            for x in antecedents:
                y = set(item_set) - set(x)
                lift = frequent_item_sets[item_set] / total_transactions / antecedentFreqProd
                confidence = frequent_item_sets[item_set] / frequent_item_sets[x]
                if (confidence >= min_conf):
                    rules.append({'x': x, 'y/x': y, 'conf': confidence, 'lift': lift})
    return rules


# Output ------------------------------------------------------------------------------------------------------------------------------------------------
def output(associations, cells):
    """
    This function puts out the results from the association analysis inside the console.
    """
    terminal_size = shutil.get_terminal_size().columns
    items = set([line for cell in cells for line in cell])
    i = 1
    print('\n')
    print('-' * terminal_size)
    print(f"Items: {items}")
    print('-' * terminal_size)
    for a in associations:
        print(f"{i}: {a['x']} -> {a['y/x']}, Confidence: {a['conf']:.2f}, Lift: {a['lift']:.4f}")
        i += 1
        print('-' * terminal_size)
    print('\n')
    return


# Function calls------------------------------------------------------------------------------------------------------------------------------------------------
csv = read_csv()
cells = split_cells(csv=csv)
associations = analyze_associations(cells=cells)
output(cells=cells, associations=associations)