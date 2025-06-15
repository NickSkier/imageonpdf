import fitz
import os.path
import json


def readJson(json_path):
    with open(json_path) as f:
        json_data = json.load(f)
    return json_data


def createDirs(images_data):
    if "images" in images_data:
        first_image = images_data["images"][0]
        first_image_path = first_image["path"]
        images_dir = first_image_path[: first_image_path.find("/") + 1]
        try:
            os.makedirs(images_dir, exist_ok=True)
        except OSError as error:
            print(f"Directory {images_dir} for images can not be created")
            print(f"Error: {error}")

    if "random_images" in images_data:
        rand_img = images_data["random_images"]
        try:
            os.makedirs(rand_img["path"], exist_ok=True)
        except OSError as error:
            print(f"Directory {rand_img['path']} for random images can not be created")
            print(f"Error: {error}")

    if "disposable_random_images" in images_data:
        dispos_rand_img = images_data["disposable_random_images"]
        try:
            os.makedirs(dispos_rand_img["path"], exist_ok=True)
        except OSError as error:
            print(
                f"Directory {dispos_rand_img['path']} for disposable random images can not be created"
            )
            print(f"Error: {error}")
        try:
            os.makedirs(dispos_rand_img["disposed_path"], exist_ok=True)
        except OSError as error:
            print(
                f"Directory {dispos_rand_img['disposed_path']} for disposed random images can not be created"
            )
            print(f"Error: {error}")


def addImage(doc, image, page_index=0, offset_x=0, offset_y=0, image_size_factor=1):
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
        doc = addImage(doc, image, page_index, offset_x, offset_y, image_size_factor)

    return doc


def addRegularImages(doc, images_data):
    for img in images_data["images"]:
        print(f"Image {img['path']} at ({img['x']}, {img['y']}) scale {img['size']}")
        if os.path.isfile(img["path"]):
            if img["page"] == "all":
                doc = addImageOnEachPage(
                    doc, img["path"], img["x"], img["y"], img["size"]
                )
                print("Added on all pages")
            else:
                doc = addImage(
                    doc, img["path"], img["page"], img["x"], img["y"], img["size"]
                )
                print(f"Added on the page {img['page']}")
        else:
            print("Does not exists")

    return doc


def main():
    doc = fitz.open("input.pdf")

    json_data = readJson("images.json")

    createDirs(json_data)

    doc = addRegularImages(doc, json_data)

    doc.save("output.pdf")


if __name__ == "__main__":
    main()
