from backend import models
import datetime
import math


async def load_data():
    swipes = await models.Swipe.all().prefetch_related(
        "swiper__tag_objects",
        "subject__tag_objects",
    )
    current_year = datetime.datetime.now().year
    xs = []
    ys = []
    for swipe in swipes:
        age_swiper = current_year - int(swipe.swiper.birth_date)
        age_subject = current_year - int(swipe.subject.birth_date)
        distance = calculate_distance(
            swipe.swiper.latitude,
            swipe.swiper.longitude,
            swipe.subject.latitude,
            swipe.subject.longitude,
        )
        tag_swiper = set(swipe.swiper.tag_objects)
        tag_subject = set(swipe.subject.tag_objects)
        tag_intersection = tag_swiper.intersection(tag_subject)
        similarity = 2 * len(tag_intersection) / (len(tag_swiper) + len(tag_subject))
        side = float(swipe.side)

        xs.append([age_swiper, age_subject, distance, similarity])
        ys.append([side])

    return xs, ys


def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # Calculate the distance
    distance = c * r
    return distance
