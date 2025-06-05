import os
from shapely.geometry import LineString, Polygon, mapping, MultiPoint
import json
import math
import numpy as np
from geometry_utils import bearing, get_point_at_distance, haversine_distance

reverse_coordinates = True

if reverse_coordinates:
    file_path = os.path.join(os.path.dirname(__file__), "parking_polygons_reversed.geojson")
    config_file = open(os.path.join(os.path.dirname(__file__), "parking_sectors.json"))
    config_geometry_file = os.path.join(os.path.dirname(__file__), "config_geometry_reversed.geojson")
else:
    file_path = os.path.join(os.path.dirname(__file__), "parking_polygons.geojson")
    config_file = open(os.path.join(os.path.dirname(__file__), "parking_sectors.json"))
    config_geometry_file = os.path.join(os.path.dirname(__file__), "config_geometry.geojson")
official_slots = json.load(config_file)
config_file.close()
parkingPolygons = []
config_geometry = {}


parking_slot_width = 0.003854667
parking_slot_length = 0.014


def save_polygon(id, p1, p2, p3, p4):
    if reverse_coordinates:
        p1 = p1[::-1]
        p2 = p2[::-1]
        p3 = p3[::-1]
        p4 = p4[::-1]
    parkingPolygons.append({
        "id": id,
        "geometry_data": Polygon([
            p1,  
            p2,
            p3,
            p4
        ])
    })

