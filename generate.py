import instructor
import requests
from io import BytesIO
from openai import OpenAI
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from pydantic import BaseModel, Field
import json

WORDS_IN_CHAPTER = 3000


class Outline(BaseModel):
    title: str = Field(..., description="Der Titel der Geschichte")
    chapter_outlines: list[str] = Field(..., description="Die Gliederung der Kapitel der Geschichte")
    short_summary: str = Field(..., description="Die Zusammenfassung der Geschichte")
    cover_image_prompt: str = Field(..., description="Aufforderung zur Erstellung des Titelbildes")


def calc_num_chapters(words):
    return words // WORDS_IN_CHAPTER


def story_outline(story, num_words, language_level):
    num_chapters = calc_num_chapters(num_words)
    words_per_chapter = num_words // num_chapters

    prompt = "Please create a novel story outline in German using the 'Outline' class structure. The story should " \
             "be captivating and suitable for a broad audience. The story should be played over one or two days." \
             "Make sure to include:" \
             "Title ('title'): Create an intriguing and memorable title for the story in German. The titel should " \
             "not be more than 30 characters." \
             "Chapter Outlines ('chapter_outlines'): List the chapter titles in German, briefly describing the key " \
             "events or themes of each chapter." \
             "Short Summary ('short_summary'): Write a concise summary of the story in German, highlighting the " \
             "main plot, characters, and the overall theme. " \
             "Cover Image Prompt ('cover_image_prompt'): Provide a detailed description for an image prompt that " \
             "captures the essence of the story. This description will be used to create the cover art of the book." \
             "The story should have " + str(num_chapters) + " chapters. Each chapter should be approximately " + \
             str(words_per_chapter) + " words long. The story should be about " + story + ". The story should be " \
             "written for people learning german in " + language_level + " level."

    # Sending request to OpenAI GPT-4
    client = instructor.patch(OpenAI())
    outline: Outline = client.chat.completions.create(
        model="gpt-4",
        response_model=Outline,
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_retries=2,
    )

    return outline


class Chapter(BaseModel):
    title: str = Field(..., description="Der Titel des Kapitels")
    content: str = Field(..., description="Der Inhalt des Kapitels in html format")
    chapter_image_prompt: str = Field(..., description="Aufforderung zur Erstellung des Kapitelbildes")
    hard_words: list[str] = Field(..., description="Die schwierigen Wörter des Kapitels und ihre Erläuterung.")


def write_chapter(content, level_of_language):
    prompt = (
            "Write a chapter in German based on the following outline: " + content + ". " +
            "The chapter should be engaging and approximately " + str(WORDS_IN_CHAPTER) + " words long, suitable for a "
            "language level of " + level_of_language + ". " + "Include a mix of dialogue, description, and action to "
            "bring the story to life. " + "Also, provide a detailed image prompt for this chapter that captures a "
            "key moment or theme. Lastly, list any challenging or advanced German words used in the chapter and "
            "explain them to help readers expand their vocabulary. The hard challenging or advanced words should be "
            "highligthed in the chapter by using the following format: <b>hard word</b>.")

    # Sending request to OpenAI GPT-4
    client = instructor.patch(OpenAI())
    chapter: Chapter = client.chat.completions.create(
        model="gpt-4",
        response_model=Chapter,
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_retries=2,
    )

    return chapter


def create_image(image_prompt):
    image_prompt += " The image should be in black and white."
    client = instructor.patch(OpenAI())
    response = client.images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        size="1024x1792",
        quality="hd",
        n=1,
    )

    response = requests.get(response.data[0].url)
    image = PILImage.open(BytesIO(response.content))
    return image


def add_text(image: PILImage, text: str, font_path: str) -> PILImage:
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, 40)
    # Starting position for the text (bottom left)
    text_x = 10
    text_y = image.size[1] - 40 - 20 - 500  # Adjust based on font size and desired padding

    # Calculate the bounding box of the text
    bbox = draw.textbbox((text_x, text_y), text, font=font)

    rect_x0 = bbox[0]
    rect_y0 = bbox[1]
    rect_x1 = bbox[2]
    rect_y1 = bbox[3]

    padding = 10
    rect_x0 -= padding
    rect_y0 -= padding
    rect_x1 += padding
    rect_y1 += padding

    # Draw the white rectangle
    draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill="white")

    # Draw the text
    draw.text((text_x, text_y), text, fill="black", font=font)

    return image


# Function to save an instance to a file
def save_to_file(instance, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(instance.dict(), file, ensure_ascii=False, indent=4)


# Function to load an instance from a file
def load_from_file(cls, filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return cls(**data)
