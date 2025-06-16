import fitz
import json
import random
import argparse
import textwrap
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


def processImagePlacement(doc, img, path=None, verbose=False):
    if path is None:
        path = img["path"]

    if verbose:
        print(f"Image {path} at ({img['x']}, {img['y']}) scale {img['size']}")
    if isfile(path):
        if img["page"] == "all":
            doc = addImageOnEachPage(doc, path, img["x"], img["y"], img["size"])
            if verbose:
                print("Added on all pages")
        else:
            doc = addImageOnPage(
                doc, path, img["page"], img["x"], img["y"], img["size"]
            )
            if verbose:
                print(f"Added on the page {img['page']}")
    else:
        print(f"\033[33mWARNING:\033[0m Image {path} does not exist!")

    return doc


def placeRegularImages(doc, images_data, verbose=False):
    for img in images_data["images"]:
        processImagePlacement(doc, img, verbose=verbose)

    return doc


def placeDisposableOrRandomImage(doc, images_data, disposable=False, verbose=False):
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
            processImagePlacement(
                doc, images_collection, random_image_path, verbose=verbose
            )
            if disposable:
                rename(
                    random_image_path,
                    join(images_collection["disposed_path"], random_image),
                )

    return doc


def cropPage(doc, args):
    if len(args) in (3, 5):
        print(args)
    else:
        raise argparse.ArgumentTypeError("Must provide either 3 or 5 values.")
    page_num = args[0]
    w = args[1]
    h = args[2]
    if len(args) == 5:
        x = args[3]
        y = args[4]
    else:
        x = y = 0
    page = doc[page_num]
    page_width = page.rect.width
    page_height = page.rect.height
    if (w + x > page_width) or (h + y > page_height):
        raise ValueError(
            f"\033[33mWARNING:\033[0m Provided page sizes for cropping are beyond sizes of the original page №{page_num}!\n"
            f"\033[33mWARNING:\033[0m Original page №{page_num} has width={page_width} and height={page_height}"
        )
        print()
        return False
    page.set_cropbox(fitz.Rect(x, y, x + w, y + h))
    return doc


def parse_args():
    parser = argparse.ArgumentParser(
        description="Place images on PDF pages",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--pdf",
        default="input.pdf",
        help="Input PDF file path (default: input.pdf)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output.pdf",
        help="Output PDF file path (default: output.pdf)",
    )
    parser.add_argument(
        "-c",
        "--json",
        default="images.json",
        help="JSON config file path (default: images.json)",
    )
    parser.add_argument(
        "--skip-regular", action="store_true", help="Skip placing regular images"
    )
    parser.add_argument(
        "--skip-random", action="store_true", help="Skip placing random images"
    )
    parser.add_argument(
        "--skip-disposable", action="store_true", help="Skip placing disposable images"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--crop",
        nargs="+",
        type=int,
        help=textwrap.dedent(
            """\
        Crop page.
        Usage: --crop 2[page] 200[crop width] 400[crop height] 20[hor. starting point(def: 0)] 20[ver. starting point(def: 0)]
        """
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()

    doc = fitz.open(args.pdf)

    if args.crop:
        cropPage(doc, args.crop)

    json_data = readJson(args.json)

    createDirs(json_data)

    if not args.skip_regular:
        doc = placeRegularImages(doc, json_data, verbose=args.verbose)
    if not args.skip_random:
        doc = placeDisposableOrRandomImage(doc, json_data, verbose=args.verbose)
    if not args.skip_disposable:
        doc = placeDisposableOrRandomImage(doc, json_data, True, verbose=args.verbose)

    doc.save(args.output)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
