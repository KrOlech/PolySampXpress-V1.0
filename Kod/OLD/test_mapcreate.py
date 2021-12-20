import cv2 as cv
import numpy as np

# rozmiar obszaru
rozmiar = (1024, 768)

x, y, x1, y1 = 10, 10, 100, 100

d = 510

ofsetx, ofsety = int((50-25)*510), int((50-25)*510)

skala = 4

# rozmiar obszaru
rozmiar = (1024, 768)



map_size = int(x + 50 * 510 / skala)  # x size
map_size *= int(y + 50 * 510 / skala)  # y size
map_size *= 3  # RGB colors

# stworzenie tablicy przechowujacej obraz mapy
map = np.zeros(map_size, dtype=np.uint8)


# okreslenei ksztaltu tej tabliczy
map.shape = (int(x + 50 * 510 / skala), int(y + 50 * 510 / skala), 3)


x +=int(ofsetx)
x1+=int(ofsetx)
y +=int(ofsety)
y1+=int(ofsety)

x =int(x*(1024/int(x + 50 * 510 / skala)))
x1 =int(x1*(1024/int(x + 50 * 510 / skala)))
y =int(y*(768/int(x + 50 * 510 / skala)))
y1 =int(y1*(768/int(x + 50 * 510 / skala)))

imput = np.ones((x1-x)*(y1-y)*3)*255
imput.shape = ((x1-x), (y1-y), 3)

map = cv.resize(map, (1024,768))
print(x, y, x1, y1 )
map[x:x1, y:y1] = imput
cv.imshow("temp",map)
cv.waitKey(0)