def generate_parking_slots(sector):
    start = {"y": sector["start"]["y"], "x": sector["start"]["x"]}
    j = 0
    skip = 0
    sector_id = sector["id"]
    current_group = sector["current_group"] if "current_group" in sector else 0
    if "width" in sector:
        d = sector["width"] / 1000
    else:
        d = parking_slot_width
    
    if "length" in sector:
        slot_length = sector["length"] / 1000
    else:
        slot_length = parking_slot_length
    
    if "skip" in sector:
        skip = sector["skip"]
    
    layout = "normal" if "layout" not in sector else sector["layout"]
    parking_angle = 90

    #schema: start - 0, end - 1, start2 - 2, multipoint - 3
    config_data = {
        "sector_data": {
            "start": [],
            "end": [],
            "start2": [],
            "multiline": []
        }
    }
    
    config_geometry[sector_id][current_group] = config_data
    config_geometry[sector_id][current_group]["sector_data"]["start"] = [sector["start"]["y"], sector["start"]["x"]] if not reverse_coordinates else [sector["start"]["x"], sector["start"]["y"]]
    if "end" in sector:
        config_geometry[sector_id][current_group]["sector_data"]["end"] = [sector["end"]["y"], sector["end"]["x"]] if not reverse_coordinates else [sector["end"]["x"], sector["end"]["y"]]
    if "start2" in sector:
        config_geometry[sector_id][current_group]["sector_data"]["start2"] = [sector["start2"]["y"], sector["start2"]["x"]] if not reverse_coordinates else [sector["start2"]["x"], sector["start2"]["y"]]
        
    #parking slots are at an angle
    if layout == "angle":
        end = {"y": sector["end"]["y"], "x": sector["end"]["x"]}
        startX = start["x"]
        endX = end["x"]
        startY = start["y"]
        endY = end["y"]
        
        width = 3.5 if not "width" in sector else sector["width"]
        width = width / 1000
        #which side of line 'right' or 'left'
        reverse = True if not "side" in sector else sector["side"]
        #which side the slot will be pointing 'up' or 'down'
        direction = True if not "direction" in sector else sector["direction"]
        
        numbering = "normal" if not "numbering" in sector else sector["numbering"]
        total_groups = sector["total_groups"] if "total_groups" in sector else 1

        #Bearing
        brng = bearing(startY, startX, endY, endX)  # in degrees
        parking_angle = 180 - 90 - sector["parking_angle"]
        
        extend = True if "extend" not in sector else sector["extend"]
        
        #angle of the parking slot
        if direction:
            widthBearing = (brng + (180-parking_angle) + 360) % 360
            lenghtBearing = (widthBearing - 90 + 360) % 360  
        else:
            widthBearing = (brng + parking_angle + 360) % 360
            lenghtBearing = (widthBearing + 90 + 360) % 360

        marginOferror = 0.0015
        #distance until the end point
        distance = haversine_distance(startY, startX, endY, endX)

        current_distance = 0
        #law of sinus to find the distance to next slot
        #use the triangle that is between 2 parking slots and a line that the slots are on
        #90 degree angle between one slot entrance and the next slots's side, angle of a parking slot and the slot width (entrance) in kilometers - find the hypothenus which is the distance
        d = (width * math.sin(math.radians(90))) / math.sin(math.radians(180-90-parking_angle))


        breakFlag = True


        while breakFlag: 
            #loop until reached the count, if not set then until reached the distance
            if "count" in sector and j >= sector["count"] - 1:
                breakFlag = False
            if current_distance + d - marginOferror > distance and not "count" in sector:
                breakFlag = False
            
            startX = start["x"]
            startY = start["y"]

            yDistance, xDistance = get_point_at_distance(startY, startX, d, brng)
            
            if direction:
                reverseWidth = not reverse
            else:
                reverseWidth = reverse
                
            lengthY, lengthX = get_point_at_distance(startY, startX, slot_length, lenghtBearing, reverse=reverse)
            if extend:
                widthY, widthX = get_point_at_distance(startY, startX, d, brng, reverse=reverseWidth)
                lengthY2, lengthX2 = get_point_at_distance(lengthY, lengthX, width, widthBearing, reverse=reverse)
            else:
                widthY, widthX = get_point_at_distance(startY, startX, width, widthBearing, reverse=reverse)
                lengthY2, lengthX2 = get_point_at_distance(widthY, widthX, slot_length, lenghtBearing, reverse=reverse)

            
            if numbering == "normal":
                id_number = j+1+skip
            elif numbering == "hop":
                id_number = j*total_groups+1+skip
                
            save_polygon(sector["id"] + str(id_number),
                        [round(startY, 6), round(startX, 6)],  
                        [round(lengthY, 6), round(lengthX, 6)],
                        [round(lengthY2, 6), round(lengthX2, 6)],
                        [round(widthY, 6), round(widthX, 6)])

            current_distance += d
            start["x"] = xDistance
            start["y"] = yDistance
            j+=1
            

    #create slots on a straight line if all 3 coordinates are set
    if "end" in sector and "start2" in sector:
        end = {"y": sector["end"]["y"], "x": sector["end"]["x"]}
        startX = start["x"]
        endX = end["x"]
        startY = start["y"]
        endY = end["y"]

        #Bearing
        brng = bearing(startY, startX, endY, endX)  # in degrees

        #generate parking slots until the count is reached
        if "count" in sector:
            lenghtVector = {"x": sector["start2"]["x"] - start["x"], "y": sector["start2"]["y"] - start["y"]}

            for i in range(1, sector["count"] + 1):
                startX = start["x"]
                startY = start["y"]
                
                yDistance, xDistance = get_point_at_distance(startY, startX, d, brng)
                save_polygon(sector["id"] + str(i+skip),
                        [start["y"], start["x"]],
                        [start["y"] + lenghtVector["y"], start["x"] + lenghtVector["x"]],
                        [yDistance + lenghtVector["y"], xDistance + lenghtVector["x"]],
                        [yDistance, xDistance]
                    )

                #next parking slot starts at the same point as the end of first slot
                start["x"] = xDistance
                start["y"] = yDistance
                j+=1
        else:
            #no count provided
            #generate until reached the distance with some margin of error if distance until end point is not exactly the slot width
            #remember the distance travelled and keep travelling until the end point
            marginOferror = 0.0019808
            #distance until the end point
            distance = haversine_distance(startY, startX, endY, endX)
            current_distance = d
            #bearing angle of the parking slot lenght
            lenghtBearing = bearing(startY, startX, sector["start2"]["y"], sector["start2"]["x"])
            while current_distance - marginOferror < distance:
                startX = start["x"]
                startY = start["y"]

                yDistance, xDistance = get_point_at_distance(startY, startX, d, brng)

                lengthY, lengthX = get_point_at_distance(startY, startX, slot_length, lenghtBearing)
                lengthY2, lengthX2 = get_point_at_distance(yDistance, xDistance, slot_length, lenghtBearing)

                save_polygon(
                        sector["id"] + str(j+1+skip),
                        [round(startY, 6), round(startX, 6)],  
                        [round(lengthY, 6), round(lengthX, 6)],
                        [round(lengthY2, 6), round(lengthX2, 6)],
                        [round(yDistance, 6), round(xDistance, 6)]
                    )

                start["x"] = xDistance
                start["y"] = yDistance
                current_distance += d
                j+=1
        
    if "multiline" in sector:
        constantWitdhBearing = False
        lenghtBearing = 0
        
        multiline_points = []

        for i, point in enumerate(sector["multiline"]):

            multiline_points.append([point["y"], point["x"]] if not reverse_coordinates else [point["x"], point["y"]])

            #can set using the start objective because everytime a new parking slot is generated start coordinates are updated
            startX = start["x"]
            startY = start["y"]
            endX = point["x"]
            endY = point["y"]
            brng = bearing(startY, startX, endY, endX)  # in degrees
            distance = haversine_distance(start["y"], start["x"], point["y"], point["x"])
            current_distance = d

            #if start 2 is set without the end coordinate, that means there will be a constant lenght angle (Parallelogram)
            #if not set then the lenght angle will be perpendicular to the slot width (rectangle)
            if "start2" in sector and not "end" in sector and not constantWitdhBearing:
                lenghtBearing = bearing(startY, startX, sector["start2"]["y"], sector["start2"]["x"])
                constantWitdhBearing = True
                reverse = False
            elif not constantWitdhBearing:
                lenghtBearing = (brng + 90 + 360) % 360
                reverse = True

            slotX = start["x"]
            slotY = start["y"]
            while current_distance - 0.0017808 < distance:

                yDistance, xDistance = get_point_at_distance(slotY, slotX, d, brng)
                lengthY, lengthX = get_point_at_distance(slotY, slotX, slot_length, lenghtBearing, reverse=reverse)
                lengthY2, lengthX2 = get_point_at_distance(yDistance, xDistance, slot_length, lenghtBearing, reverse=reverse)

                if numbering == "normal":
                    id_number = j+1+skip
                elif numbering == "hop":
                    id_number = j*total_groups+1+skip
                    
                save_polygon(sector["id"] + str(id_number),
                        [round(slotY, 6), round(slotX, 6)],  
                        [round(lengthY, 6), round(lengthX, 6)],
                        [round(lengthY2, 6), round(lengthX2, 6)],
                        [round(yDistance, 6), round(xDistance, 6)]
                        )
                j+=1
                current_distance += d
                slotX = xDistance
                slotY = yDistance

            start["x"] = point["x"]
            start["y"] = point["y"]

        config_geometry[sector_id][current_group]["sector_data"]["multiline"] = multiline_points
    
    return j

