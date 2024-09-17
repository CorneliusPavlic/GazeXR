def scale_coords(gazePointX, gazePointY, newResolution, curResolution):

    horizontalScale = newResolution[0] / curResolution[0]
    verticalScale = newResolution[1] / curResolution[1]

    newX = int(float(gazePointX) * horizontalScale)
    newY = int(float(gazePointY) * verticalScale)

    return newX, newY