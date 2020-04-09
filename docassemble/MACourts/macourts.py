from docassemble.base.core import DAObject, DAList, DADict
from docassemble.base.util import path_and_mimetype, Address, LatitudeLongitude, DAStaticFile, text_type, PY2
from docassemble.base.legal import Court
import io, json, sys, requests, bs4, re, os #, cbor
from docassemble.webapp.playground import PlaygroundSection
import usaddress
from uszipcode import SearchEngine

__all__= ['get_courts_from_massgov_url','save_courts_to_file','MACourt','MACourtList','PY2'] 

def get_courts_from_massgov_url(url, shim_ehc_middlesex=True, shim_nhc_woburn=True):
    searcher = SearchEngine(simple_zipcode=True)
    """Load specified court directory page on Mass.gov and returns an MACourtList
    Properties include name, phone, fax, address, description (usually includes cities or county served), latitude, longitude
    """
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    jstring = soup.find_all( attrs={"data-drupal-selector":"drupal-settings-json"} )[0].text # this is the element that has the JSON data as of 6/19/2018
    jdata = json.loads(jstring)
    markers = jdata['locations']['googleMap']['markers']

    courts = []

    # The address and description are in a different part of the JSON
    for marker in markers:
        html_name = marker['infoWindow']['name']
        for item in jdata['locations']['imagePromos']['items']:
            description = ''
            if item['title']['text'] in html_name:
                name = item['title']['text'].rstrip()
                description = item['description']['richText']['rteElements'][0]['data']['rawHtml']['content']['#context']['value']
                break

        address = Address()
        orig_address = marker['infoWindow']['address'] # The geolocate method does _not_ work with PO Boxes (silently discards)
        clean_address = re.sub(r' *PO Box .*?,',"",orig_address)
        clean_address = re.sub(r' *P.O. Box .*?,',"",orig_address)
        has_po_box = not clean_address == orig_address # We want to track if there was a PO Box where mail should be delivered
        address.address = orig_address

        # See: https://usaddress.readthedocs.io/en/latest/ which explains how the mapping below prevents a RepeatedLabelError.
        # Basically parsing into line 1, line 2, etc is good enough for our use case.
        tag_mapping={
            'Recipient': 'recipient',
            'AddressNumber': 'address',
            'AddressNumberPrefix': 'address',
            'AddressNumberSuffix': 'address',
            'StreetName': 'address',
            'StreetNamePreDirectional': 'address',
            'StreetNamePreModifier': 'address',
            'StreetNamePreType': 'address',
            'StreetNamePostDirectional': 'address',
            'StreetNamePostModifier': 'address',
            'StreetNamePostType': 'address',
            'CornerOf': 'address',
            'IntersectionSeparator': 'address',
            'LandmarkName': 'address',
            'USPSBoxGroupID': 'address',
            'USPSBoxGroupType': 'address',
            'USPSBoxID': 'address',
            'USPSBoxType': 'address',
            'BuildingName': 'unit',
            'OccupancyType': 'unit',
            'OccupancyIdentifier': 'unit',
            'SubaddressIdentifier': 'unit',
            'SubaddressType': 'unit',
            'PlaceName': 'city',
            'StateName': 'state',
            'ZipCode': 'zip',
            } 
        try:
            address_parts = usaddress.tag(orig_address, tag_mapping=tag_mapping) 
        except usaddress.RepeatedLabelError:
            address_parts = usaddress.tag(clean_address, tag_mapping=tag_mapping) # Discard the PO box entry if necessary - not a valid address

        try:
            if address_parts[1].lower() == 'street address':
                address.address = address_parts[0].get('address')
                if address_parts[0].get('unit'):
                    address.unit = address_parts[0].get('unit')
                address.city.lower() = address_parts[0].get('city')
                address.state = address_parts[0].get('state')
                address.zip = address_parts[0].get('zip')
                zipinfo = searcher.by_zipcode(address.zip)
                address.county.lower() = zipinfo.county
                del zipinfo
            else:
                raise Exception('We expected a Street Address.')
        except:
            address.address = orig_address
            #address.geolocate(self.elements.get('full_address',''))

        if not hasattr(address,'address'):
            address.address = ''
        if not hasattr(address, 'city'):
            address.city.lower() = ''
        if not hasattr(address, 'state'):
            address.state = ''
        if not hasattr(address, 'zip'):
            address.zip = ''
        if not hasattr(address, 'county'):
            address.county.lower() = ''
        #if not hasattr(address, 'unit'):
            #address.unit = ''                    

        # store the data in a serializable format. maybe could refactor to use object_hooks, but would need to go all the way down to DAObject?
        court = {
            'name': name,
            'description': description,
            'has_po_box' : has_po_box,
            'phone':marker['infoWindow']['phone'],
            'fax':marker['infoWindow']['fax'],
            'address': {
                'city': address.city.lower(),
                'address': address.address,
                'state': address.state,
                'zip': address.zip,
                'county': address.county.lower(),
                'orig_address':  orig_address # the one-line original address, which may include a PO Box
            },
            'location': {
                'latitude': marker['position']['lat'],
                'longitude': marker['position']['lng']
            }
        }
        if hasattr(address, 'unit'):
            court['address']['unit']= address.unit

        courts.append(court)
        
    if shim_ehc_middlesex and url == 'https://www.mass.gov/orgs/housing-court/locations':
        court = {
            'name': "Eastern Housing Court - Middlesex Session",
            'description': "The Middlesex Session of the Eastern Housing Court serves Arlington, Belmont, and Cambridge, Medford and Somerville",
            'has_po_box' : False,
            'phone': "(781) 306-2715",
            'fax':"",
            'address': {
                'city': "Medford",
                'address': "4040 Mystic Valley Parkway",
                'state': "MA",
                'zip': "02155",
                'county': "Middlesex County",
                'orig_address':  "4040 Mystic Valley Parkway, Medford, MA 02155"
            },
            'location': {
                'latitude': 42.4048336,
                'longitude': -71.0893853
            }
        }
        courts.append(court)

    if shim_nhc_woburn and url == 'https://www.mass.gov/orgs/housing-court/locations': 
        court = {
            'name': "Northeast Housing Court - Woburn Session",
            'description': "The Woburn session of the Northeast Housing Court serves Bedford, Burlington, Concord, Everett,Lexington, Lincoln, Malden, Melrose, North Reading, Reading, Stoneham, Wakefield, Waltham, Watertown, Weston, Wilmington, Winchester, and Woburn.",
            'has_po_box' : False,
            'phone': "(978) 689-7833",
            'fax':"",
            'address': {
                'city': "Woburn",
                'address': "200 Trade Center",
                'unit': "Courtroom 540 - 5th Floor",
                'state': "MA",
                'zip': "01801",
                'county': "Middlesex County",
                'orig_address':  "200 Trade Center, Courtroom 540 - 5th Floor, Woburn, MA 01801"
            },
            'location': {
                'latitude': 42.500543,
                'longitude': -71.1656604
            }
        }
        courts.append(court)

    courts.sort(key=lambda k: k['name']) # We want to sort within category of court

    return courts

