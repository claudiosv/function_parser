import function_parser
import os

import pandas as pd

from function_parser.language_data import LANGUAGE_METADATA
from function_parser.process import DataProcessor
from tree_sitter import Language
from tqdm import tqdm
from pathlib import Path
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dir_path", type=Path)
    args = parser.parse_args()
    language = "python"
    DataProcessor.PARSER.set_language(
        Language(
            os.path.join(function_parser.__path__[0], "tree-sitter-languages.so"),
            language,
        )
    )
    processor = DataProcessor(
        language=language,
        language_parser=LANGUAGE_METADATA[language]["language_parser"],
    )

    for i in tqdm(range(1, 51)):
        dependee = (
            Path(os.environ["DYPYBENCH_PROJECTS_ROOT"]) / f"project{i}"
        ).resolve()
        print(dependee)
        if not dependee.exists():
            continue
        definitions = processor.process_project(
            str(dependee), ext=LANGUAGE_METADATA[language]["ext"]
        )
        df = pd.DataFrame(definitions)
        output_path = args.dir_path / f"df_project{i}.parquet"
        df.to_parquet(str(output_path))

    print("Done!")
