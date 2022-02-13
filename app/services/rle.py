"""Somebody's open source implementation of RLE encoding."""
# important: code here is not mine


import cv2


def rle_encoding(img, bits=8, binary=True):
    """
    img: Grayscale img.
    bits: what will be the maximum run length? 2^bits
    """

    # suppose A - means 0 bit, B means 1 bit
    # resulting rle string would be like: A5B3A1B9...
    if binary:
        ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    encoded = []
    count = 0
    prev = None
    fimg = img.flatten()
    th = 127
    for pixel in fimg:
        if binary:
            if pixel < th:
                pixel = 0
            else:
                pixel = 1
        if prev == None:
            prev = pixel
            count += 1
        else:
            if prev != pixel:
                encoded.append((count, prev))
                prev = pixel
                count = 1
            else:
                if count < (2**bits) - 1:
                    count += 1
                else:
                    encoded.append((count, prev))
                    prev = pixel
                    count = 1
    encoded.append((count, prev))

    resulted_rle_string = ""
    for count, bit in encoded:
        if bit == 0:
            bit = "A"
        else:
            bit = "B"
        resulted_rle_string += f"{count}{bit}"

    return resulted_rle_string
