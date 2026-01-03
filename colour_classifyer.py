source_folder = r"C:\Users\ellio\Pictures\Artwork for room\TrialCode\SourceFolder"
output_folder = r"C:\Users\ellio\Pictures\Artwork for room\TrialCode\OutputFolder"

#Counting images in source_folder
import os
image_count = 0
list_of_images = os.scandir(source_folder) #returns a list of files in directory
for each_image in list_of_images:
    if each_image.is_file():
        image_count += 1
print(f"{image_count} images detected")    



""" 

count images in source_folder 

determine user requirements()
determine opposite_colour()

for images in root_directory_count
    resize_image()
    if average_colour_of_image() == opposite_colour
        next image
    if classify_image() = TRUE
        save images in output_folder



FUNCTION to determine user requirements
    INPUT user_desired_colour (colours can be added in future)
    INPUT user_sensitivity (threshold level for that colour)
    RETURN desired_colour, threshold

FUNCTION to determine 'opposite colour'
    PARSED(desired_colour)
    opposite_colour = user input colour, + 180, or similar logic
    RETURN opposite_colour

FUNCTION to resize image to shrink image to e.g. 300 x 300x pixels
    parsed(current_image)
    resizing constraints - e.g. 300 x 300
    resized_image = current_image * logic for resizing
    RETURN resized_image, size_of_image

FUNCTION to determine average colour of image 
    parsed(resized_image)
    look at pixels one by one
        store pixel value in a list?
    average_colour = average of list values 
    RETURN average_colour

FUNCTION to see if image fits users vibe
    parsed(desired_colour, threshold, resized_image, size_of_image)
    look at each pixel of image
        if pixel == desired colour
            count += 1
    if count / size_of_image >= threshold
        RETURN TRUE


 """