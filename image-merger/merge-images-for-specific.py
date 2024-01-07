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

def merge_layers(layer1, filenames1, layer2, filenames2, valid_filenames, output_dir):
    """ Merge two layers of images in a 1-for-1 fashion with concatenated filenames. """
    for i, (image1, image2) in enumerate(zip(layer1, layer2)):
        # Check if the filename of the layer 2 image is in the valid filenames list
        if filenames2[i] not in valid_filenames:
            print(f"Skipping merge for {filenames2[i]} as it's not in the valid list.")
            continue

        merged_image = image1.copy()
        merged_image.paste(image2, (0, 0), image2)

        # Remove the file extension from each filename and concatenate them
        filename1 = os.path.splitext(filenames1[i])[0]
        filename2 = os.path.splitext(filenames2[i])[0]
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

# valid_filenames_layer2 = ['qr_18.png', 'qr_32.png', 'qr_36.png', 'qr_43.png', 'qr_44.png', 'qr_46.png', 'qr_47.png', 'qr_51.png', 'qr_55.png', 'qr_76.png', 'qr_90.png', 'qr_114.png', 'qr_115.png', 'qr_121.png', 'qr_153.png', 'qr_165.png', 'qr_170.png', 'qr_180.png', 'qr_189.png', 'qr_190.png', 'qr_191.png', 'qr_198.png', 'qr_201.png', 'qr_209.png', 'qr_216.png', 'qr_217.png', 'qr_224.png', 'qr_233.png', 'qr_254.png', 'qr_259.png', 'qr_278.png', 'qr_281.png', 'qr_284.png', 'qr_286.png', 'qr_291.png', 'qr_293.png', 'qr_294.png', 'qr_300.png', 'qr_301.png', 'qr_302.png', 'qr_320.png', 'qr_344.png', 'qr_345.png', 'qr_359.png', 'qr_372.png', 'qr_384.png', 'qr_388.png', 'qr_394.png', 'qr_395.png', 'qr_397.png', 'qr_404.png', 'qr_425.png', 'qr_430.png', 'qr_448.png', 'qr_452.png', 'qr_453.png', 'qr_459.png', 'qr_468.png', 'qr_474.png', 'qr_479.png', 'qr_493.png', 'qr_501.png', 'qr_507.png', 'qr_508.png', 'qr_520.png', 'qr_527.png', 'qr_529.png', 'qr_534.png', 'qr_539.png', 'qr_545.png', 'qr_547.png', 'qr_550.png', 'qr_558.png', 'qr_581.png', 'qr_587.png', 'qr_598.png', 'qr_612.png', 'qr_617.png', 'qr_631.png', 'qr_648.png', 'qr_651.png', 'qr_652.png', 'qr_657.png', 'qr_661.png', 'qr_670.png', 'qr_679.png', 'qr_685.png', 'qr_688.png', 'qr_697.png', 'qr_698.png', 'qr_699.png', 'qr_700.png', 'qr_702.png', 'qr_708.png', 'qr_714.png', 'qr_715.png', 'qr_716.png', 'qr_718.png', 'qr_734.png', 'qr_735.png', 'qr_738.png', 'qr_739.png', 'qr_747.png', 'qr_754.png', 'qr_756.png', 'qr_761.png', 'qr_764.png', 'qr_768.png', 'qr_772.png', 'qr_774.png', 'qr_778.png', 'qr_782.png', 'qr_783.png', 'qr_785.png', 'qr_806.png', 'qr_812.png', 'qr_815.png', 'qr_820.png', 'qr_826.png', 'qr_829.png', 'qr_831.png', 'qr_833.png', 'qr_836.png', 'qr_837.png', 'qr_839.png', 'qr_842.png', 'qr_847.png', 'qr_855.png', 'qr_856.png', 'qr_860.png', 'qr_868.png', 'qr_880.png', 'qr_882.png', 'qr_912.png', 'qr_913.png', 'qr_924.png', 'qr_925.png', 'qr_931.png', 'qr_933.png', 'qr_936.png', 'qr_937.png', 'qr_942.png', 'qr_947.png', 'qr_959.png', 'qr_970.png', 'qr_973.png', 'qr_1010.png', 'qr_1024.png', 'qr_1025.png', 'qr_1026.png', 'qr_1036.png', 'qr_1059.png', 'qr_1062.png', 'qr_1069.png', 'qr_1070.png', 'qr_1082.png', 'qr_1116.png', 'qr_1118.png', 'qr_1121.png', 'qr_1122.png', 'qr_1123.png']
valid_filenames_layer2 = ['qr_18.png', 'qr_32.png', 'qr_36.png', 'qr_44.png', 'qr_46.png', 'qr_47.png', 'qr_51.png', 'qr_76.png', 'qr_90.png', 'qr_114.png', 'qr_115.png', 'qr_121.png', 'qr_165.png', 'qr_170.png', 'qr_189.png', 'qr_190.png', 'qr_191.png', 'qr_198.png', 'qr_201.png', 'qr_216.png', 'qr_217.png', 'qr_224.png', 'qr_233.png', 'qr_254.png', 'qr_259.png', 'qr_278.png', 'qr_281.png', 'qr_284.png', 'qr_286.png', 'qr_291.png', 'qr_293.png', 'qr_294.png', 'qr_300.png', 'qr_301.png', 'qr_302.png', 'qr_320.png', 'qr_344.png', 'qr_345.png', 'qr_359.png', 'qr_372.png', 'qr_384.png', 'qr_388.png', 'qr_404.png', 'qr_448.png', 'qr_452.png', 'qr_453.png', 'qr_459.png', 'qr_468.png', 'qr_474.png', 'qr_479.png', 'qr_493.png', 'qr_501.png', 'qr_507.png', 'qr_508.png', 'qr_520.png', 'qr_527.png', 'qr_529.png', 'qr_534.png', 'qr_539.png', 'qr_558.png', 'qr_581.png', 'qr_598.png', 'qr_612.png', 'qr_617.png', 'qr_648.png', 'qr_651.png', 'qr_652.png', 'qr_657.png', 'qr_661.png', 'qr_670.png', 'qr_679.png', 'qr_685.png', 'qr_688.png', 'qr_697.png', 'qr_698.png', 'qr_699.png', 'qr_700.png', 'qr_702.png', 'qr_708.png', 'qr_714.png', 'qr_715.png', 'qr_716.png', 'qr_718.png', 'qr_734.png', 'qr_735.png', 'qr_738.png', 'qr_739.png', 'qr_754.png', 'qr_756.png', 'qr_761.png', 'qr_764.png', 'qr_768.png', 'qr_772.png', 'qr_774.png', 'qr_782.png', 'qr_783.png', 'qr_806.png', 'qr_812.png', 'qr_820.png', 'qr_826.png', 'qr_831.png', 'qr_833.png', 'qr_836.png', 'qr_837.png', 'qr_839.png', 'qr_842.png', 'qr_847.png', 'qr_855.png', 'qr_856.png', 'qr_860.png', 'qr_868.png', 'qr_880.png', 'qr_882.png', 'qr_912.png', 'qr_913.png', 'qr_924.png', 'qr_925.png', 'qr_931.png', 'qr_933.png', 'qr_936.png', 'qr_937.png', 'qr_942.png', 'qr_947.png', 'qr_959.png', 'qr_970.png', 'qr_973.png', 'qr_1010.png', 'qr_1024.png', 'qr_1025.png', 'qr_1026.png', 'qr_1036.png', 'qr_1059.png', 'qr_1069.png', 'qr_1070.png', 'qr_1082.png', 'qr_1118.png', 'qr_1121.png', 'qr_1122.png', 'qr_1123.png']

merge_method = input("Enter 'MERGE' for a 1-for-1 merge of corresponding images or 'COMBINE' to generate all combinations: ").lower()
if merge_method == 'merge' and len(layersPath) == 2 and len(layersPath[0]) == len(layersPath[1]):
    merge_layers(layersPath[0], all_filenames[0], layersPath[1], all_filenames[1], valid_filenames_layer2, outputInput)

elif merge_method == 'combine':
    generate_combinations(layersPath, all_filenames, outputInput)
else:
    print("Invalid option or mismatched layers for merging.")
