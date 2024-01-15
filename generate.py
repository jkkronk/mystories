import instructor
from openai import OpenAI
from IPython.display import Image
from pydantic import BaseModel, Field

class Outline(BaseModel):
    title: str = Field(..., description="Der Titel der Geschichte")
    chapter_outlines: list[str] = Field(..., description="Die Gliederung der Kapitel der Geschichte")
    short_summary: str = Field(..., description="Die Zusammenfassung der Geschichte")
    cover_image_prompt: str = Field(..., description="Aufforderung zur Erstellung des Titelbildes")


def calc_num_chapters(words):
    # 1000 words per chapter
    return words // 1000


def story_outline(story, num_words, language_level):
    num_chapters = calc_num_chapters(num_words)
    words_per_chapter = num_words // num_chapters

    prompt =    "Please create a novel story outline in German using the 'Outline' class structure. The story should " \
                "be captivating and suitable for a broad audience. Make sure to include:" \
                "Title ('title'): Create an intriguing and memorable title for the story in German. " \
                "Chapter Outlines ('chapter_outlines'): List the chapter titles in German, briefly describing the key" \
                " events or themes of each chapter." \
                "Short Summary ('short_summary'): Write a concise summary of the story in German, highlighting the " \
                "main plot, characters, and the overall theme. " \
                "Cover Image Prompt ('cover_image_prompt'): Provide a detailed description for an image prompt that " \
                "captures the essence of the story. This description will be used to create the cover art of the book."\
                "The story should have " + str(num_chapters) + " chapters. Each chapter should be approximately " + \
                str(words_per_chapter) + " words long. The story should be about " + story + ". The story should be " \
                "written for people learning german in " + language_level + " level." \


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
    content: str = Field(..., description="Der Inhalt des Kapitels")
    chapter_image_prompt: str = Field(..., description="Aufforderung zur Erstellung des Kapitelbildes")
    hard_words: list[str] = Field(..., description="Die schwierigen Wörter des Kapitels und ihre Erläuterung.")


def write_chapter(content, level_of_language):
    prompt = (
            "Write a chapter in German based on the following outline: '" + content + "'. " +
            "The chapter should be engaging and approximately 1000 words long, suitable for a language level of '" +
            level_of_language + "'. " + "Include a mix of dialogue, description, and action to bring the story to "
            "life. " + "Also, provide a detailed image prompt for this chapter that captures a key moment or theme. " +
            "Lastly, list any challenging or advanced German words used in the chapter to help readers expand their "
            "vocabulary. The hard challenging or advanced words should be highligthed in the chapter by using the "
            "following format: **hard word**.")

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
        size="640x400",
        quality="hd",
        n=1,
    )

    image_url = response.data[0].url

    return Image(url=image_url)