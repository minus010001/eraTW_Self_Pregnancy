import csv
import glob
import xml.etree.ElementTree as ET
import os

CSV_EXCEPT = ["list.csv", "tokei.csv", "eikianim.csv"]

def GetParams(row, base):
    ret = { "name":row[0], "src":base+row[1] }
    if len(row):
        ret["param"] = ",".join(row[2:])
    return ret

def OpenAndProcess(path, encoding, base):
    with open("resources/"+path, "r", newline='', encoding=encoding) as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            if len(row)<2 or row[0][0]==';':
                continue
            if row[1]=="ANIME":
                sprites[row[0]] = { "isAnime":True, "id":len(root) }
                ET.SubElement(root, "a", { "name":row[0], "width":row[2], "height":row[3]})
            elif sprites.get(row[0]) != None and sprites[row[0]]["isAnime"]:
                params = GetParams(row, base)
                params.pop("name")
                ET.SubElement(root[sprites[row[0]]["id"]], "f", params)
            else:
                ET.SubElement(root, "i", GetParams(row, base))
                sprites[row[0]] = { "isAnime":False }
        ET.indent(root, space='    ')
        with open(f"resources/{base}{file[:-4]}.xml", "wb+") as xmlFile:
            xmlFile.write(ET.tostring(root, encoding="utf_8"))

    os.rename("resources/"+path, "resources/"+path+".txt")

CSV_EXCEPT = [str.lower().replace("\\", "/") for str in CSV_EXCEPT]

sprites = {}

csvList = glob.glob("resources/**/*.csv", recursive=True)

for path in csvList:

    path = path.replace("\\", "/")[10:]
    file = os.path.basename(path)
    base = path[0:len(path)-len(file)]

    should_skip = False
    for bad_path in CSV_EXCEPT:
        if bad_path in path.lower():
             should_skip = True

    if should_skip:
        continue

    root = ET.fromstring('<sprites/>')

    print("processing", path, "...")

    try:
        OpenAndProcess(path, "utf_8", base)
    except UnicodeDecodeError:
        OpenAndProcess(path, "shift_jis", base)