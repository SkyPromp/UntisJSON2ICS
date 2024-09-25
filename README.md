example:
```py
from JSON2ICS import getEvents, filterRooster, writeEvents


r_class1 = filterRooster(getEvents("files/input/class1.json"), exclusions_file="files/exclusions/class1_exclusions.txt")
r_class2 = filterRooster(getEvents("files/input/class2.json"), exclusions_file="files/exclusions/class2_exclusions.txt")

writeEvents(r_class1 + r_class2)
```
