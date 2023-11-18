import os
import sys
import webbrowser
import tkinter as tk
from xdsl import FileData
#from fibre import FileData
from tkinter import filedialog


def selectDataFromDialogWindow():
    # Erstellt ein Dialog-Fenster, um Dateien einzulesen
    root = tk.Tk()
    root.withdraw()
    rawData = filedialog.askopenfilename()
    if not rawData:
        sys.exit('Keine Datei ausgewählt.')
    root.destroy()
    return rawData


def htmlOutput(overviewData, networkDevicesSection, eventSection):
    def format_data(key, default='N/A!'):
        return str(overviewData.get(key, default)).replace('\n', '<br>')


    creationDateOfSupportData = format_data('creationDate')
    boxModel = format_data('boxModel')
    firmware = format_data('firmware')
    serialNumber = format_data('serialNumber')
    firstUseDate = format_data('firstUseDate')
    syncSpeed = format_data('syncSpeed')
    maxSpeedL2 = format_data('maxSpeedL2')
    macAddress = format_data('macAddress')
    maxUpstreamRate = format_data('maxUpstreamRate')
    dslVersions = format_data('dslVersions')
    activeProvider = format_data('activeProvider')
    lastFirmware = format_data('lastFirmware')
    endDateOfFirmwareUpgrade = format_data('endDateOfFirmwareUpgrade')
    ageInDays = format_data('ageInDays')
    ipv4 = format_data('ipv4')
    ipv6 = format_data('ipv6')
    
    networkDevicesSection = '<br>'.join(networkDevicesSection) if networkDevicesSection else 'N/A'
    eventSection = '<br>'.join(eventSection) if eventSection else 'N/A'

    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Support-Datei Auswertung</title>
    </head>
    <body style='background-color: #ccf8f7;'>
        <h1> Diagnose für {boxModel} </h1>
        <hr>
        <h2>Overview Data</h2>
        <p><b>Box Model:</b> {boxModel} </p>
        <p><b>Date of First Use:</b> {firstUseDate} => {ageInDays} Days in use</p>
        <p><b>Date of Creation:</b> {creationDateOfSupportData} </p>
        <p><b>Current Firmware:</b> {firmware} Installed on: {endDateOfFirmwareUpgrade}</p> 
        <p><b>Last Firmware:</b> {lastFirmware} </p>
        <p><b>Serial Number:</b> {serialNumber} </p>
        <p><b>MAC Address:</b> {macAddress} </p>
        <p><b>IPv4:</b> {ipv4} </p>
        <p><b>IPv6:</b> {ipv6} </p>
        <p><b>Provider Flash:</b> {activeProvider} </p>
        <hr>
        <h2>DSL Information </h2>
        <p><b>Sync Speed:</b> {syncSpeed} </p>
        <p><b>Max Speed L2:</b> {maxSpeedL2} </p>
        <b>Störsicherheit:</b><br>{maxUpstreamRate} </p>
        <p><b>DSL Versions:</b> {dslVersions} </p>
        <hr>
        <h2>Network Devices</h2>
        <p><h4>Note: Not all listed devices have to be connected! (saved devices are also displayed)</h4></p>
        {networkDevicesSection}
        <hr>
        <h2>Eventlog</h2>
        {eventSection}
        <hr>
    </body>
    </html>'''

    file_path = "./index.html"
    with open(file_path, "wb") as file:
        file.write(html_content.encode('utf-8'))

    absolute_file_path = os.path.abspath(file_path)
    webbrowser.open_new_tab(absolute_file_path)


def main():
    support_file = selectDataFromDialogWindow()


    if support_file:
        result = FileData(support_file) # result ist ein Objekt der Klasse FileData
        overviewData = result.extractOverviewData()
        networkDevicesSection = result.extractNetworkDevices()
        eventSection = result.extractEventData()
        postProcessOverviewData = result.postProcessOverviewData(overviewDataResult = overviewData)
        overviewData = {**overviewData, **postProcessOverviewData}
        htmlOutput(overviewData, networkDevicesSection, eventSection)

if __name__ == "__main__":
    main()