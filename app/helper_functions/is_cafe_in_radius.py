from math import sin, cos, sqrt, atan2, radians
from app.models import Address

def get_cafes_within_radius(latitude, longitude, radius):
    # query the database to get all addresses
    print(f"inside get_cafes_within_radius with lat: {latitude} long: {longitude} and radius: {radius}")
    addresses = Address.objects.all()

    # create a list to store the cafes within the radius
    cafes_within_radius = []

    # iterate over all addresses to check if any are within the radius
    for addr in addresses:
        # calculate the distance between the point and the center of the rectangle
        x = longitude
        y = latitude
        cx = (addr.topLeft_coord_long + addr.topRight_coord_long + addr.bottomLeft_coord_long + addr.BottomRight_coord_long) / 4
        cy = (addr.topLeft_coord_lat + addr.topRight_coord_lat + addr.bottomLeft_coord_lat + addr.BottomRight_coord_lat) / 4
        dx = abs(x - cx)
        dy = abs(y - cy)
        distance = sqrt(dx*dx + dy*dy)

        # if the distance is within the radius, check if the rectangle is within the radius
        if distance <= radius:
            # calculate the distance between the point and each corner of the rectangle
            lat1 = radians(latitude)
            lon1 = radians(longitude)
            lat2 = radians(addr.topLeft_coord_lat)
            lon2 = radians(addr.topLeft_coord_long)
            lat3 = radians(addr.topRight_coord_lat)
            lon3 = radians(addr.topRight_coord_long)
            lat4 = radians(addr.bottomLeft_coord_lat)
            lon4 = radians(addr.bottomLeft_coord_long)
            lat5 = radians(addr.BottomRight_coord_lat)
            lon5 = radians(addr.BottomRight_coord_long)
            
            R = 6373.0 # approximate radius of earth in km
            
            dlon1 = lon1 - lon2
            dlat1 = lat1 - lat2
            a1 = sin(dlat1 / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon1 / 2)**2
            c1 = 2 * atan2(sqrt(a1), sqrt(1 - a1))
            distance1 = R * c1 * 1000
            
            dlon2 = lon1 - lon3
            dlat2 = lat1 - lat3
            a2 = sin(dlat2 / 2)**2 + cos(lat1) * cos(lat3) * sin(dlon2 / 2)**2
            c2 = 2 * atan2(sqrt(a2), sqrt(1 - a2))
            distance2 = R * c2 * 1000
            
            dlon3 = lon1 - lon4
            dlat3 = lat1 - lat4
            a3 = sin(dlat3 / 2)**2 + cos(lat1) * cos(lat4) * sin(dlon3 / 2)**2
            c3 = 2 * atan2(sqrt(a3), sqrt(1 - a3))
            distance3 = R * c3 * 1000
            
            dlon4 = lon1 - lon5
            dlat4 = lat1 - lat5
            a4 = sin(dlat4 / 2)**2 + cos(lat1) * cos(lat5) * sin(dlon4 / 2)**2
            c4 = 2 * atan2(sqrt(a4), sqrt(1 - a4))
            distance4 = R * c4 * 1000
            
            # if any part of the rectangle is within the radius, add it to the list of cafes within radius
            if distance1 <= radius or distance2 <= radius or distance3 <= radius or distance4 <= radius:
                cafes_within_radius.append(addr.cafe)
        
    return cafes_within_radius
