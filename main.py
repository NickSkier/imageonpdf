import fitz
import json
import random
from os import makedirs, listdir, rename
from os.path import isfile, join


def readJson(json_path):
    with open(json_path) as f:
        json_data = json.load(f)
    return json_data


def createDirs(images_data):
    images_dirs = list()
    successful = True
    for img_batch in (
        images_data["images"],
        images_data["random_images"],
        images_data["disposable_random_images"],
    ):
        for img_batch_data in img_batch:
            img_path = img_batch_data["path"]
            img_dir = img_path[: img_path.find("/") + 1]
            images_dirs.append(img_dir)

    unique_images_dirs = list(set(images_dirs))

    for img_dir in unique_images_dirs:
        try:
            makedirs(img_dir, exist_ok=True)
        except OSError as error:
            print(f"Directory {img_dir} can not be created")
            print(f"Error: {error}")
            successful = False

    return successful


def addImageOnPage(
    doc, image, page_index=0, offset_x=0, offset_y=0, image_size_factor=1
):
    pix = fitz.Pixmap(image)

    x_dpi = pix.xres or 72
    y_dpi = pix.yres or 72
    w_pt = pix.width * 72 / x_dpi * image_size_factor
    h_pt = pix.height * 72 / y_dpi * image_size_factor

    rect = fitz.Rect(offset_x, offset_y, offset_x + w_pt, offset_y + h_pt)

    page = doc[page_index]
    page.insert_image(rect, filename=image)

    return doc


def addImageOnEachPage(doc, image, offset_x=0, offset_y=0, image_size_factor=1):
    for page_index in range(len(doc)):
        doc = addImageOnPage(
            doc, image, page_index, offset_x, offset_y, image_size_factor
        )

    return doc


def processImagePlacement(doc, img, path=None):
    if path is None:
        path = img["path"]

    print(f"Image {path} at ({img['x']}, {img['y']}) scale {img['size']}")
    if isfile(path):
        if img["page"] == "all":
            doc = addImageOnEachPage(doc, path, img["x"], img["y"], img["size"])
            print("Added on all pages")
        else:
            doc = addImageOnPage(
                doc, path, img["page"], img["x"], img["y"], img["size"]
            )
            print(f"Added on the page {img['page']}")
    else:
        print("Does not exists")

    return doc


def placeRegularImages(doc, images_data):
    for img in images_data["images"]:
        processImagePlacement(doc, img)

    return doc


def placeDisposableOrRandomImage(doc, images_data, disposable=False):
    if disposable:
        images_type = images_data["disposable_random_images"]
    else:
        images_type = images_data["random_images"]

    for images_collection in images_type:
        images_names = [
            f
            for f in listdir(images_collection["path"])
            if isfile(join(images_collection["path"], f))
        ]
        if images_names:
            random_image = random.choice(images_names)
            random_image_path = join(images_collection["path"], random_image)
            processImagePlacement(doc, images_collection, random_image_path)
            if disposable:
                rename(
                    random_image_path,
                    join(images_collection["disposed_path"], random_image),
                )

    return doc


def main():
    doc = fitz.open("input.pdf")

    json_data = readJson("images.json")

    createDirs(json_data)

    doc = placeRegularImages(doc, json_data)
    doc = placeDisposableOrRandomImage(doc, json_data)
    doc = placeDisposableOrRandomImage(doc, json_data, True)

    doc.save("output.pdf")


if __name__ == "__main__":
    main()
