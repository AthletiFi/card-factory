#!/bin/bash

print_welcome_message() {
    cat << EOF
╔═══════════════════════════════════════════════════════════════════════╗
║           Welcome to AthletiFi Card Cropper and Converter!            ║
╚═══════════════════════════════════════════════════════════════════════╝

This script will take your PNG cards, trim the excess transparent 
space, optionally resize them, and convert them to shiny new WebP format!

Remember:
 - PNG files go in, WebP files come out!
 - Transparent space disappears like a midfielder's energy in extra time!
 - Resize your cards faster than a striker's sprint to the goal!

Let's turn those cards into digital gold! Are you ready to play?

EOF
}

sanitize_path() {
    local input_path="$1"
    # Remove both single and double quotes
    local sanitized="${input_path//[\'\"]/}"
    # Replace backslashes with forward slashes
    sanitized="${sanitized//\\//}"
    # Trim leading and trailing whitespace
    sanitized="$(echo -e "${sanitized}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    
    if [ -d "$sanitized" ]; then
        echo "$sanitized"
    else
        echo "Directory not found: $sanitized" >&2
        echo "Please check if the path exists and try again." >&2
        return 1
    fi
}

print_welcome_message

read -p "Enter the path to the folder containing PNG files: " input_folder
input_folder=$(sanitize_path "$input_folder") || exit 1

read -p "Enter the path to save the WebP files: " output_folder
output_folder=$(sanitize_path "$output_folder") || exit 1

read -p "Enter the resize percentage (100 for no resizing, or any other number to resize): " resize_percentage

if ! [[ "$resize_percentage" =~ ^[0-9]+$ ]] ; then
   echo "Error: Resize percentage must be a positive integer" >&2
   exit 1
fi

mkdir -p "$output_folder"

find "$input_folder" -type f -name "*.png" | while read -r file; do
    filename=$(basename "$file" .png)
    bbox=$(identify -format "%@" "$file")
    
    cwebp_cmd="cwebp -lossless"
    
    if [[ ! -z "$bbox" && "$bbox" =~ ^[0-9]+x[0-9]+\+[0-9]+\+[0-9]+$ ]]; then
        width=$(echo $bbox | cut -d'x' -f1)
        height=$(echo $bbox | cut -d'x' -f2 | cut -d'+' -f1)
        x_offset=$(echo $bbox | cut -d'+' -f2)
        y_offset=$(echo $bbox | cut -d'+' -f3)
        cwebp_cmd+=" -crop $x_offset $y_offset $width $height"
    fi
    
    if [ "$resize_percentage" -ne 100 ]; then
        new_width=$((width * resize_percentage / 100))
        new_height=$((height * resize_percentage / 100))
        cwebp_cmd+=" -resize $new_width $new_height"
    fi
    
    $cwebp_cmd "$file" -o "${output_folder}/${filename}.webp"
    
    echo "Processed: $filename"
done

echo "Conversion, cropping, and resizing complete! Your cards are now as sleek as a well-executed slide tackle!"