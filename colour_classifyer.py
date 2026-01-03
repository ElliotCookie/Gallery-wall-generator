import os
from colorist import bg_hsl
from PIL import Image, ImageColor
import colorsys
Image.MAX_IMAGE_PIXELS = None  # Disable decompression bomb check

source_folder = r"C:\Users\ellio\Pictures\Artwork for room\TrialCode\SourceFolder"
output_folder = r"C:\Users\ellio\Pictures\Artwork for room\TrialCode\OutputFolder"

def count_images_in_folder():
    image_count = 0
    list_of_image_paths = []  # Changed to a list to store paths
    for each_image in os.scandir(source_folder):  # Re-scan here
        if each_image.is_file():
            list_of_image_paths.append(each_image.path)  # Store the path
            image_count += 1
    print(f"{image_count} images detected")    
    return(list_of_image_paths)

def user_requirements():
    desired_hue = int(input("Enter the hue you'd like: "))
    desired_saturation = int(input("Enter the saturation you'd like: "))
    desired_lightness = int(input("Enter the desired lightness you'd like: "))
    bg_hsl("Colour confirmed", desired_hue, desired_saturation, desired_lightness)
    
    desired_scope = input("On a scale of 0-100 (most accurate), how close do you want the match? ")
    desired_intensity = input("Enter how much of that colour you want in the image ")
    
    print(f"Noted, you want a range of {desired_scope} at strength of {desired_intensity}")
    return desired_hue, desired_saturation, desired_lightness, desired_scope, desired_intensity

def calc_opposite_colour(desired_hue, desired_saturation, desired_lightness):
    
    opp_hue = desired_hue + 180
    if opp_hue > 360:
        opp_hue = opp_hue - 360

    if desired_saturation > 50:
        opp_sat = 100 - desired_saturation
    elif desired_saturation < 50:
        opp_sat = 50 + desired_saturation

    if desired_lightness > 50:
        opp_light = 100 - desired_lightness
    elif desired_lightness < 50:
        opp_light = 50 + desired_lightness
    
    return opp_hue, opp_sat, opp_light

def resized_image(image_file):
    current_image = Image.open(image_file)  # Now receives a string path
    #print(f"File size detected as {current_image.size}")
    new_max = 300
    new_thumbnail = current_image.copy()
    new_thumbnail.thumbnail((new_max, new_max))
    new_size = new_thumbnail.size
    #new_thumbnail.show() <- VERY IMPORTANT TO NOT TURN THIS ON
    #print(f"Temporarily resized to {new_size}")
    return new_thumbnail, new_size

def average_colour(image_file, size):
    r_tot = 0
    g_tot = 0
    b_tot = 0

    img = Image.open(image_file)
    img = img.convert('RGB')
    width, height = size
    for x in range (0, width):
        for y in range (0, height):
            r, g, b = img.getpixel((x,y))
            r_tot += r
            g_tot += g
            b_tot += b
    av_r = r_tot / (width * height)
    av_g = g_tot / (width * height)
    av_b = b_tot / (width * height)
    hls = colorsys.rgb_to_hls(av_r / 255.0, av_g / 255.0, av_b / 255.0)
    hsl = (hls[0], hls[2], hls[1])
    bg_hsl("Average colour determined", hls[0], hls[2], hls[1])
    return hsl

def colour_match(opp_hue, opp_sat, opp_light, av_hue, av_sat, av_light, tolerance):
    # clamp / normalise tolerance to [0,100]
    t = max(0.0, min(100.0, float(tolerance)))

    # ---- linear interpolation for tolerances ----
    # Hue tolerance: 100 -> 5°, 0 -> 40°
    hue_min_tol = 5.0
    hue_max_tol = 40.0
    hue_tol = hue_min_tol + (hue_max_tol - hue_min_tol) * (1.0 - t / 100.0)

    # Saturation tolerance: 100 -> 5, 0 -> 15
    sat_min_tol = 5.0
    sat_max_tol = 15.0
    sat_tol = sat_min_tol + (sat_max_tol - sat_min_tol) * (1.0 - t / 100.0)

    # Lightness tolerance: same ias above
    light_min_tol = 5.0
    light_max_tol = 15.0
    light_tol = light_min_tol + (light_max_tol - light_min_tol) * (1.0 - t / 100.0)

    # ---- Hue difference with wrap-around (shortest angular distance) ----
    # formula: shortest difference in degrees between angles
    # result in [0, 180]
    hue_diff = abs((opp_hue - av_hue + 180.0) % 360.0 - 180.0)

    hue_ok = hue_diff <= hue_tol

    # ---- Saturation / Lightness differences (no wrap-around) ----
    # ensure values are clipped to 0..100 first (defensive)
    def clamp01(x): 
        return max(0.0, min(100.0, float(x)))

    opp_sat_c = clamp01(opp_sat)
    av_sat_c = clamp01(av_sat)
    opp_light_c = clamp01(opp_light)
    av_light_c = clamp01(av_light)

    sat_diff = abs(opp_sat_c - av_sat_c)
    light_diff = abs(opp_light_c - av_light_c)

    sat_ok = sat_diff <= sat_tol
    light_ok = light_diff <= light_tol

    # final combined decision
    return hue_ok and sat_ok and light_ok

