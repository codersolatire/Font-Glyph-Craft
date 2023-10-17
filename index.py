import json
from fontTools.ttLib import TTFont
from fontTools.pens.reportLabPen import ReportLabPen
from reportlab.lib import colors
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Group, Drawing, scale, Path
from PIL import Image, ImageDraw, ImageFont

import string

metrics_dict = {}

def export_png_glyphs(font_path, output_directory):
    # Load the TrueType font file
    font = TTFont(font_path)

    unitsPerEm = float(font["head"].unitsPerEm)

    ascender, descender = font['OS/2'].usWinAscent, -font['OS/2'].usWinDescent
    # ascender, descender = font.getmetrics()

    height = ascender - descender

    print(ascender, descender)

    glyphset = font.getGlyphSet(preferCFF=True, location=None, normalized=False)

    # chars = []

    chars = {}

    for cmap in font['cmap'].tables:
        for (code, _) in cmap.cmap.items():
            # print(code)
            # chars.append(chr(code))

            # chars[_] = chr(code)
            chars[_] = code
    
    print(chars)

    cmap_index = 1

    for glyphName in glyphset.keys():

        if font["glyf"][glyphName].numberOfContours:

            if glyphset[glyphName].name in chars:

                width_, lsb = font['hmtx'][glyphName]
                
                rsb = width_ - lsb - (font['glyf'][glyphName].xMax - font['glyf'][glyphName].xMin)

                ascii_value = chars[glyphset[glyphName].name]

                print(glyphset[glyphName].name, width_, lsb, rsb, font["glyf"][glyphName].yMax, font['glyf'][glyphName].xMax, font['glyf'][glyphName].xMin, chars[glyphset[glyphName].name], ascii_value)


                IMAGE_WIDTH, IMAGE_HEIGHT = glyphset[glyphName].width, int(height)

                pen = ReportLabPen(glyphset, Path(fillColor=colors.grey, strokeWidth=1))

                g = glyphset[glyphName]
                g.draw(pen)
                
                g = Group(pen.path)
                g.translate(abs(lsb), abs(descender))
                # g.scale(0.3, 0.3)

                d = Drawing(IMAGE_WIDTH+abs(lsb)+abs(rsb), IMAGE_HEIGHT)
                d.add(g)

                image = renderPM.drawToPIL(d)
                
                fromImage = Image.new('RGBA', (IMAGE_WIDTH+abs(lsb)+abs(rsb), IMAGE_HEIGHT), color=(255, 255, 255))
                
                fromImage.paste(image, (0, 0))

                imageFile = output_directory + "/%s.png" % (cmap_index-1)

                print(chars[glyphset[glyphName].name])

                metrics_dict[str(cmap_index-1)+".png"] = {"ASCII": ascii_value, "Name": glyphName, "Width": width_, "LSB": lsb, "RSB": rsb}

                cmap_index += 1

                fromImage.save(imageFile)

    print(metrics_dict)

    with open("metrics.json", "w") as outfile:
        json.dump(metrics_dict, outfile)


font_path = "font.ttf"
output_directory = "output/png_index"

export_png_glyphs(font_path, output_directory)
