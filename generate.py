import instructor
import requests
from io import BytesIO
from openai import OpenAI
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from pydantic import BaseModel, Field
import json

CHARS_IN_CHAPTER = 10000
OUTPUT_CHAR_PER_PROMPT = 3000


class Outline(BaseModel):
    title: str = Field(..., description="Der Titel der Geschichte")
    chapter_outlines: list[str] = Field(..., description="Die Gliederung der Kapitel der Geschichte")
    short_summary: str = Field(..., description="Die Zusammenfassung der Geschichte")
    cover_image_prompt: str = Field(..., description="Aufforderung zur Erstellung des Titelbildes")


def story_outline(story, num_chapters, language_level):
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
             "The story should have " + str(num_chapters) + " chapters. The story should be about " + story + "" \
                                                                                                              "The story should be written for people learning german in " + language_level + " level."

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


class ChapterContent(BaseModel):
    title: str = Field(..., description="Der Titel des Kapitels")
    content: str = Field(..., description="Der Inhalt des Kapitels in html format")


class ChapterMisc(BaseModel):
    title: str = Field(..., description="Der Titel des Kapitels")
    chapter_image_prompt: str = Field(..., description="Aufforderung zur Erstellung des Kapitelbildes")
    hard_words: list[str] = Field(..., description="Die schwierigen Wörter des Kapitels und ihre Erläuterung.")


class Chapter(BaseModel):
    title: str = Field(..., description="Der Titel des Kapitels")
    chapter_image_prompt: str = Field(..., description="Aufforderung zur Erstellung des Kapitelbildes")
    hard_words: list[str] = Field(..., description="Die 15 schwierigsten Wörter des Kapitels und ihre Erläuterung.")
    content: str = Field(..., description="Der Inhalt des Kapitels in html format")


def write_chapter(content, level_of_language):
    chapter_text = ""
    prompt = (
                "Write a chapter in German based on the following outline: " + content + ". " +
                "The book you are writing is for people learning German at the " + level_of_language + " level. " +
                "Hence, you should use words and grammar so the reader understands and also that helps the reader " +
                "improve their german. The chapter " +
                "should be engaging and approximately " + str(CHARS_IN_CHAPTER) + " characters long in total, " +
                "suitable for a Include a mix of dialogue, description, and action to bring the story to life. The " +
                "hard, challenging or advanced words should be highlighted in the chapter by using the following " +
                "format: <b>hard word</b>.")

        # Now, you only need to write " + str(
        #     OUTPUT_CHAR_PER_PROMPT) + " characters for now.")
        #
        # if len(chapter_text) == 0:
        #     prompt += "You don't need to finish the chapter in one go. We will finish it later."
        # elif len(chapter_text) < CHARS_IN_CHAPTER + OUTPUT_CHAR_PER_PROMPT:
        #     prompt += (
        #             "So far you have written this, please continue the story: " + chapter_text + "." +
        #             "You don't need to finish the chapter in one go. We will finish it later."
        #     )
        # else:
        #     prompt += (
        #             "So far you have written this, please continue the story: " + chapter_text + "." +
        #             "Please write an ending to the story."
        #     )

        # Sending request to OpenAI GPT-4
    client = instructor.patch(OpenAI())
    chapter_content: ChapterContent = client.chat.completions.create(
            model="gpt-4",
            response_model=ChapterContent,
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_retries=2,
        )

    chapter_text += chapter_content.content

    # Sending request to OpenAI GPT-4
    last_prompt = ("Create a title of a chapter in a book. Additionally, you should provide a detailed " +
                   "description for an image prompt that captures the essence of the chapter. This description " +
                   "will be used to create the cover art of the chapter. Additionally, all words in bold (<b>hard word</b>) should " +
                   "be explained hard_words list. Lastly there should also be a summary of the chapter. The text " +
                   "is as follows: " + chapter_text)
    client = instructor.patch(OpenAI())
    chapter_misc: ChapterMisc = client.chat.completions.create(
        model="gpt-4",
        response_model=ChapterMisc,
        messages=[
            {"role": "user", "content": last_prompt},
        ],
        max_retries=2,
    )

    chapter = Chapter(title=chapter_misc.title, chapter_image_prompt=chapter_misc.chapter_image_prompt,
                      hard_words=chapter_misc.hard_words, content=chapter_text)

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
