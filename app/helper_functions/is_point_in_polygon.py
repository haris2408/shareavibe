def is_point_on_line(point, line):
    """
    Check if a point lies on a line.

    Parameters:
    point (tuple): The (x, y) coordinates of the point.
    line (tuple): A tuple of two points defining the line segment.

    Returns:
    bool: True if the point is on the line, False otherwise.
    """
    x1, y1 = line[0]
    x2, y2 = line[1]
    x, y = point
    return abs((y2 - y1) * x + (x1 - x2) * y + (x2 * y1 - x1 * y2)) < 0.000001


def is_point_above_line(point, line):
    """
    Check if a point is above a line.

    Parameters:
    point (tuple): The (x, y) coordinates of the point.
    line (tuple): A tuple of two points defining the line segment.

    Returns:
    bool: True if the point is above the line, False otherwise.
    """
    x1, y1 = line[0]
    x2, y2 = line[1]
    x, y = point
    return (y - y1) * (x2 - x1) > (y2 - y1) * (x - x1)


def is_inside_polygon(point, rect):
    print("inside is_inside_polygon")
    """Checks if a point lies inside a rectangle.

    Parameters:
    point (tuple): The (latitude, longitude) coordinates of the point.
    rect (list of tuples): The vertices of the rectangle in the format:
        [(top_left_lat, top_left_long), (top_right_lat, top_right_long),
         (bottom_right_lat, bottom_right_long), (bottom_left_lat, bottom_left_long)]

    Returns:
    bool: True if the point is inside the rectangle, False otherwise.
    """
    if not rect or len(rect) != 4:
        raise ValueError("Invalid rectangle coordinates")

    x, y = point
    x_min = min(rect[0][0], rect[3][0])
    x_max = max(rect[1][0], rect[2][0])
    y_min = min(rect[0][1], rect[1][1])
    y_max = max(rect[2][1], rect[3][1])

    if x < x_min or x > x_max or y < y_min or y > y_max:
        return False

    # Check if the point lies on the rectangle edges
    for i in range(4):
        x1, y1 = rect[i]
        x2, y2 = rect[(i+1) % 4]
        if is_point_on_line(point, ((x1, y1), (x2, y2))):
            return True

    # Check if the point is inside the rectangle
    count = 0
    for i in range(4):
        x1, y1 = rect[i]
        x2, y2 = rect[(i+1) % 4]
        if is_point_above_line(point, ((x1, y1), (x2, y2))):
            count += 1
    return count % 2 == 1




# def on_segment(p, q, r):
#     """Return True if point q is on segment pr, False otherwise."""
#     return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0])
#             and q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

# def is_left(p, q, r):
#     """Return twice the signed area of the triangle defined by p, q, and r."""
#     return (q[0] - p[0]) * (r[1] - p[1]) - (r[0] - p[0]) * (q[1] - p[1])

# def intersection(p1, q1, p2, q2):
#     """Return True if line segment p1q1 intersects line segment p2q2, False otherwise."""
#     o1 = is_left(p1, q1, p2)
#     o2 = is_left(p1, q1, q2)
#     o3 = is_left(p2, q2, p1)
#     o4 = is_left(p2, q2, q1)
#     if (o1 > 0 and o2 < 0) or (o1 < 0 and o2 > 0) or (o3 > 0 and o4 < 0) or (o3 < 0 and o4 > 0):
#         return True
#     if o1 == 0 and on_segment(p1, p2, q1):
#         return True
#     if o2 == 0 and on_segment(p1, q2, q1):
#         return True
#     if o3 == 0 and on_segment(p2, p1, q2):
#         return True
#     if o4 == 0 and on_segment(p2, q1, q2):
#         return True
#     return False

# def is_simple_polygon(polygon):
#     """Return True if the polygon is a simple polygon, False otherwise."""
#     n = len(polygon)
#     for i in range(n):
#         p1, q1 = polygon[i], polygon[(i+1)%n]
#         for j in range(i+1, n):
#             p2, q2 = polygon[j], polygon[(j+1)%n]
#             if intersection(p1, q1, p2, q2):
#                 return False
#     return True

# def is_inside_polygon(point, polygon):
#     """Check if a point is inside a polygon.

#     Parameters:
#     point (tuple): The (x, y) coordinates of the point.
#     polygon (list of tuples): The vertices of the polygon in order.

#     Returns:
#     bool: True if the point is inside the polygon, False otherwise.
#     """
#     # if not is_simple_polygon(polygon):
#     if True == False:
#         raise ValueError("Polygon is not a simple polygon.")
#     wn = 0
#     for i in range(len(polygon)):
#         if on_segment(polygon[i], polygon[(i+1)%len(polygon)], point):
#             return True
#         if polygon[i][1] <= point[1]:
#             if polygon[(i+1)%len(polygon)][1] > point[1]:
#                 if is_left(polygon[i], polygon[(i+1)%len(polygon)], point) > 0:
#                     wn += 1
#         else:
#             if polygon[(i+1)%len(polygon)][1] <= point[1]:
#                 if is_left(polygon[i], polygon[(i+1)%len(polygon)], point) < 0:
#                     wn -= 1
#     return wn >= 0