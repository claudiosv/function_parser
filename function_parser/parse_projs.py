import function_parser
import os

import pandas as pd

from function_parser.language_data import LANGUAGE_METADATA
from function_parser.process import DataProcessor
from tree_sitter import Language
from tqdm import tqdm

language = "python"
DataProcessor.PARSER.set_language(
    Language(os.path.join(function_parser.__path__[0], "tree-sitter-languages.so"), language)
)
processor = DataProcessor(
    language=language, language_parser=LANGUAGE_METADATA[language]["language_parser"]
)

for i in tqdm(range(1,51)):
    dependee = f"project{i}"
    print(dependee)
    definitions = processor.process_dee(dependee, ext=LANGUAGE_METADATA[language]["ext"])
    df = pd.DataFrame(definitions)
    df.to_parquet(f"df_project{i}.parquet")
print("Done!")
# conc = pd.concat(dfs)
# conc.to_json("df_all.json")

"""
pip install coverage

if [[ $1 == "scikit-learn" ]]

then

    timeout -k 10s $5 coverage run -m  pytest --import-mode=importlib $3 #tests for scikit-learn need importlib to locate conftest

else

    timeout -k 10s $5 coverage run -m  pytest $3
    """