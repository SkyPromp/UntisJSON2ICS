import json
from time import localtime
from uuid import uuid4


def getEvents(input_json_file):
    with open(input_json_file) as f:
        d = json.loads(f.read())
        data = d["data"]["result"]["data"]
        data = data["elementPeriods"][str(data["elementIds"][0])]
        periodids = []
        rooster = []
        for el in data:
            periodids.append(el["lessonNumber"])
            rooster.append((el["date"], el["startTime"], el["endTime"], list(map(lambda e: e['id'], el["elements"])), el["lessonText"]))

        data = d["data"]["result"]["data"]["elements"]
        id2name = {}
        for element in data:
            if "longName" in element.keys():
                ln = element["longName"]
                id = element["id"]
                if id not in id2name.keys():
                    id2name[id] = ln

    # 0->date,1->starttime,2->endtime,3->elements
    gmt_delta = localtime().tm_gmtoff // 36  # account for timezones (multiply by 100 for HHmm included)
    rooster = [[el[0], el[1] - gmt_delta, el[2] - gmt_delta, list(map(lambda id: id2name[id] if id in id2name.keys() else id, el[3])), el[4]] for el in rooster]

    for i in range(1, len(rooster)):
        prev = rooster[i - 1]
        curr = rooster[i]
        if prev[0] == curr[0] and prev[3] == curr[3] and prev[4] == curr[4] and prev[2] == curr[1]:
            rooster[i - 1][2] = rooster[i][2]
            rooster[i] = [None, None, None, None]

    rooster = filter(lambda x: x[0] is not None, rooster)

    rooster = list(map(lambda x: (x[0], str(x[1]).zfill(4), str(x[2]).zfill(4), x[3], x[4]), rooster))
    rooster.sort(key=lambda x: str(x[0]) + str(x[1]))

    return rooster


def filterRooster(rooster, exclusions_file):
    filtered_rooster = []

    for event in rooster:
        event_date = event[0]
        event_start_time = event[1]
        event_end_time = event[2]
        event_elements = event[3]
        event_description = event[4]
        event_name = ""
        event_locations = ""

        for i in range(len(event_elements)):
            if isinstance(event_elements[i], int):
                event_name = event_elements[i + 1]
                event_locations = ", ".join(list(map(lambda location: location.split(" ")[0], event_elements[i + 2:])))

        with open(exclusions_file) as g:
            exemptions = g.read().split('\n')
            if event_name in exemptions:
                continue

        filtered_rooster.append((event_date, event_start_time, event_end_time, event_name, event_description, event_locations))

    return filtered_rooster


def printRooster(rooster):
    for el in rooster:
        print(el)


def writeEvents(rooster):
    with open("files/output/output.ics", "w") as f:
        f.write(
        """BEGIN:VCALENDAR
PRODID:-//Max Poppe//iCal4j 1.0//EN
VERSION:2.0
CALSCALE:GREGORIAN\n"""
        )
        for event in rooster:
            event_date = event[0]
            event_start_time = event[1]
            event_end_time = event[2]
            event_name = event[3]
            event_description = event[4]
            event_locations = event[5]

            f.write("BEGIN:VEVENT\n")

            f.write(f"""DTSTAMP:20240527T000523Z
DTSTART:{event_date}T{event_start_time}00Z
DTEND:{event_date}T{event_end_time}00Z
UID:{uuid4()}
X-MICROSOFT-CDO-BUSYSTATUS:BUSY
X-GWSHOW-AS:BUSY
X-MICROSOFT-CDO-INTENDEDSTATUS:BUSY
SUMMARY:{event_name}
DESCRIPTION:{event_description}
LOCATION:{event_locations}\n""")

            f.write("END:VEVENT\n")

        f.write("END:VCALENDAR")