def generate(sectors):
    for sector in sectors:
        config_geometry[sector["id"]] = [{}]
        if "groups" in sector:
            skip = sector["skip"] if "skip" in sector else 0
            total_groups = len(sector["groups"])
            layout = sector["layout"] if "layout" in sector else "normal" 
            numbering = sector["numbering"] if "numbering" in sector else "normal"
            current_group = 0
            for group in sector["groups"]:
                if "count" in sector:
                    group["count"] = sector["count"]
                group["skip"] = skip
                group["id"] = sector["id"]
                group["total_groups"] = total_groups
                group["numbering"] = numbering

                if "layout" not in group:
                    group["layout"] = layout
                    
                group["current_group"] = current_group
                
                count = generate_parking_slots(group)
                if numbering == "hop":
                    skip += 1
                else:
                    skip += count
                current_group += 1
                if current_group < total_groups:
                    config_geometry[sector["id"]].append({})
        else:
            generate_parking_slots(sector)

    
generate(official_slots)

# Convert to GeoJSON format
geojson_features = []
for polygon_data in parkingPolygons:
    feature = {
        "type": "Feature",
        "properties": {"id": polygon_data["id"]},
        "geometry": mapping(polygon_data["geometry_data"])
    }
    geojson_features.append(feature)

geojson_data = {
    "type": "FeatureCollection",
    "features": geojson_features
}

geojson_config_geometry = []
for sector_id, groups in config_geometry.items():
    for group in groups:
        data = group["sector_data"]
        for config_geom_type, coordinates in data.items():
            if len(coordinates) <= 0:
                continue
            geometry = {}
            fill = "black"
            if config_geom_type == "start" or config_geom_type == "start2" or config_geom_type == "end":
                geometry["coordinates"] = coordinates
                geometry["type"] = "Point"
            elif config_geom_type == "multiline":
                geometry["type"] = "MultiPoint"
                geometry["coordinates"] = []
                fill = "lime"
                for coordinate in coordinates:
                    geometry["coordinates"].append(coordinate)
                    
            if geometry:
                feature = {
                    "type": "Feature",
                    "properties": {"id": sector_id, "type": config_geom_type},
                    "geometry": geometry,
                    "style": {
                        "fill": fill
                    }
                }
                geojson_config_geometry.append(feature)

geojson_config_geometry_data = {
    "type": "FeatureCollection",
    "features": geojson_config_geometry
}

# Write to GeoJSON file
with open(file_path, "w") as f:
    json.dump(geojson_data, f)

with open(config_geometry_file, "w") as f:
    json.dump(geojson_config_geometry_data, f)

print("GeoJSON file written successfully:", file_path)
