from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

from ocr import OCRModel


class TrOCRModel(OCRModel):

    def extract_text(self, image_path: str):
        image = Image.open(image_path).convert("RGB")
        processor = TrOCRProcessor.from_pretrained("fhswf/TrOCR_Math_handwritten")
        model = VisionEncoderDecoderModel.from_pretrained(
            "fhswf/TrOCR_Math_handwritten"
        )

        pixel_values = processor(images=image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        print(f"Generated text: ", generated_text)

        return generated_text
