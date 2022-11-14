from googletrans import Translator

translator = Translator()


def transliterate_text(text: str) -> str:
    tr = translator.translate(text, src="ru")
    return tr.extra_data["origin_pronunciation"]
