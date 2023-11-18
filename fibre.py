import re
import codecs
from datetime import datetime


def maxSpeedL2Mapper(groups):
    return '<br> Down: ' + str(int(groups[0]) / 1000000) + 'Mbit/s <br> Up: ' + str(int(groups[1]) / 1000000) + 'Mbit/s'


def syncSpeedMapper(groups):
    return '<br> Down: ' + str(int(groups[0]) / 1000000) + 'Mbit/s <br> Up: ' + str(int(groups[1]) / 1000000) + 'Mbit/s'


def creationDateMapper(groups):
    parsed_time = datetime.strptime(groups[0], '%a %b %d %H:%M:%S CEST %Y')
    formattedCreationDate = parsed_time.strftime('%d.%m.%Y | %H:%M:%S')
    return formattedCreationDate


def firstUseDateMapper(groups):
    parsed_time = datetime.strptime(groups[0], '%Y-%m-%d %H:%M:%S')
    formattedFirstUseDate = parsed_time.strftime('%d.%m.%Y | %H:%M:%S')
    return formattedFirstUseDate


def endDateOfFirmwareUpgradeMapper(groups):
    parsed_time = datetime.strptime(groups[0], '%Y-%m-%d %H:%M:%S')
    formattedEndDateOfFirmwareUpgradeMapper = parsed_time.strftime('%d.%m.%Y | %H:%M:%S')
    return formattedEndDateOfFirmwareUpgradeMapper


def macAddressMapper(groups):
    formattedMacAddress = groups[0].upper()
    return formattedMacAddress


patterns = {
    'creationDate': {
        'mapper': creationDateMapper,
        'regex': r'##### TITLE Datum\s(.*)'
    },

    'boxModel': r'CONFIG_PRODUKT_NAME=(.*)',
    'firmware': r'CONFIG_VERSION=(.*)',
    'serialNumber': r'SerialNumber\t(.*)',
    'firstUseDate': {
        'mapper': firstUseDateMapper,
        'regex': r'FirstUseDate =\s\"(.*)\"'
    },

    'syncSpeed': {
        'mapper': syncSpeedMapper,
        'regex': r'syncsspeed\s+(\d+)\s+(\d+)',
    },

    'maxSpeedL2': {
        'mapper': maxSpeedL2Mapper,
        'regex': r'maxspeed\sL2\s+(\d+)\s+(\d+)',
    },

    'macAddress': {
        'mapper': macAddressMapper,
        'regex': r'macaddr=\b([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}\b)',#
    },
    'maxUpstreamRate': r'MaxUpstreamRate=\d\n(.*\n.*\n.*\n.*)',
    'dslVersions': r'/var/dsl/dsl_versions.txt\n.*(\n.*\n.*\n.*\n)',
    'activeProvider': r'active_provider = \"(.*)\"',
    'lastFirmware': r'last_version =\s\"\d{3}\.(\d{2}\.\d{2})',
    'endDateOfFirmwareUpgrade': {
        'mapper': endDateOfFirmwareUpgradeMapper,
        'regex': r'end = "(.*)";',
    },
    
    'ipv4Ipv6': r'External address status:\n\t(IPv4:.*)\n\t(IPv6:.*)',
	
}

# Die "FileData" Klasse enthält Methoden zum Extrahieren und Verarbeiten von Informationen aus einer Datei.
class FileData:
    # Konstruktor, um die Datei zu öffnen und Daten zu lesen
    def __init__(self, fileName):
        with codecs.open(fileName, 'r', encoding='utf-8', errors='ignore') as supportFile:
            self.supportData = supportFile.read()
            self.lines = self.supportData.split('\n')


    def extractOverviewData(self):
        overviewData = {}

        for key, item in patterns.items():
            match = re.search(item['regex'] if isinstance(item, dict) else item, self.supportData)
            if match:
                mapper = lambda groups: groups[len(groups)-1] # Default: letzte Regex-Match Ausagbe
                if isinstance(item, dict) and item.get('mapper') is not None:
                    mapper = item['mapper']
                overviewData[key] = mapper(match.groups())
        return overviewData


    #Daten, welche nach dem Regex verarbeitet werden müssen
    def postProcessOverviewData(self,overviewDataResult):
        postProcessOverviewData = {}
        today = datetime.now()
        parsedTime =  datetime.strptime(overviewDataResult['firstUseDate'], '%d.%m.%Y | %H:%M:%S')
        ageInDays = (today - parsedTime).days
        postProcessOverviewData['ageInDays'] = ageInDays
        return postProcessOverviewData
    

    def extractNetworkDevices(self):
        inside_section = False
        networkDevicesSection = []
        for line in self.lines:
            if "interface identifiers:" in line:
                inside_section = True
                continue  # Springe zur nächsten Zeile, um die Überschrift zu überspringen
            elif "##### END SECTION neighbours" in line:
                inside_section = False
            elif inside_section:
                networkDevicesSection.append(line.strip())  # Füge die Zeile zur Liste hinzu
        return networkDevicesSection


    def extractEventData(self):
        inside_section = False
        eventSection = []
        for line in self.lines:
            if "##### BEGIN SECTION Events Events" in line:
                inside_section = True
                section_content = []
            elif "##### END SECTION Events" in line:
                if inside_section:
                    inside_section = False
                    # Entfernt "Events" und "------" aus dem Abschnitt
                    section_content = [line for line in section_content if not line.strip() in ["Events", "------"]]
                    eventSection.extend(section_content)
            elif inside_section:
                section_content.append(line)
        return eventSection