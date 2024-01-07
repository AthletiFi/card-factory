from PIL import Image
import os
import itertools
import functools

def sanitize_path(input_path):
    """ Sanitize the file path by handling both paths with escaped spaces and quoted paths. """
    # First, strip any leading and trailing quotes
    sanitized = input_path.strip('\'"')

    # Then, replace backslash-space combinations with a space
    sanitized = sanitized.replace("\\ ", " ").strip()

    print(f"final path = {sanitized}")

    # Check if the path exists
    if os.path.exists(sanitized):
        return sanitized
    else:
        raise FileNotFoundError(f"Sanitized path is not a valid file or directory: {sanitized}")

# Function to load images from a given directory or a single image file
def load_variations(path, replicate_to_match=None):
    """ Load images from a given directory or a single image file.
        If replicate_to_match is provided, replicate the image to match the number of images in another layer. """
    print(f"Processing path: {path}")
    path = sanitize_path(path)  # Sanitize the input path
    images, filenames = [], []

    if os.path.isfile(path):
        print("Path is a file. Loading image...")
        try:
            with Image.open(path) as image:
                images = [image.copy()] * (replicate_to_match if replicate_to_match else 1)
                filenames = [os.path.basename(path)] * (replicate_to_match if replicate_to_match else 1)
        except IOError as e:
            print(f"Error opening image file: {e}")
            raise IOError(f"Could not open image file: {path}")

    elif os.path.isdir(path):
        print("Path is a directory. Loading images from directory...")
        files = os.listdir(path)
        print(f"Found {len(files)} files. Filtering image files...")
        image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        print(f"Found {len(image_files)} image files.")

        for file in image_files:
            try:
                with Image.open(os.path.join(path, file)) as img:
                    images.append(img.copy())
                    filenames.append(file)
                    print(f"Loaded image: {file}")
            except IOError as e:
                print(f"Error opening image file: {file}, Error: {e}")

    else:
        print("Path is not valid.")
        raise FileNotFoundError(f"Path is not a valid file or directory: {path}")

    return images, filenames

def enhance_opacity(image, factor=1.2):
    """ Enhance the opacity of an image. """
    if image.mode == 'RGBA':
        r, g, b, alpha = image.split()
        alpha = alpha.point(lambda p: p * factor)
        return Image.merge('RGBA', (r, g, b, alpha))
    return image

def merge_layers(layer1, filenames1, layer2, filenames2, output_dir):
    """ Merge two layers of images in a 1-for-1 fashion with concatenated filenames. """
    for i, (image1, image2) in enumerate(zip(layer1, layer2)):
        merged_image = image1.copy()
        merged_image.paste(image2, (0, 0), image2)

        # Remove the file extension from each filename and concatenate them
        filename1 = os.path.splitext(filenames1[i])[0]
        filename2 = os.path.splitext(filenames2[i])[0]
        # output_filename = f"{filename1}_{filename2}_{i+1}.png"
        output_filename = f"{filename1}_-_{filename2}.png"

        merged_image.save(os.path.join(output_dir, output_filename))
        print(f'Merged image {i + 1} saved as {output_filename}.')



numLayers = input("Enter the number of layers: ")
outputInput = sanitize_path(input("Where do you want the images to output: "))
layerPaths = [sanitize_path(input(f'Enter the folder (or file) path for layer {i + 1}: ')) for i in range(int(numLayers))]
num_images_in_layers = [len(os.listdir(path)) if os.path.isdir(path) else 1 for path in layerPaths]

layersPath, all_filenames = [], []
for i, path in enumerate(layerPaths):
    print(f"Working on Layer {i + 1}...")
    replicate_count = None if not os.path.isfile(path) or i == len(layerPaths) - 1 else num_images_in_layers[i + 1]
    images, filenames = load_variations(path, replicate_count)
    layersPath.append(images)
    all_filenames.append(filenames)
    if i == 1:
        enhance_layer = input("Do you want to enhance the opacity of images in Layer 2? (yes/no): ").lower()
        if enhance_layer == 'yes':
            layersPath[i] = [enhance_opacity(img, factor=1.2) for img in images]

def generate_combinations(layers, filenames, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    layer_lengths = [len(layer) for layer in layers]
    total_combinations = functools.reduce(lambda x, y: x * y, layer_lengths)
    print("\nCalculating total combinations...")
    print("Total combinations = " + ' x '.join([str(length) for length in layer_lengths]))
    print(f"Total combinations to generate: {total_combinations}")

    count = 1
    for combination in itertools.product(*layers):
        combined_filenames = [
            os.path.splitext(filenames[layer_index][img_index])[0]  # Remove the file extension
            for layer_index, img_index in enumerate(
                [layers[layer_index].index(img) for layer_index, img in enumerate(combination)]
            )
        ]
        new_image = combination[0].copy()
        for overlay in combination[1:]:
            new_image.paste(overlay, (0, 0), overlay)
        output_filename = "_".join(combined_filenames) + f"_{count}.png"
        new_image.save(os.path.join(output_dir, output_filename))
        print(f"Generating image {count} of {total_combinations}: {output_filename}")
        count += 1


merge_method = input("Enter 'MERGE' for a 1-for-1 merge of corresponding images or 'COMBINE' to generate all combinations: ").lower()
if merge_method == 'merge' and len(layersPath) == 2 and len(layersPath[0]) == len(layersPath[1]):
    merge_layers(layersPath[0], all_filenames[0], layersPath[1], all_filenames[1], outputInput)

elif merge_method == 'combine':
    generate_combinations(layersPath, all_filenames, outputInput)
else:
    print("Invalid option or mismatched layers for merging.")
