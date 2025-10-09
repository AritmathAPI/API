from flask import Flask, request, jsonify
import os
import tempfile
import uuid
from typing import Dict, Any

from ocr import MockOCRModel
from nlp import NLPCorrector
from tokenizer import LexicalAnalyzer
from parser import SyntacticAnalyzer
from formatter import FormatConverter

app = Flask(__name__)

ocr_model = MockOCRModel()
nlp_corrector = NLPCorrector()
lexical_analyzer = LexicalAnalyzer()


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

            result = process_expression_pipeline(temp_path)

            return jsonify(result), 200

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}", "status": "error"}), 500


def process_expression_pipeline(image_path: str) -> Dict[str, Any]:
    """
    Process an image through the complete expression solving pipeline.

    Args:
        image_path (str): Path to the image file

    Returns:
        Dict[str, Any]: Complete solution with all processing steps
    """
    raw_expression = ocr_model.extract_text(image_path)

    try:
        corrected_expression = nlp_corrector.correct_expression(raw_expression)
    except Exception as e:
        raise ValueError(f"NLP correction failed: {e}")

    try:
        tokens = lexical_analyzer.tokenize(corrected_expression)

        if not lexical_analyzer.validate_tokens(tokens):
            raise ValueError("Invalid token sequence in expression")

    except Exception as e:
        raise ValueError(f"Lexical analysis failed: {e}")

    try:
        parser = SyntacticAnalyzer(tokens)

        ast_root = parser.parse()

        final_result = parser.evaluate(ast_root)

        steps = parser.solve_step_by_step(ast_root)

        normalized_expression = parser.to_string(ast_root)

    except Exception as e:
        raise ValueError(f"Syntactic analysis failed: {e}")

    try:
        latex_output = FormatConverter.to_latex(normalized_expression)
        mathml_output = FormatConverter.to_mathml(normalized_expression)

        formatted_steps = [FormatConverter.format_step(step) for step in steps]

    except Exception as e:
        raise ValueError(f"Format conversion failed: {e}")

    return {
        "input_expression_raw": raw_expression,
        "expression_corrected": normalized_expression,
        "solution": {"steps": formatted_steps, "final_result": final_result},
        "export_formats": {"latex": latex_output, "mathml": mathml_output},
        "status": "success",
    }


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
