# -*- coding: utf-8 -*-
""" Tests for the services module """

from __future__ import unicode_literals
from soco.events import parse_event_xml

DUMMY_EVENT = """
<e:propertyset xmlns:e="urn:schemas-upnp-org:event-1-0">
    <e:property>
        <ZoneGroupState>&lt;ZoneGroups&gt;&lt;
            ZoneGroup Coordinator="RINCON_000XXX01400"
            ID="RINCON_000XXX1400:56"&gt;&lt;
            ZoneGroupMember UUID="RINCON_000XXX400"
            Location="http://XXX" ZoneName="Living Room"
            Icon="x-rincon-roomicon:living" Configuration="1"
            SoftwareVersion="XXXX"
            MinCompatibleVersion="XXXX"
            LegacyCompatibleVersion="XXXX" BootSeq="48"/&gt;&lt;
            /ZoneGroup&gt;&lt;ZoneGroup Coordinator="RINCON_000XXXX01400"
            ID="RINCON_000XXXX1400:0"&gt;&lt;
            ZoneGroupMember UUID="RINCON_000XXXX1400"
            Location="http://192.168.1.100:1400/xml/device_description.xml"
            ZoneName="BRIDGE" Icon="x-rincon-roomicon:zoneextender"
            Configuration="1" Invisible="1" IsZoneBridge="1"
            SoftwareVersion="XXXX" MinCompatibleVersion="XXXX"
            LegacyCompatibleVersion="XXXX" BootSeq="37"/&gt;&lt;
            /ZoneGroup&gt;&lt;ZoneGroup Coordinator="RINCON_000XXXX1400"
            ID="RINCON_000XXXX1400:57"&gt;&lt;
            ZoneGroupMember UUID="RINCON_000XXXX01400"
            Location="http://192.168.1.102:1400/xml/device_description.xml"
            ZoneName="Kitchen" Icon="x-rincon-roomicon:kitchen"
            Configuration="1" SoftwareVersion="XXXX"
            MinCompatibleVersion="XXXX" LegacyCompatibleVersion="XXXX"
            BootSeq="56"/&gt;&lt;/ZoneGroup&gt;&lt;/ZoneGroups&gt;
         </ZoneGroupState>
    </e:property>
    <e:property>
        <ThirdPartyMediaServersX>...s+3N9Lby8yoJD/QOC4W</ThirdPartyMediaServersX>
    </e:property>
    <e:property>
        <AvailableSoftwareUpdate>&lt;UpdateItem
            xmlns="urn:schemas-rinconnetworks-com:update-1-0"
            Type="Software" Version="XXXX"
            UpdateURL="http://update-firmware.sonos.com/XXXX"
            DownloadSize="0"
            ManifestURL="http://update-firmware.sonos.com/XX"/&gt;
         </AvailableSoftwareUpdate>
    </e:property>
    <e:property>
        <AlarmRunSequence>RINCON_000EXXXXXX0:56:0</AlarmRunSequence>
    </e:property>
    <e:property>
        <ZoneGroupName>Kitchen</ZoneGroupName>
    </e:property>
    <e:property>
        <ZoneGroupID>RINCON_000XXXX01400:57</ZoneGroupID>
    </e:property>
    <e:property>
        <ZonePlayerUUIDsInGroup>RINCON_000XXX1400</ZonePlayerUUIDsInGroup>
    </e:property>
</e:propertyset>
"""


def test_event_parsing():
    event_dict = parse_event_xml(DUMMY_EVENT)
    assert event_dict['ZoneGroupState']
    assert event_dict['AlarmRunSequence'] == 'RINCON_000EXXXXXX0:56:0'
    assert event_dict['ZoneGroupID'] == "RINCON_000XXXX01400:57"

