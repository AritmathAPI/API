#!/usr/bin/env python3
"""
Test script for the complete arithmetic expression processing pipeline.
"""

import os
import tempfile
from ocr import MockOCRModel
from nlp import NLPCorrector
from tokenizer import LexicalAnalyzer
from parser import SyntacticAnalyzer
from formatter import FormatConverter


def test_ocr_module():
    """Test the OCR module with mock implementation."""
    print("=== Testing OCR Module ===")
    ocr = MockOCRModel()

    # Test different filename patterns
    test_cases = [
        "test1.png",
        "test2.jpg",
        "test3.png",
        "test4.jpg",
        "test5.png",
        "unknown_file.png",
    ]

    for filename in test_cases:
        result = ocr.extract_text(filename)
        print(f"File: {filename} -> OCR Result: '{result}'")

    print()


def test_nlp_corrector():
    """Test the NLP corrector module."""
    print("=== Testing NLP Corrector Module ===")
    nlp = NLPCorrector()

    test_cases = [
        "12 + (5 x 4) - I",  # Common OCR errors
        "3,14 * 2 + 7 / 2",  # Proper expression
        "8 - 4 / 2 + 1",  # Division before subtraction
        "(10 + 2) * 3 - 5",  # Parentheses
        "2 O + 3 l - S",  # Character confusion
        "1 2 + ( 5 x 4 ) - I",  # Extra spaces
        "1 2 + (() 5 ++ 4 )) - I",  # Extra spaces
    ]

    for expr in test_cases:
        try:
            corrected = nlp.correct_expression(expr)
            print(f"Input: '{expr}' -> Corrected: '{corrected}'")
        except Exception as e:
            print(f"Input: '{expr}' -> Error: {e}")

    print()


def test_tokenizer():
    """Test the lexical analyzer."""
    print("=== Testing Lexical Analyzer ===")
    tokenizer = LexicalAnalyzer()

    test_cases = ["12+(5*4)-1", "3.14*2+7/2", "8-4/2+1", "(10+2)*3-5", "2+3*4"]

    for expr in test_cases:
        try:
            tokens = tokenizer.tokenize(expr)
            print(f"Expression: '{expr}'")
            print(f"Tokens: {tokens}")
            print(f"Valid: {tokenizer.validate_tokens(tokens)}")
        except Exception as e:
            print(f"Expression: '{expr}' -> Error: {e}")

    print()


def test_parser():
    """Test the syntactic analyzer and evaluation."""
    print("=== Testing Syntactic Analyzer ===")

    test_cases = [
        "12+(5*4)-1",  # Should be 31.0
        "3.14*2+7/2",  # Should be 11.28
        "8-4/2+1",  # Should be 7.0
        "(10+2)*3-5",  # Should be 31.0
        "2+3*4",  # Should be 14.0
    ]

    for expr in test_cases:
        try:
            tokenizer = LexicalAnalyzer()
            tokens = tokenizer.tokenize(expr)

            parser = SyntacticAnalyzer(tokens)
            result = parser.evaluate()
            steps = parser.solve_by_substitution()

            print(f"Expression: {expr}")
            print(f"Result: {result}")
            print("Steps:")
            for i, step in enumerate(steps, 1):
                print(f"  {i}. {step}")
            print()

        except Exception as e:
            print(f"Expression: '{expr}' -> Error: {e}")
            print()


def test_formatter():
    """Test the format converter."""
    print("=== Testing Format Converter ===")

    test_cases = ["12+(5*4)-1", "3.14*2+7/2", "(10+2)*3-5"]

    for expr in test_cases:
        latex = FormatConverter.to_latex(expr)
        mathml = FormatConverter.to_mathml(expr)
        readable = FormatConverter.expression_to_readable(expr)

        print(f"Expression: {expr}")
        print(f"Readable: {readable}")
        print(f"LaTeX: {latex}")
        print(f"MathML: {mathml}")
        print()


def test_complete_pipeline():
    """Test the complete pipeline from OCR to solution."""
    print("=== Testing Complete Pipeline ===")

    # Create a mock OCR that simulates different scenarios
    ocr = MockOCRModel()
    nlp = NLPCorrector()
    tokenizer = LexicalAnalyzer()

    test_files = [
        "test1.png",  # "12 + (5 x 4) - I"
        "test2.jpg",  # "3.14 * 2 + 7 / 2"
        "test3.png",  # "8 - 4 / 2 + 1"
    ]

    for filename in test_files:
        print(f"\nProcessing file: {filename}")
        print("-" * 40)

        try:
            # Step 1: OCR
            raw_text = ocr.extract_text(filename)
            print(f"1. OCR Raw: '{raw_text}'")

            # Step 2: NLP Correction
            corrected = nlp.correct_expression(raw_text)
            print(f"2. NLP Corrected: '{corrected}'")

            # Step 3: Tokenization
            tokens = tokenizer.tokenize(corrected)
            print(f"3. Tokens: {tokens}")

            # Step 4: Parsing and Evaluation
            parser = SyntacticAnalyzer(tokens)
            result = parser.evaluate()
            steps = parser.solve_by_substitution()

            print(f"4. Final Result: {result}")
            print("5. Step-by-step solution:")
            for i, step in enumerate(steps, 1):
                print(f"   {i}. {step}")

            # Step 5: Format Conversion
            latex = FormatConverter.to_latex(corrected)
            mathml = FormatConverter.to_mathml(corrected)
            print(f"6. LaTeX: {latex}")
            print(f"7. MathML: {mathml}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue


def main():
    """Run all tests."""
    print("Arithmetic Expression Processing Pipeline Test")
    print("=" * 50)
    print()

    try:
        test_ocr_module()
        test_nlp_corrector()
        test_tokenizer()
        test_parser()
        test_formatter()
        test_complete_pipeline()

        print("All tests completed successfully!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
