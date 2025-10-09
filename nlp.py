from transformers import pipeline, AutoTokenizer, AutoModelForMaskedLM
import re


class NLPCorrector:
    """
    Uses a hybrid approach to correct and validate arithmetic expressions.
    It combines a BERT-based model for contextual character correction with
    a robust set of rules for fixing and validating syntactic structure.
    """

    def __init__(self, model_name: str = "tbs17/MathBERT"):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForMaskedLM.from_pretrained(model_name)
            self.fill_mask = pipeline(
                "fill-mask", model=self.model, tokenizer=self.tokenizer, top_k=10
            )
            print(f"Successfully initialized NLP model: {model_name}")
        except Exception as e:
            print(f"Warning: Failed to initialize NLP model {model_name}: {e}")
            print("Falling back to rule-based correction only.")
            self.fill_mask = None

    def correct_expression(self, text: str) -> str:
        # ... (correct_expression method remains the same) ...
        text = re.sub(r"\s+", "", text)
        corrections = {
            "x": "*",
            "X": "*",
            "l": "1",
            "I": "1",
            "O": "0",
            "S": "5",
            ",": ".",
            "q": "9",
            "b": "6",
            "z": "2",
            "B": "8",
        }
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        if self.fill_mask:
            text = self._contextual_correction(text)
        text = self._correct_syntax_with_rules(text)
        text = self._correct_parentheses(text)
        return text

    def _correct_syntax_with_rules(self, text: str) -> str:
        """
        Uses regular expressions to fix common structural syntactic errors.
        """
        text = re.sub(r"\(\(\)\s*(\d)", r"(*\1", text)

        text = re.sub(r"(\d)(\()", r"\1*\2", text)
        text = re.sub(r"(\))(\d)", r"\1*\2", text)

        text = (
            text.replace("--", "+")
            .replace("++", "+")
            .replace("-+", "-")
            .replace("+-", "-")
        )

        text = re.sub(r"([\+\-\*\/])(\))", r"\2", text)

        text = re.sub(r"\(\)", "", text)

        return text

    def _correct_parentheses(self, text: str) -> str:
        corrected_text = ""
        balance = 0

        for char in text:
            if char == "(":
                balance += 1
                corrected_text += char
            elif char == ")":
                if balance > 0:
                    balance -= 1
                    corrected_text += char
            else:
                corrected_text += char
        if balance > 0:
            corrected_text += ")" * balance

        return corrected_text

    def _contextual_correction(self, text: str) -> str:
        if not self.fill_mask:
            return text

        corrected_text = text
        valid_arithmetic_tokens = set("0123456789+-*/")

        while re.search(r"[a-zA-Z]", corrected_text):
            match = re.search(r"[a-zA-Z]", corrected_text)
            if not match:
                break

            start, end = match.span()
            masked_text = (
                corrected_text[:start]
                + self.tokenizer.mask_token
                + corrected_text[end:]
            )
            best_prediction = None

            try:
                predictions = self.fill_mask(masked_text)

                for pred in predictions:
                    token_str = pred["token_str"].strip()

                    if token_str in valid_arithmetic_tokens:
                        best_prediction = token_str
                        break

                if best_prediction:
                    corrected_text = (
                        corrected_text[:start] + best_prediction + corrected_text[end:]
                    )
                else:
                    corrected_text = corrected_text[:start] + corrected_text[end:]
            except Exception as e:
                print(
                    f"Error during BERT prediction: {e}. Removing offending character."
                )
                corrected_text = corrected_text[:start] + corrected_text[end:]

        return corrected_text
