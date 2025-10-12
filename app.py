from flask import Flask, request, jsonify
import os
import tempfile
import uuid
from typing import Dict, Any, TypedDict

from nlp import NLPCorrector
from tokenizer import LexicalAnalyzer
from parser import SyntacticAnalyzer
from formatter import FormatConverter
from trocr_ocr import TrOCRModel
from sympy.parsing.latex import parse_latex


def format_math(expr, format):
    try:
        if format == "latex":
            return FormatConverter.to_latex(str(expr))
        elif format == "mathml":
            return FormatConverter.to_mathml(str(expr))
        else:
            return str(expr)
    except:
        return str(expr)


def process_raw_expression_pipeline(raw_expression: str, format: str = "latex"):
    try:
        corrected_expression = nlp_corrector.correct_expression(raw_expression)
    except Exception as e:
        raise ValueError(f"Correção NLP falhou: {e}")

    try:
        tokens = lexical_analyzer.tokenize(corrected_expression)

        if not lexical_analyzer.validate_tokens(tokens):
            raise ValueError("Sequência inválida de tokens na expressão")

    except Exception as e:
        raise ValueError(f"Análise Léxica falhou: {e}")

    try:
        parser = SyntacticAnalyzer(tokens)
        ast_root = parser.parse()
        final_result = parser.evaluate(ast_root)
        steps = parser.solve_by_substitution()
        normalized_expression = parser.to_string(ast_root)

    except Exception as e:
        raise ValueError(f"Análise Sintática falhou: {e}")

    return {
        "input_expression_raw": format_math(raw_expression, format),
        "expression_corrected": format_math(normalized_expression, format),
        "solution": {
            "steps": [format_math(step, format) for step in steps],
            "final_result": format_math(final_result, format),
        },
        "status": "success",
    }


def process_latex_pipeline(
    latex_expression: str, format: str = "latex"
) -> Dict[str, Any]:
    processed_expression = str(parse_latex(latex_expression))

    return process_raw_expression_pipeline(processed_expression, format)


def process_expression_pipeline(
    image_path: str, format: str = "latex"
) -> Dict[str, Any]:
    raw_expression = ocr_model.extract_text(image_path)

    return process_raw_expression_pipeline(raw_expression, format)


class LatexBody(TypedDict, total=False):
    latex: str
    format: str


app = Flask(__name__)

ocr_model = TrOCRModel()
nlp_corrector = NLPCorrector()
lexical_analyzer = LexicalAnalyzer()


# Test expression: (\sqrt{57-2})^{7}
@app.route("/solve-expression", methods=["POST"])
def solve_expression():
    """
    API endpoint to solve handwritten arithmetic expressions from images.

    Expects multipart/form-data with an image file under key 'image'.

    Returns:
        JSON response with solution details or error message
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided", "status": "error"}), 400

        image_file = request.files["image"]

        if image_file.filename == "":
            return jsonify({"error": "No selected file", "status": "error"}), 400

        temp_dir = tempfile.gettempdir()
        temp_filename = f"math_expr_{uuid.uuid4().hex}.png"
        temp_path = os.path.join(temp_dir, temp_filename)

        try:
            image_file.save(temp_path)
            format = request.form.get("format", "latex")
            result = process_expression_pipeline(temp_path, format)

            return jsonify(result), 200

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return (
            jsonify({"error": f"Erro de processamento: {str(e)}", "status": "error"}),
            500,
        )


@app.route("/solve-latex", methods=["POST"])
def solve_latex():
    try:
        data: LatexBody = request.get_json()
        format = data.get("format", "latex")
        result = process_latex_pipeline(data["latex"], format)

        return jsonify(result), 200
    except Exception as e:
        return (
            jsonify({"error": f"Erro de processamento: {str(e)}", "status": "error"}),
            400,
        )


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "status": "error"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed", "status": "error"}), 405


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return (
        jsonify(
            {"status": "healthy", "message": "Math Expression Solver API is running"}
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
