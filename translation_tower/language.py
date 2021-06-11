from pathlib import Path
import pandas as pd


class WrongLanguage(Exception):
    pass


class Language:
    def __init__(self, config_path: Path):
        self._df = pd.read_csv(config_path, sep=",", quotechar='"')
        self._df.set_index("code")

    def get(self, language: str, translator: str, for_translation=False):
        line = self._df.loc[self._df["code"] == language]
        if line.empty:
            raise WrongLanguage(
                f"Invalid language code `{language}`\n"
                f"{self.get_available_languages(translator)}"
            )

        else:
            converted_language = line[translator].values[0]
            if pd.isna(converted_language):
                raise ValueError(
                    f"Invalid language code `{language} for translator `{translator}`\n"
                    f"{self.get_available_languages(translator)}"
                )
            if translator == "deepl":
                if not for_translation:
                    only_for_translation = line["deepl_only_translation"].values[0]
                    if only_for_translation == 1:
                        raise WrongLanguage(
                            f"Invalid language code `{language} for translator {translator}.\n"
                            f"This language only exists for translations\n"
                            f"{self.get_available_languages(translator)}"
                        )
            return converted_language

    def get_available_languages(self, translator: str) -> str:
        result = f"Allowed language for `{translator}`\n:"
        lines = self._df.loc[self._df[translator].notna()]
        for line in lines.itertuples():
            result += f"\t- {line.code} ({line.description})\n"
        return result