def classify_image(image_path, size, hue, sat, light, scope, frequency):
    # Calculate tolerances based on scope (0-100)
    # Hue tolerance: 100 scope -> 5°, 0 scope -> 40°
    hue_min_tol = 5.0
    hue_max_tol = 40.0
    hue_tol = hue_min_tol + (hue_max_tol - hue_min_tol) * (1.0 - float(scope) / 100.0)

    # Saturation tolerance: 100 scope -> 5, 0 scope -> 15
    sat_min_tol = 5.0
    sat_max_tol = 15.0
    sat_tol = sat_min_tol + (sat_max_tol - sat_min_tol) * (1.0 - float(scope) / 100.0)

    # Lightness tolerance: same as above
    light_min_tol = 5.0
    light_max_tol = 15.0
    light_tol = light_min_tol + (light_max_tol - light_min_tol) * (1.0 - float(scope) / 100.0)

    # Define hue range with wrap-around
    upper_h = (hue + hue_tol) % 360.0
    lower_h = (hue - hue_tol) % 360.0

    # Define saturation range (0-100 scale)
    upper_s = min(100.0, sat + sat_tol)
    lower_s = max(0.0, sat - sat_tol)

    # Define lightness range (0-100 scale)
    upper_l = min(100.0, light + light_tol)
    lower_l = max(0.0, light - light_tol)

    img = Image.open(image_path)
    img = img.convert('RGB')
    width, height = size
    
    suitability = 0
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = img.getpixel((x, y))
            h, s, l = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
            h = h * 360.0  # Convert to 0-360 range
            s = s * 100.0  # Convert to 0-100 range
            l = l * 100.0  # Convert to 0-100 range
            
            # Check hue with wrap-around support
            hue_diff = abs((h - hue + 180.0) % 360.0 - 180.0)
            hue_ok = hue_diff <= hue_tol
            
            if hue_ok and (lower_s < s < upper_s) and (lower_l < l < upper_l):
                suitability += 1

    threshold = width * height            
    print(f"Image score = {suitability} / {threshold}")            

    if (suitability / (threshold)) > (float(frequency) / 100.0):
        print("Image accepted and saved")
        return True, suitability
    else:
        print("Criteria not met")
        return False, suitability

list_of_image_paths = count_images_in_folder()
desired_hue, desired_saturation, desired_lightness, desired_scope, desired_intensity = user_requirements()
opp_hue, opp_sat, opp_light = calc_opposite_colour(desired_hue, desired_saturation, desired_lightness)
print("Determining opposite colour to user input...")
bg_hsl("Opposite colour calculated", opp_hue, opp_sat, opp_light)

counter = 0
best_image_num = None
best_image_score = 0

for each_image_path in list_of_image_paths:  # Iterates over paths
    counter += 1
    print(f"Checking image {counter}")

    opp_hsl = calc_opposite_colour(desired_hue, desired_saturation, desired_lightness)
    
    new_thumbnail, new_size = resized_image(each_image_path)
    avg_hsl = average_colour(each_image_path, new_size)
    
    if colour_match(*opp_hsl, *avg_hsl, desired_scope):
        print("Image discounted as colours are no where near what user is looking for")
        continue # breaks this run of the loop
    
    accepted, score = classify_image(each_image_path, new_size, desired_hue, desired_saturation, desired_lightness, desired_scope, desired_intensity)
    
    if score > best_image_score:
        best_image_score = score
        best_image_num = counter
    
    if accepted:
        output_file_path = os.path.join(output_folder, os.path.basename(each_image_path))
        new_thumbnail.save(output_file_path)
    
    print()
    print()

print(f"best image score {best_image_score}")
    