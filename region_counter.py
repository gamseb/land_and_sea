def region_counter(input_file, output_file=False, show_output=False):
    import numpy as np
    import cv2 as cv
    import random
    random.seed(123) # For reproducible results

    im = cv.imread(input_file)

    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

    ret, thresh = cv.threshold(imgray, 200, 255, 0)

    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    poly_contours = list()
    bound_rects = list()
    for contour in contours:
        # Bounding rectangle for each contour
        bound_rect = cv.boundingRect(contour)
        bound_rects.append(bound_rect)

        """These could be helpful if we were interested in having fewer points
           and approximating the contour to a known polygon.
           But we use the contours with many points to more precisely combine
           the pixels they enclose.
        """
        # poly_contour = cv.approxPolyDP(contour, 3, True)
        # poly_contours.append(poly_contour)

    def drawContour(poly_contour, imout):
        color = tuple([random.uniform(0, 255) for i in range(3)])
        last_index = poly_contour.shape[0] - 1
        for i in range(1, poly_contour.shape[0]):
            p1 = tuple(poly_contour[i - 1][0])
            p2 = tuple(poly_contour[i][0])
            cv.line(imout, p1, p2, color, 2)
        p1 = tuple(poly_contour[last_index][0])
        p2 = tuple(poly_contour[0][0])
        cv.line(imout, p1, p2, color, 2)

    def drawBoundRect(bound_rect, imout):
        color = tuple([random.uniform(0, 255) for i in range(3)])
        x, y, w, h = bound_rect
        cv.rectangle(imout, (x, y), (x + w, y + h), color, 2)

    imres = cv.cvtColor(np.zeros_like(thresh) + 255, cv.COLOR_GRAY2BGR)

    for contour in contours:
        drawContour(contour, imres)

    #print("Number of contours: {}".format(len(contours)))

    def drawContour(poly_contour, imout):
        color = tuple([random.uniform(0, 255) for i in range(3)])
        last_index = poly_contour.shape[0] - 1
        for i in range(1, poly_contour.shape[0]):
            p1 = tuple(poly_contour[i - 1][0])
            p2 = tuple(poly_contour[i][0])
            cv.line(imout, p1, p2, color, 2)
        p1 = tuple(poly_contour[last_index][0])
        p2 = tuple(poly_contour[0][0])
        cv.line(imout, p1, p2, color, 2)

    def drawBoundRect(bound_rect, imout):
        color = tuple([random.uniform(0, 255) for i in range(3)])
        x, y, w, h = bound_rect
        cv.rectangle(imout, (x, y), (x + w, y + h), color, 2)

    # Generate the Set of Pixels that are inside a Contour
    def genPixelSet(img, contour, bound_rect, UnionSet, threshEdgePixelsRatio=0.3):
        """Helper function that generates a Set of pixels that are inside
        the contours given.
        Returns:
            A Set containing the pixels within the Area or None if the Area
            generated should be discarded, and (2) an update on the 'UnionSet'
            parameter.
        Parameters:
            img: The image to perform lookup
            contour: The contour coordinates
            bound_rect: The contour's bounding box. A loop is run on its
                boundaries to add the right pixels to Set
            threshEdgePixelsRatio: A threshold indicating if a area should
                be discarted. The ratio indicates how many edge pixels are
                within the targeted area.
            UnionSet: A Set containing all the pixels that are already contained
                by another area.
        """
        S = set()
        x0, y0, w, h = bound_rect
        xF = x0 + w
        yF = y0 + h
        edgePixels = 0
        for x in range(x0, xF):
            for y in range(y0, yF):
                if (x, y) not in UnionSet and cv.pointPolygonTest(contour, (x, y), False) >= 0:
                    # If the pixel does not belong to another Set
                    # And is inside the bounds of the generated polygon
                    # It is a candidate to be added to the current Set
                    if img[y][x] != 0:
                        # Assuming black pixels (0) are Edge Pixels
                        # We add the pixel if it is not an Edge Pixel
                        S.add((x, y))
                    else:
                        edgePixels += 1
        elems = len(S)
        if elems > 0:
            ratio = edgePixels / (elems + edgePixels)
            if ratio < threshEdgePixelsRatio:
                # If the generated Set passes the ratio it is returned
                return S
        return None

    def findAreas_(img, contours, bound_rects, hierarchy, UnionSet=set(), index=0, threshEdgePixelsRatio=0.3):
        """Helper function that covers the hierarchy recursively in order to
           find the Areas.
        Returns:
            A tuple which elements are (1) The Value returned by genPixelSet and
            (2) an update on the 'UnionSet' parameter.
            parameter.
        Parameters:
            img: The image to perform lookup
            contours: The list of contour coordinates
            bound_rect: The list of each contour's bounding box.
            hierarchy: The hierarchy of the contours.
            UnionSet: A Set containing all the pixels that are already contained
                by another area. Needs to be updated after calling the function
                recursively.
        """
        # Use for recursion
        areasHead = []
        areasTail = []

        S = None
        childIndex = hierarchy[0][index][2]
        if childIndex < 0:
            # Always start "labeling" with the contours that does not have children.
            S = genPixelSet(img, contours[index], bound_rects[index], UnionSet, threshEdgePixelsRatio)
        else:
            # If the contour has children, their pixels should be labeled first
            areasHead, UnionSet = findAreas_(img, contours, bound_rects, hierarchy, UnionSet, childIndex,
                                             threshEdgePixelsRatio)
            # Now proceed to generate the current contour Set
            S = genPixelSet(img, contours[index], bound_rects[index], UnionSet, threshEdgePixelsRatio)

        # Add all pixels of the current Contour to the UnionSet
        if S:
            UnionSet = UnionSet.union(S)

        # Visit the other contours in the same level
        nextIndex = hierarchy[0][index][0]
        if nextIndex > -1:
            areasTail, UnionSet = findAreas_(img, contours, bound_rects, hierarchy, UnionSet, nextIndex,
                                             threshEdgePixelsRatio)

        # Combine the results obtained and return
        areas = areasHead + ([S] if S else []) + areasTail
        return areas, UnionSet

    def findAreas(img, contours, bound_rects, hierarchy, threshEdgePixelsRatio=0.3):
        """The function that should be called by the user.
           Internally calls the helper function.
        """
        return findAreas_(img, contours, bound_rects, hierarchy, set(), 0, threshEdgePixelsRatio)[0]

    AREAS = findAreas(thresh, contours, bound_rects, hierarchy)

    # imres = cv.cvtColor(np.zeros_like(imgray), cv.COLOR_GRAY2BGR)
    imres = cv.cvtColor(imgray, cv.COLOR_GRAY2BGR)
    print("Number of areas: {}".format(len(AREAS) - 1))
    for area in AREAS:
        color = tuple([random.randrange(0, 255) for _ in range(3)])
        for (j, i) in area:
            imres[i][j] = color
    if output_file:
        cv.imwrite(output_file, imres)
    if show_output:
        cv.imshow("", imres)
        cv.waitKey()

    return len(AREAS) - 1


# regions = region_counter('generated_plot.png', 'colorized_plot.png')
# print("The number of regions is: " + str(regions))
