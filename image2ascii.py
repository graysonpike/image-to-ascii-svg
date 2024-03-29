from PIL import Image, ImageEnhance
import os
import matplotlib.pyplot as plt
import numpy as np
import svgwrite


def load_image(file_path: str) -> Image.Image:
    """
    Load an image from a specified file path and convert it to RGB.
    """
    with Image.open(file_path) as img:
        return img.convert('RGB')


def load_images_from_dir(directory: str) -> tuple[list[str], list[Image.Image]]:
    """
    Load all PNG and JPG images in a directory and return them in a list.
    """
    supported_formats = ('.png', '.jpg', '.jpeg')
    filenames: list[str] = []
    images: list[Image.Image] = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(supported_formats):
            file_path = os.path.join(directory, filename)
            image = load_image(file_path)
            filenames.append(filename)
            images.append(image)
    return filenames, images


def resize_image(image: Image.Image, max_size: int = 200) -> Image.Image:
    """
    Resize an image to fit within a max size bounding box, maintaining the original aspect ratio.
    """
    # Find which side is longest. This side will be scaled to max_size pixels and the other side
    # will be scaled proportionally, so that the original aspect ratio is maintained.
    width, height = image.size
    if width > height:
        scale_factor = max_size / width
    else:
        scale_factor = max_size / height
    new_size = (int(width * scale_factor), int(height * scale_factor))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def get_pixel_data(image: Image.Image) -> list[tuple[int, int, int]]:
    """
    Get the pixel data from an image, as a list of tuples (R,G,B).
    """
    return list(image.getdata())


def rgb_to_luminance(pixel_data: list[tuple[int, int, int]]) -> list[int]:
    """
    Convert a list of RGB pixel data to a list of luminance values.
    """
    luminance_values = [
        int(0.2126 * r + 0.7152 * g + 0.0722 * b)
        for r, g, b in pixel_data
    ]
    return luminance_values


def display_luminance_preview(luminance_values: list[int], dimensions: tuple[int, int]):
    """
    Display a preview of an image from its luminance values.
    """
    # Convert the list of luminance values back into a 2D array. Need to switch the dimensions because of how
    # numpy treats array dimensions.
    luminance_array = np.array(luminance_values).reshape((dimensions[1], dimensions[0]))
    plt.imshow(luminance_array, cmap='gray', interpolation='none')
    plt.axis('off')  # Hide axes for better visualization
    plt.show()


def save_svg_ascii_grid_from_luminance(luminance_data: list[int], dimensions: tuple[int, int], filename: str, bottom_text: list[str] = None, left_justified=True) -> str:
    """
    Save an SVG file with a grid of the letter "g" based on the dimensions of the provided image. Returns the saved filename.
    """
    density_str = "Ñ@#W$9876543210?!abc;:+=-,.   "
    width, height = dimensions
    scale_factor = 10  # Adjust this value to change the size of the SVG
    scaled_width = width * scale_factor
    scaled_height = height * scale_factor
    cell_size = max(scaled_width, scaled_height) // max(width, height)
    filename = os.path.join("output", f"{filename}.svg")
    dwg: svgwrite.Drawing = svgwrite.Drawing(
        filename,
        size=(scaled_width, scaled_height),
        profile='full'
    )
    # Set the background color to white
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill="black"))
    for y in range(height):
        for x in range(width):
            x_pos = x * cell_size + cell_size // 2
            y_pos = y * cell_size + cell_size // 2
            index = y * width + x
            density_str_index = int(luminance_data[index] / 255 * (len(density_str) - 1) + 0.5)
            density_str_index = len(density_str) - density_str_index - 1
            character = density_str[density_str_index]
            # If bottom text is provided, we may overwrite the normal character selection with the text character
            if bottom_text and left_justified:
                # Left justified bottom text
                bottom_text_index = (y - height) + len(bottom_text)
                if bottom_text_index >= 0 and x < len(bottom_text[bottom_text_index]):
                    character = bottom_text[bottom_text_index][x]
            elif bottom_text and not left_justified:
                # Right justified bottom text
                bottom_text_index = (y - height) + len(bottom_text)
                if bottom_text_index >= 0 and x >= width - len(bottom_text[bottom_text_index]):
                    character = bottom_text[bottom_text_index][x - (width - len(bottom_text[bottom_text_index]))]
            text = dwg.text(
                character,
                insert=(x_pos, y_pos),
                text_anchor="middle",
                dominant_baseline="middle",
                font_size=cell_size,
                font_family="Courier, monospace",
                fill="white"
            )
            dwg.add(text)
    dwg.save()
    return filename


def main():
    # Read files from the input dir.
    directory = "input/"
    filenames, original_images = load_images_from_dir(directory)
    # Resize the images to be manageable for ascii art.
    resized_images = [resize_image(image) for image in original_images]
    # Can adjust contrast for better effect.
    contrasted_images = []
    for image in resized_images:
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(1.5)
        contrasted_images.append(enhanced_image)
    # Convert images to RGB pixel data lists [[R, G, B, R, G, B, ...]..]
    rgb_data = [get_pixel_data(image) for image in contrasted_images]
    # Convert RBG data lists to Luminance data lists [[L, L, ...]..]
    luminance_data = [rgb_to_luminance(rgb) for rgb in rgb_data]
    # Uncomment this to see a preview window with the luminance values plotted to gray squares
    # display_luminance_preview(luminance_data[0], resized_images[0].size)
    # Save luminance lists to ASCII SVGs
    for i in range(len(luminance_data)):
        bottom_text = [
            "Artwork Title",
            "Grayson Pike, 2024"
        ]
        filename = save_svg_ascii_grid_from_luminance(
            luminance_data[i],
            contrasted_images[i].size,
            filenames[i].split(".")[0],  # Remove file extension
            bottom_text,
            left_justified=True
        )
        print(f"Saved file: {filename}")


if __name__ == "__main__":
    main()
