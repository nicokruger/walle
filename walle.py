#!/usr/bin/env python

import os
import sys
import tempfile

from PIL import Image

HOME = os.environ['HOME']

import locale

encoding = locale.getdefaultlocale()[1]
import subprocess
output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]

def make_wallpapers(WIDTH, HEIGHT, original):
    RATIO = float(WIDTH) / HEIGHT
    im = Image.open(original)
    width, height = im.size
    ratio = float(width) / height

    if ratio > RATIO:
        # resize to match height, then crop horizontally from center
        new_width = int(HEIGHT * ratio)
        im.thumbnail((new_width, HEIGHT), Image.ANTIALIAS)
        offset = int((new_width - WIDTH) / 2)
        #print("Offset:" + str(offset))
        cropped = im.crop((offset, 0, offset + new_width, HEIGHT))
    elif ratio < RATIO:
        # resize to match width, then crop vertically from center
        new_height = int(WIDTH / ratio)
        im.thumbnail((WIDTH, new_height), Image.ANTIALIAS)
        offset = int((new_height - HEIGHT) / 2)
        cropped = im.crop((0, offset, WIDTH, offset + HEIGHT))
    else:
        im.thumbnail((WIDTH, HEIGHT), Image.ANTIALIAS)
        cropped = im

    path, ext = os.path.splitext(original)
    tmpname = tempfile.mkstemp()[1]

    dest_png = tmpname + ".png"

    cropped.save(dest_png, 'PNG')

    return dest_png

def local_file(filename):
    return os.path.join(HOME, filename)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Usage: <script> <img>")
        sys.exit(1)
    else:
        filename = sys.argv[-1]

    if not os.path.exists(filename):
        print('Error: %s not found' % filename)
        sys.exit(1)

    displays = output.decode(encoding).split("\n")
    displays *= 2
    scaled_imgs = []
    displays = [ [int(v) for v in display.split("x")] for display in displays if len(display) > 0]
    for display in displays:
        if len(display) == 0:
            continue
        width = display[0]
        height = display[1]
        #print("Width: %i,%i" %(width, height))

        scaled_img = make_wallpapers(width,height,filename)
        scaled_imgs.append(scaled_img)

    all_width = sum(int(display[0]) for display in displays)
    all_height = max(int(display[1]) for display in displays)
    #print("Creating full image: %ix%i" % (all_width, all_height))
    
    all_img = Image.new("RGB",(all_width, all_height))
    x = 0
    for z in zip(displays, scaled_imgs):
        display, scaled_img = z
        img = Image.open(scaled_img)
        img_width, img_height = img.size
        all_img.paste(img, (x,0,x+img_width,img_height))
        x += img_width

    all_img_out = tempfile.mkstemp()[1] + ".png"
    all_img.save(all_img_out, "PNG")
    print(all_img_out)
        
