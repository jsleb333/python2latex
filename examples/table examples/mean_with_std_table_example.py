from python2latex import Document, Table, italic
import numpy as np

"""
In this example, we show how the Table class can be used to produce large tables with mean and standard deviation. Such tables occur often in the field of machine learning where one has to compare multiple models across several datasets.
"""

# First, we create a class that automatically manages the mean and standard deviation of an array of results. The __format__ method will be used by the Table to typeset the numbers.
class MeanWithStd(float):
    def __new__(cls, array):
        mean = array.mean()
        instance = super().__new__(cls, mean)
        instance.mean = mean
        instance.std = array.std()
        return instance

    def __format__(self, format_spec):
        return f'{format(self.mean, format_spec)} \pm {format(self.std, format_spec)}'

# Second, obtain the data
n_datasets = 10
n_models = 4
n_draws = 5

data = np.full((n_datasets, n_models), 0, dtype=object)
for i, row in enumerate(data):
    for j, _ in enumerate(row):
        data[i, j] = MeanWithStd(np.random.rand(n_draws))

# Third, create the table

# Create a basic document
doc = Document(filename='mean_with_std_table_example', filepath='examples/table examples', doc_type='article', options=('12pt',))

# Create table
col, row = n_models + 1, n_datasets + 2
table = doc.new(Table(shape=(row, col), float_format='.3f'))

# Set a caption
table.caption = f'Mean test accuracy (and standard deviation) of {n_models} models on {n_datasets} datasets for {n_draws} different random states.'
table.caption_space = '10pt' # Space between table and caption.

# Set entries with slices
table[2:, 1:] = data
table[2:, 0] = [f'Dataset {i}' for i in range(n_datasets)]
table[0, 1:] = 'Models'
table[1, 1:] = [f'Model {i}' for i in range(n_models)]

# Add rules
table[1].add_rule()
table[0,1:3].add_rule(trim_left=True, trim_right=True)
table[0,3:].add_rule(trim_left=True, trim_right=True)

# Highlight best value up to tolerance and set every numbers in mathmode
mathmode = lambda content: f'${content}$'
mathbold = lambda content: f'$\\mathbf{{{content}}}$'
for dataset in range(2, n_datasets+2):
    table[dataset, 1:].highlight_best(best=mathbold, not_best=mathmode, atol=0.0025)

# Build the document
tex = doc.build()
print(tex)