def save_courts_to_file():
    ''' Writes all courts to .json files in Playground data sources folder'''
    courts = [
        [
            'juvenile_courts', 'https://www.mass.gov/orgs/juvenile-court/locations'
        ],
        [
            'probate_and_family_courts', 'https://www.mass.gov/orgs/probate-and-family-court/locations'
        ], 
        [
            'district_courts', 'https://www.mass.gov/orgs/district-court/locations'
        ],
        [
            'housing_courts', 'https://www.mass.gov/orgs/housing-court/locations'
        ],
        [
            'bmc', 'https://www.mass.gov/orgs/boston-municipal-court/locations'
        ],
        [
            'superior_courts', 'https://www.mass.gov/orgs/superior-court/locations'
        ],
        [
            'land_court', 'https://www.mass.gov/orgs/land-court/locations'
        ]
    ]
    sources = PlaygroundSection('sources')
    for court in courts:
        jdata = json.dumps(get_courts_from_massgov_url(court[1]))
        sources.write_file(court[0] + '.json', jdata, binary=True)
        
    # for court in courts: 
    #     #area = PlaygroundSection('sources').get_area()
    #     fpath = os.path.join(sources.directory, court[0] + '.json')
    #     jdata = text_type(json.dumps(get_courts_from_massgov_url(court[1])))
    #     f = open(fpath, 'w')
    #     f.write(jdata)
    #     f.close()
    #sources.finalize()

