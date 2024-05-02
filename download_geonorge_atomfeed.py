"""
Example of how to utilize geonorge http://geonorge.no Atom Feed to download fresh data whenever they're published. 

This code fetch the specified geonorge atom feed and download data, using the URL of the <link> element. 

To avoid unnescesary data trafic, this file is only downloaded if the time stamp in the <updated> element 
of the atom feed is newer than the time stamp found in the JSON file 'lastgeonorgedownload.json' (if present). 

Example of geonorge atom feed for NVDB routing application data in JSON format
https://nedlasting2.geonorge.no/geonorge/ATOM-feeds/NVDBRuteplanNettverksdatasett_AtomFeedSpatiaLite.xml

```xml
<feed xmlns:gml="http://www.opengis.net/gml" xmlns:georss="http://www.georss.org/georss" xmlns="http://www.w3.org/2005/Atom">
<generator version="2020.2.3.0" uri="https://nedlasting.geonorge.no/fmeserver"/>
<id>https://nedlasting.geonorge.no</id>
<link rel="self" href="https://nedlasting.geonorge.no" type="application/atom+xml"/>
<rights>Statens vegvesen</rights>
<subtitle>SpatiaLite-format</subtitle>
<title>NVDB Ruteplan nettverksdatasett</title>
<updated>2024-04-29T04:34Z</updated>
<entry>
<author>
<name>Kartverket</name>
</author>
<category term="EPSG:25833" scheme="http://www.opengis.net/def/crs/" label="EPSG/0/25833"/>
<content type="html">Trykk på linken for å laste ned landsdekkende data i koordinatsystemet EPSG:25833. <br /> <a href="https://nedlasting.geonorge.no/geonorge/Samferdsel/NVDBRuteplanNettverksdatasett/SpatiaLite/Samferdsel_0000_Norge_25833_NVDBRuteplanNettverksdatasett_SpatiaLite.zip">SpatiaLite-format, Landsdekkende<\a></content>
<id>https://nedlasting.geonorge.no/geonorge/Samferdsel/NVDBRuteplanNettverksdatasett/SpatiaLite/Samferdsel_0000_Norge_25833_NVDBRuteplanNettverksdatasett_SpatiaLite.zip_2024-03-06T09:58:14</id>
<link rel="alternate" href="https://nedlasting.geonorge.no/geonorge/Samferdsel/NVDBRuteplanNettverksdatasett/SpatiaLite/Samferdsel_0000_Norge_25833_NVDBRuteplanNettverksdatasett_SpatiaLite.zip" type="application/gml+xml;version=3.2.1" title="Datasettet som GML-fil i EPSG:25833"/>
<published>2024-04-29T06:34:24+02:00</published>
<rights>Statens vegvesen</rights>
<title>SpatiaLite-format, Landsdekkende</title>
<updated>2024-03-06T09:58:14</updated>
</entry>
</feed>
```

"""
import xml.etree.ElementTree as ET
import requests
import json 
from json import JSONDecodeError

def checkLastDownload( filename:str ): 
    """
    Reading json file containing the time stamp of previous download
    """
    lastDownload = '1950-01-01T00:00:00'
    try: 
        with open( filename) as f: 
            timeStampJson = json.load( f )
    except FileNotFoundError: 
        print( f"Filestamp-file not found: {filename}, fallback value lastDownload={lastDownload}")
    except JSONDecodeError: 
        print( f"Error parsing file {filename}, fallback value lastDownload={lastDownload}")
    else: 
        if 'lastDownload' in timeStampJson: 
            lastDownload = timeStampJson['lastDownload']
        else: 
            print( f"No lastdownload tag found in {filename}, fallback value lastDownload={lastDownload}")

    return lastDownload 

def writeLastDownload( filename:str, lastDowload:str, url:str ):
    """
    Writing time stamp of last successful download to JSON file 
    """ 
    myJson = {'comment' : 'AUTOMATIC GENERATED, DO NOT EDIT - Time stamp for last download from http://geonorge.no', 
                'lastDownload' : lastDowload, 
                 'url' : url }
    
    with open( filename, 'w') as f: 
        json.dump( myJson, f, indent=4 )

def getFreshData( geonorgeAtomFeedUrl:str, timestampfile='lastgeonorgedownload.json', datafile='download.zip' ): 

    r = requests.get( geonorgeAtomFeedUrl )
    if r.ok: 
        atomfeed = ET.fromstring( r.text )
        entry = atomfeed.find(  '{http://www.w3.org/2005/Atom}entry' )
        lastUpdated = entry.find( '{http://www.w3.org/2005/Atom}updated' )
        lastUpdated = str( lastUpdated.text )
        lastDownload = checkLastDownload( timestampfile )
        if lastDownload < lastUpdated: 
            link = entry.find( '{http://www.w3.org/2005/Atom}link' )
            link = link.attrib['href']

            print( f"Fresh data available {lastUpdated} > last download {lastDownload}, starting download of \n{link}")
            r = requests.get( link )
            with open( datafile, 'wb' ) as f: 
                f.write( r.content )
            writeLastDownload( timestampfile, lastUpdated, link)

        else: 
            print( f"Last download {lastDownload} >= {lastUpdated} geonorge atom feed time stamp, NOT downloading")

    else: 
        print( f"Can't access download link: HTTP {r.status_code} {r.text[0:200]} {geonorgeAtomFeedUrl}")



if __name__ == '__main__': 

    # URL to atom feed for NPRA routing application in spatialLite format 
    geonorgeAtomFeedUrl = 'https://nedlasting2.geonorge.no/geonorge/ATOM-feeds/NVDBRuteplanNettverksdatasett_AtomFeedSpatiaLite.xml'
    timestampfile = 'lastgeonorgedownload.json'
    datafile = 'download.zip'
    atomfeed = getFreshData( geonorgeAtomFeedUrl, timestampfile=timestampfile, )

    #### Other geonorge atom feeds of interest:
    ## ELVEG 2.0
    # https://nedlasting2.geonorge.no/geonorge/ATOM-feeds/Elveg2-0_AtomFeedGML.xml 
    # 
    ## Routing application data converted to file geodatababase format
    # https://nedlasting2.geonorge.no/geonorge/ATOM-feeds/NVDBRuteplanNettverksdatasett_AtomFeedFGDB.xml 