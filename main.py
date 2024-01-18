import argparse
import generate
import book
from PIL import Image as PILImage

def main():
    parser = argparse.ArgumentParser(description='Create your own story using gpt-4!')
    parser.add_argument('plot', type=str, help='The content of the story')
    parser.add_argument('language_level', type=str, default="A1", help='The content of the story')
    parser.add_argument('length', type=int, default=3000, help='The content of the story')
    parser.add_argument('author', type=str, default="", help='Name of the author')
    parser.add_argument('outpath', type=str, default="./data", help='Name of the author')

    args = parser.parse_args()

    print("------------Generate Story Outline------------")
    story = generate.story_outline(args.plot, args.length, args.language_level)
    generate.save_to_file(story, args.outpath + "story.json")
    #story = generate.load_from_file(generate.Outline, args.outpath + "story.json")

    print("Title: " + story.title)
    print("Short Summary: " + story.short_summary)
    print("Number of chapters: " + str(len(story.chapter_outlines)))
    cover_image = generate.create_image(story.cover_image_prompt)
    cover_image = generate.add_text(cover_image, story.title, args.outpath + "SourceSansPro-Black.ttf")
    cover_image.save(args.outpath + "cover.png")
    #cover_image = PILImage.open(args.outpath + "cover.png")

    chapters = []
    chapter_images = []
    for idx, chapter_outline in enumerate(story.chapter_outlines):
        print(f"------------Generate Chapter {idx}------------")
        chapter = generate.write_chapter(chapter_outline, args.language_level)
        generate.save_to_file(chapter, args.outpath + f"chapter{idx}.json")
        #chapter = generate.load_from_file(generate.Chapter, args.outpath + f"chapter{idx}.json")
        chapters.append(chapter)

        print("Chapter Title: " + chapter.title)
        print("Content: " + chapter.content)
        print("Hard Words: " + str(chapter.hard_words))
        image = generate.create_image(chapter.chapter_image_prompt)
        image.save(args.outpath + f"{idx}.png")
        #image = PILImage.open(args.outpath + f"{idx}.png")
        chapter_images.append(image)

    print("------------Generate ePub------------")
    book.create_epub_book(story, chapters, cover_image, chapter_images, args.author, args.outpath)

if __name__ == "__main__":
    main()