def test_write():
    area = PlaygroundSection('sources').get_area()
    fpath = os.path.join(area.directory, "test" + '.json')
    jdata = "test"
    f = open(fpath, 'w')
    f.write(jdata)
    f.close()
    area.finalize()
    return fpath

class MACourt(Court):
    def init(self, *pargs, **kwargs):
        super(MACourt, self).init(*pargs, **kwargs)
        if 'address' not in kwargs:
            self.initializeAttribute('address', Address)
        if 'jurisdiction' not in kwargs:
            self.jurisdiction = list()
        if 'location' not in kwargs:
            self.initializeAttribute('location', LatitudeLongitude)

    def __unicode__(self):
        return text_type(self.name)

    def __str__(self):
        return self.__unicode__().encode('utf-8') if PY2 else self.name     

class MACourtList(DAList):
    """Represents a list of courts in Massachusetts. Package includes a cached list that is scraped from mass.gov"""
    def init(self, *pargs, **kwargs):
        super(MACourtList, self).init(*pargs, **kwargs)
        self.auto_gather = False
        self.gathered = True
        self.object_type = MACourt
        if hasattr(self,'courts'):
            if isinstance(self.courts, list):
                self.load_courts(courts=self.courts)
            elif self.courts is True:
                self.load_courts()

    def load_courts(self, courts=['housing_courts','bmc','district_courts','superior_courts'], data_path='docassemble.MACourts:data/sources/'):
        """Load a set of courts into the MACourtList. Courts should be a list of names of JSON files in the data/sources directory.
        Will fall back on loading courts directly from MassGov if the cached file doesn't exist. Available courts: district_courts, housing_courts,bmc,superior_courts,land_court,juvenile_courts,probate_and_family_courts"""
        try:
            for court in courts:
                self.load_courts_from_file(court, data_path=data_path)
        except IOError:
            for court in courts:
                self.load_courts_from_massgov_by_filename(court)

    def load_courts_from_massgov_by_filename(self, filename):
        urls = {
            'district_courts': 'https://www.mass.gov/orgs/district-court/locations',
            'housing_courts': 'https://www.mass.gov/orgs/housing-court/locations',
            'bmc': 'https://www.mass.gov/orgs/boston-municipal-court/locations',
            'superior_courts': 'https://www.mass.gov/orgs/superior-court/locations',
            'land_court': 'https://www.mass.gov/orgs/land-court/locations',
            'juvenile_courts': 'https://www.mass.gov/orgs/juvenile-court/locations',
            'probate_and_family_courts': 'https://www.mass.gov/orgs/probate-and-family-court/locations'
            }

        courts = get_courts_from_massgov_url(urls[filename])
        
        for item in courts:
            # translate the dictionary data into an MACourtList
            court = self.appendObject()
            court.name = item['name']
            court.phone = item['phone']
            court.fax = item['fax']
            court.location.latitude = item['location']['latitude']
            court.location.longitude = item['location']['longitude']
            court.has_po_box = item.get('has_po_box')
            court.description = item.get('description')

            court.address.address = item['address']['address']
            court.address.city.lower() = item['address']['city']
            court.address.state = item['address']['state']
            court.address.zip = item['address']['zip']
            court.address.county.lower() = item['address']['county']
            court.address.orig_address = item['address'].get('orig_address')            
        
    def load_courts_from_file(self, json_path, data_path='docassemble.MACourts:data/sources/'):
        """Add the list of courts at the specified JSON file into the current list"""

        path = path_and_mimetype(os.path.join(data_path,json_path+'.json'))[0]

        with open(path) as courts_json:
            courts = json.load(courts_json)

        for item in courts:
            # translate the dictionary data into an MACourtList

            court = self.appendObject()
            court.name = item['name']
            court.phone = item['phone']
            court.fax = item['fax']
            court.location.latitude = item['location']['latitude']
            court.location.longitude = item['location']['longitude']
            court.has_po_box = item.get('has_po_box')
            court.description = item.get('description')

            court.address.address = item['address']['address']
            court.address.city.lower() = item['address']['city']
            court.address.state = item['address']['state']
            court.address.zip = item['address']['zip']
            court.address.county.lower() = item['address']['county']
            court.address.orig_address = item['address'].get('orig_address')

    def matching_housing_court(self, address):
        """Return the MACourt representing the Housing Court serving the given address""" 
        court_name = self.matching_housing_court_name(address)
        return next ((court for court in self.elements if court.name.rstrip().lower() == court_name.lower()), None)

    def matching_housing_court_name(self,address):
        """Returns the name of the MACourt representing the housing court that covers the specified address.
        Harcoded and must be updated if court jurisdictions or names change. Address must specify county attribute"""
        if (not hasattr(address, 'county')) or (address_to_compare.county.lower().strip() == ''):
            return ''
        if hasattr(address, 'norm') and hasattr(address.norm, 'city') and hasattr(address.norm, 'county'):
            address_to_compare = address.norm
        else:
            address_to_compare = address
        if (address_to_compare.county.lower() == "suffolk county") or (address_to_compare.city.lower() in ["newton","brookline"]):
            local_housing_court = "Eastern Housing Court"
        elif address_to_compare.city.lower() in ["arlington","belmont","cambridge","medford","somerville"]:
            local_housing_court = "Eastern Housing Court - Middlesex Session"
        elif address_to_compare.city.lower() in ["ashfield", "bernardston", "buckland", "charlemont", "colrain", "conway", "deerfield", "erving", "gill", "greenfield", "hawley", "heath", "leverett", "leyden", "monroe", "montague", "new salem", "northfield", "orange", "rowe", "shelburne", "shutesbury", "sunderland", "warwick", "wendell", "whately"]:
            local_housing_court = "Western Housing Court - Greenfield Session"
        elif address_to_compare.city.lower() in ['amherst', 'belchertown', 'chesterfield', 'cummington', 'easthampton', 'goshen', 'granby', 'hadley', 'hatfield', 'huntington', 'middlefield', 'northampton', 'pelham', 'plainfield', 'south hadley', 'southampton', 'ware', 'westhampton', 'williamsburg','worthington']:
            local_housing_court = "Western Housing Court - Hadley Session"
        elif address_to_compare.county.lower() == "berkshire":
            local_housing_court = "Western Housing Court - Pittsfield Session"
        elif address_to_compare.city.lower() in ['agawam', 'blandford', 'brimfield', 'chester', 'chicopee', 'east longmeadow', 'granville', 'hampden', 'holland', 'holyoke', 'longmeadow', 'ludlow', 'monson', 'montgomery', 'palmer', 'russell', 'southwick', 'springfield', 'tolland', 'wales', 'west springfield', 'westfield','wilbraham']:
            local_housing_court = "Western Housing Court - Springfield Session"
        elif address_to_compare.city.lower() in ['charlton', 'dudley', 'oxford', 'southbridge', 'sturbridge', 'webster']:
            local_housing_court ="Central Housing Court - Dudley Session"
        elif address_to_compare.city.lower() in ['ashburnham', 'athol', 'fitchburg', 'gardner', 'holden', 'hubbardston', 'leominster', 'lunenberg', 'petersham', 'phillipston', 'princeton', 'royalston', 'templeton', 'westminster', 'winchendon']:
            local_housing_court = "Central Housing Court - Leominster Session"
        elif address_to_compare.city.lower() in ['ashland', 'berlin', 'bolton', 'framingham', 'harvard', 'holliston', 'hopkinton', 'hudson', 'marlborough', 'natick', 'northborough', 'sherborn', 'southborough', 'sudbury', 'wayland', 'westborough']:
            local_housing_court = "Central Housing Court - Marlborough Session"
        elif address_to_compare.city.lower() in ['auburn', 'barre', 'bellingham', 'blackstone', 'boylston', 'brookfield', 'clinton', 'douglas', 'east brookfield', 'grafton', 'hardwick', 'hopedale', 'lancaster', 'leicester', 'mendon', 'milford', 'millbury', 'millville', 'new braintree', 'northbridge', 'north brookfield', 'oakham', 'oxford', 'paxton', 'rutland', 'shrewsbury', 'spencer', 'sterling', 'sutton', 'upton', 'uxbridge', 'warren', 'west boylston', 'worcester']:
            local_housing_court = "Central Housing Court - Worcester Session"
        elif address_to_compare.city.lower() in ['abington', 'avon', 'bellingham', 'braintree', 'bridgewater', 'brockton', 'canton', 'cohasset', 'dedham', 'dover', 'east bridgewater', 'eastham', 'foxborough', 'franklin', 'holbrook', 'medfield', 'medway', 'millis', 'milton', 'needham', 'norfolk', 'norwood', 'plainville', 'quincy', 'randolph', 'sharon', 'stoughton', 'walpole', 'wellesley', 'west bridgewater', 'westwood', 'weymouth', 'whitman', 'wrentham']:
            local_housing_court = "Metro South Housing Court - Brockton Session"
        elif address_to_compare.county.lower() == "norfolk county" and not address_to_compare.city.lower() in ["newton","brookline"]:
            local_housing_court = "Metro South Housing Court - Canton Session"
        elif address_to_compare.city.lower() in ['amesbury', 'andover', 'boxford', 'georgetown', 'groveland', 'haverhill', 'lawrence', 'merrimac', 'methuen', 'newbury', 'newburyport', 'north andover', 'rowley', 'salisbury', 'west newbury']:
            local_housing_court =  "Northeast Housing Court - Lawrence Session"
        elif address_to_compare.city.lower() in ['acton', 'ashby', 'ayer', 'billerica', 'boxborough', 'carlisle', 'chelmsford', 'devens', 'dracut', 'dunstable', 'groton', 'littleton', 'lowell', 'maynard', 'pepperell', 'shirley', 'stow', 'tewksbury', 'townsend', 'tyngsborough', 'westford']:
            local_housing_court = "Northeast Housing Court - Lowell Session"
        elif address_to_compare.city.lower() in ['lynn', 'nahant', 'saugus']:
            local_housing_court = "Northeast Housing Court - Lynn Session"
        elif address_to_compare.city.lower() in ['beverly', 'danvers', 'essex', 'gloucester', 'hamilton', 'ipswich', 'lynnfield', 'manchester-by-the-sea', 'marblehead', 'middleton', 'peabody', 'rockport', 'salem', 'swampscott', 'topsfield', 'wenham']:
            local_housing_court = "Northeast Housing Court - Salem Session"
        elif address_to_compare.city.lower() in ['bedford', 'burlington', 'concord', 'everett','lexington', 'lincoln', 'malden', 'melrose', 'north reading', 'reading', 'stoneham', 'wakefield', 'waltham', 'watertown', 'weston', 'wilmington', 'winchester', 'woburn']:
            local_housing_court = "Northeast Housing Court - Woburn Session"
        elif address_to_compare.city.lower() in ['freetown', 'westport', 'fall river', 'somerset','swansea']:
            local_housing_court = "Southeast Housing Court - Fall River Session"
        elif address_to_compare.city.lower() in ['acushnet', 'dartmouth', 'fairhaven', 'freetown', 'new bedford','westport']:
            local_housing_court = "Southeast Housing Court - New Bedford Session"
        elif address_to_compare.city.lower() in ['aquinnah', 'barnstable', 'bourne', 'brewster', 'carver', 'chatham', 'chilmark', 'dennis', 'duxbury', 'edgartown', 'falmouth', 'halifax', 'hanson', 'harwich', 'kingston', 'lakeville', 'marion', 'marshfield', 'mashpee', 'mattapoisett', 'middleborough', 'nantucket', 'oak bluffs', 'pembroke', 'plymouth', 'plympton', 'provincetown', 'rochester', 'sandwich', 'and wareham.beginning on august 6', 'the plymouth session of the southeast housing court will also serve accord', 'assinippi', 'hanover', 'hingham', 'hull', 'humarock', 'norwell', 'rockland', 'scituate']:
            local_housing_court = "Southeast Housing Court - Plymouth Session"
        elif address_to_compare.city.lower() in ['attleboro', 'berkley', 'dighton', 'easton', 'mansfield', 'north attleborough', 'norton', 'raynham', 'rehoboth', 'seekonk','taunton']:
            local_housing_court = "Southeast Housing Court - Taunton Session"
        else:
            local_housing_court = ""
        return local_housing_court


if __name__ == '__main__':
    import pprint
    courts = get_courts_from_massgov_url('https://www.mass.gov/orgs/district-court/locations')
    pprint.pprint(courts)