#!/usr/bin/env python
"""jss.py

Python wrapper for JSS API.
Copyright (C) 2014 Shea G Craig <shea.craig@da.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from xml.etree import ElementTree
from xml.parsers.expat import ExpatError
import os
import re
import copy
import subprocess

from .contrib import requests
try:
    from .contrib import FoundationPlist
except ImportError as e:
    if os.uname()[0] == 'Darwin':
        print("Warning: Import of FoundationPlist failed: %s" % e)
        print("See README for information on this issue.")
    import plistlib


class JSSPrefsMissingFileError(Exception):
    pass


class JSSPrefsMissingKeyError(Exception):
    pass


class JSSGetError(Exception):
    pass


class JSSPutError(Exception):
    pass


class JSSPostError(Exception):
    pass


class JSSDeleteError(Exception):
    pass


class JSSMethodNotAllowedError(Exception):
    pass


class JSSUnsupportedSearchMethodError(Exception):
    pass


class JSSPrefs(object):
    """Uses the OS X preferences system to store credentials and JSS URL."""
    def __init__(self, preferences_file=None):
        """Create a preferences object.

        preferences_file: Alternate location to look for preferences.

        Preference file should include the following keys:
            jss_url:        Full path, including port, to JSS,
                            e.g. 'https://mycasper.donkey.com:8443'
                            (JSS() handles the appending of /JSSResource)
            jss_user:       API username to use.
            jss_password:   API password.

        """
        if preferences_file is None:
            preferences_file = '~/Library/Preferences/com.github.sheagcraig.python-jss.plist'
        preferences_file = os.path.expanduser(preferences_file)
        if os.path.exists(preferences_file):
            try:
                prefs = FoundationPlist.readPlist(preferences_file)
            except NameError:
                # Plist files are probably not binary on non-OS X machines, so
                # this should be safe.
                try:
                    prefs = plistlib.readPlist(preferences_file)
                except ExpatError:
                    subprocess.call(['plutil', '-convert', 'xml1', preferences_file])
                    prefs = plistlib.readPlist(preferences_file)
            try:
                self.user = prefs['jss_user']
                self.password = prefs['jss_pass']
                self.url = prefs['jss_url']
            except KeyError:
                raise JSSPrefsMissingKeyError("Please provide all required"
                                              " preferences!")
        else:
            raise JSSPrefsMissingFileError("Preferences file not found!")


class JSS(object):
    """Connect to a JSS and handle API requests."""
    def __init__(self, jss_prefs=None, url=None, user=None, password=None,
                 ssl_verify=True, verbose=False):
        """Provide either a JSSPrefs object OR specify url, user, and password
        to init.

        jss_prefs:  A JSSPrefs object.
        url:        Path with port to a JSS. See JSSPrefs.__doc__
        user:       API Username.
        password:   API Password.
        ssl_verify: Boolean indicating whether to verify SSL certificates.
                    Defaults to True.

        """
        if jss_prefs is not None:
            url = jss_prefs.url
            user = jss_prefs.user
            password = jss_prefs.password

        self._url = '%s/JSSResource' % url
        self.user = user
        self.password = password
        self.ssl_verify = ssl_verify
        self.verbose = verbose
        self.factory = JSSObjectFactory(self)
        self.session = requests.Session()
        self.session.auth = (self.user, self.password)
        self.session.verify = self.ssl_verify
        headers = {"content-type": 'text/xml', 'Accept': 'application/xml'}
        self.session.headers.update(headers)

    def _error_handler(self, exception_cls, response):
        """Generic error handler. Converts html responses to friendlier
        text.

        """
        # Responses are sent as html. Split on the newlines and give us the
        # <p> text back.
        errorlines = response.text.encode('utf-8').split('\n')
        error = []
        for line in errorlines:
            e = re.search(r'<p.*>(.*)</p>', line)
            if e:
                error.append(e.group(1))

        error = '\n'.join(error)
        raise exception_cls('JSS ERROR. Response Code: %s\tResponse: %s' %
                          (response.status_code, error))

    def get(self, url):
        """Get a url, handle errors, and return an etree from the XML data."""
        # For some objects the JSS tries to return JSON if we don't specify
        # that we want XML.
        url = '%s%s' % (self._url, url)
        response = self.session.get(url)

        if response.status_code == 200:
            if self.verbose:
                print("GET: Success.")
        elif response.status_code >= 400:
            self._error_handler(JSSGetError, response)

        # JSS returns xml encoded in utf-8
        jss_results = response.text.encode('utf-8')
        try:
            xmldata = ElementTree.fromstring(jss_results)
        except ElementTree.ParseError:
            raise JSSGetError("Error Parsing XML:\n%s" % jss_results)
        return xmldata

    def post(self, obj_class, url, data):
        """Post an object to the JSS. For creating new objects only."""
        # The JSS expects a post to ID 0 to create an object
        url = '%s%s' % (self._url, url)
        data = ElementTree.tostring(data)
        response = self.session.post(url, data=data)

        if response.status_code == 201:
            if self.verbose:
                print("POST: Success")
        elif response.status_code >= 400:
            self._error_handler(JSSPostError, response)

        # Get the ID of the new object. JSS returns xml encoded in utf-8
        jss_results = response.text.encode('utf-8')
        id_ =  int(re.search(r'<id>([0-9]+)</id>', jss_results).group(1))

        return self.factory.get_object(obj_class, id_)

    def put(self, url, data):
        """Updates an object on the JSS."""
        url = '%s%s' % (self._url, url)
        data = ElementTree.tostring(data)
        response = self.session.put(url, data)

        if response.status_code == 201:
            if self.verbose:
                print("PUT: Success.")
        elif response.status_code >= 400:
            self._error_handler(JSSPutError, response)

    def delete(self, url):
        """Delete an object from the JSS."""
        url = '%s%s' % (self._url, url)
        response = self.session.delete(url)

        if response.status_code == 200:
            if self.verbose:
                print("DEL: Success.")
        elif response.status_code >= 400:
            self._error_handler(JSSDeleteError, response)

    # Constructor methods for all JSSObject types #############################

    def Account(self, data=None):
        return self.factory.get_object(Account, data)

    def AccountGroup(self, data=None):
        return self.factory.get_object(AccountGroup, data)

    def AdvancedComputerSearch(self, data=None):
        return self.factory.get_object(AdvancedComputerSearch, data)

    def AdvancedMobileDeviceSearch(self, data=None):
        return self.factory.get_object(AdvancedMobileDeviceSearch, data)

    def AdvancedUserSearch(self, data=None):
        return self.factory.get_object(AdvancedUserSearch, data)

    def ActivationCode(self, data=None):
        return self.factory.get_object(ActivationCode, data)

    def Building(self, data=None):
        return self.factory.get_object(Building, data)

    def Category(self, data=None):
        return self.factory.get_object(Category, data)

    def Class(self, data=None):
        return self.factory.get_object(Class, data)

    def Computer(self, data=None):
        return self.factory.get_object(Computer, data)

    def ComputerCheckIn(self, data=None):
        return self.factory.get_object(ComputerCheckIn, data)

    def ComputerCommand(self, data=None):
        return self.factory.get_object(ComputerCommand, data)

    def ComputerExtensionAttribute(self, data=None):
        return self.factory.get_object(ComputerExtensionAttribute, data)

    def ComputerGroup(self, data=None):
        return self.factory.get_object(ComputerGroup, data)

    def ComputerInventoryCollection(self, data=None):
        return self.factory.get_object(ComputerInventoryCollection, data)

    def ComputerInvitation(self, data=None):
        return self.factory.get_object(ComputerInvitation, data)

    def ComputerReport(self, data=None):
        return self.factory.get_object(ComputerReport, data)

    def Department(self, data=None):
        return self.factory.get_object(Department, data)

    def DirectoryBinding(self, data=None):
        return self.factory.get_object(DirectoryBinding, data)

    def DiskEncryptionConfiguration(self, data=None):
        return self.factory.get_object(DiskEncryptionConfiguration, data)

    def DistributionPoint(self, data=None):
        return self.factory.get_object(DistributionPoint, data)

    def DockItem(self, data=None):
        return self.factory.get_object(DockItem, data)

    def EBook(self, data=None):
        return self.factory.get_object(EBook, data)

    #def FileUpload(self, data=None):
    #    return self.factory.get_object(FileUpload, data)

    def GSXConnection(self, data=None):
        return self.factory.get_object(GSXConnection, data)

    def JSSUser(self, data=None):
        return self.factory.get_object(JSSUser, data)

    def LDAPServer(self, data=None):
        return self.factory.get_object(LDAPServer, data)

    def LicensedSoftware(self, data=None):
        return self.factory.get_object(LicensedSoftware, data)

    def ManagedPreferenceProfile(self, data=None):
        return self.factory.get_object(ManagedPreferenceProfile, data)

    def MobileDevice(self, data=None):
        return self.factory.get_object(MobileDevice, data)

    def MobileDeviceApplication(self, data=None):
        return self.factory.get_object(MobileDeviceApplication, data)

    def MobileDeviceCommand(self, data=None):
        return self.factory.get_object(MobileDeviceCommand, data)

    def MobileDeviceConfigurationProfile(self, data=None):
        return self.factory.get_object(MobileDeviceConfigurationProfile, data)

    def MobileDeviceEnrollmentProfile(self, data=None):
        return self.factory.get_object(MobileDeviceEnrollmentProfile, data)

    def MobileDeviceExtensionAttribute(self, data=None):
        return self.factory.get_object(MobileDeviceExtensionAttribute, data)

    def MobileDeviceInvitation(self, data=None):
        return self.factory.get_object(MobileDeviceInvitation, data)

    def MobileDeviceGroup(self, data=None):
        return self.factory.get_object(MobileDeviceGroup, data)

    def MobileDeviceProvisioningProfile(self, data=None):
        return self.factory.get_object(MobileDeviceProvisioningProfile, data)

    def NetbootServer(self, data=None):
        return self.factory.get_object(NetbootServer, data)

    def NetworkSegment(self, data=None):
        return self.factory.get_object(NetworkSegment, data)

    def OSXConfigurationProfile(self, data=None):
        return self.factory.get_object(OSXConfigurationProfile, data)

    def Package(self, data=None):
        return self.factory.get_object(Package, data)

    def Peripheral(self, data=None):
        return self.factory.get_object(Peripheral, data)

    def PeripheralType(self, data=None):
        return self.factory.get_object(PeripheralType, data)

    def Policy(self, data=None):
        return self.factory.get_object(Policy, data)

    def Printer(self, data=None):
        return self.factory.get_object(Printer, data)

    def RestrictedSfotware(self, data=None):
        return self.factory.get_object(RestrictedSoftware, data)

    def RemovableMACAddress(self, data=None):
        return self.factory.get_object(RemovableMACAddress, data)

    def SavedSearch(self, data=None):
        return self.factory.get_object(SavedSearch, data)

    def Script(self, data=None):
        return self.factory.get_object(Script, data)

    def Site(self, data=None):
        return self.factory.get_object(Site, data)

    def SoftwareUpdateServer(self, data=None):
        return self.factory.get_object(SoftwareUpdateServer, data)

    def SMTPServer(self, data=None):
        return self.factory.get_object(SMTPServer, data)

    def UserExtensionAttribute(self, data=None):
        return self.factory.get_object(UserExtensionAttribute, data)

    def User(self, data=None):
        return self.factory.get_object(User, data)

    def UserGroup(self, data=None):
        return self.factory.get_object(UserGroup, data)


class XMLEditor(object):
    """XMLEditor provides convenient methods for manipulating XML data.

    It is used as an abstract class from which we subclass JSSObjects and
    JSSObjectTemplates.

    XMLEditors can be subclassed to provide wrappers for these methods to
    further enable context-class-specific behavior.

    I use multiple-inheritance rather than composition here to avoid multiple
    dot sequences in calls.

    NOTE: XMLEditor has no ElementTree, so on its own, its methods will fail!

    """

    # There are some ElementTree.Element methods in here. As XMLEditor is an
    # abstract class to be inherited by classes which also inherit Element,
    # this works, although it's not very clear.

    def _indent(self, elem, level=0, more_sibs=False):
        """Indent an xml element object to prepare for pretty printing.

        Method is internal to discourage indenting the self._root Element,
        thus potentially corrupting it.

        """
        i = "\n"
        pad = '    '
        if level:
            i += (level - 1) * pad
        num_kids = len(elem)
        if num_kids:
            if not elem.text or not elem.text.strip():
                elem.text = i + pad
                if level:
                    elem.text += pad
            count = 0
            for kid in elem:
                self._indent(kid, level+1, count < num_kids - 1)
                count += 1
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
                if more_sibs:
                    elem.tail += pad
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                if more_sibs:
                    elem.tail += pad

    def __repr__(self):
        """Make our data human readable."""
        # deepcopy so we don't mess with the valid XML.
        pretty_data = copy.deepcopy(self)
        self._indent(pretty_data)
        elementstring = ElementTree.tostring(pretty_data)
        return elementstring.encode('utf-8')

    def _handle_location(self, location):
        """Return an element located at location.

        Handles a string xpath as per ElementTree.find or an element.

        """
        if not isinstance(location, ElementTree.Element):
            element = self.find(location)
            if element is None:
                raise ValueError("Invalid path!")
        else:
            element = location
        return element

    def search(self, tag):
        """Return elements with tag using getiterator."""
        return self.getiterator(tag)

    def set_bool(self, location, value):
        """For an object at path, set the string representation of a boolean
        value to value. Mostly just to prevent me from forgetting to convert
        to string.

        """
        element = self._handle_location(location)
        if bool(value) == True:
            element.text = 'true'
        else:
            element.text = 'false'

    def add_object_to_path(self, obj, location):
        """Add an object of type JSSContainerObject to XMLEditor's context
        object at "path".

        location can be an Element or a string path argument to find()

        """
        location = self._handle_location(location)
        location.append(obj.as_list_data())

    def remove_object_from_list(self, obj, list_element):
        """Remove an object from a list element.

        object:     Accepts JSSObjects, id's, and names
        list:   Accepts an element or a string path to that element

        """
        list_element = self._handle_location(list_element)

        if isinstance(object, JSSObject):
            results = [item for item in list_element.getchildren() if
                       item.findtext("id") == obj.id]
        elif type(obj) in [int, str, unicode]:
            results = [item for item in list_element.getchildren() if
                       item.findtext("id") == str(obj) or
                       item.findtext("name") == obj]

        if len(results) == 1 :
            list_element.remove(results[0])
        else:
            raise ValueError("There is either more than one object, or no "
                             "matches at that path!")

    def clear_list(self, list_element):
        """Clear all list items from path.

        list_element can be a string argument to find(), or an element.

        """
        list_element = self._handle_location(list_element)
        list_element.clear()


class GroupEditor(XMLEditor):
    """Abstract XMLEditor for ComputerGroup and MobileDeviceGroup."""
    def add_criterion(self, name, priority, and_or, search_type, value):
        """Add a search criteria object to a smart group."""
        criterion = SearchCriteria(name, priority, and_or, search_type, value)
        self.criteria.append(criterion)

    def set_is_smart(self, value):
        """Set whether a group is smart or not."""
        self.set_bool("is_smart", value)
        if value is True:
            if self.find("criteria") is None:
                self.criteria = ElementTree.SubElement(self, "criteria")

    def add_device(self, device, container):
        """Add a device to a group. Wraps XMLEditor.add_object_toPath.

        device can be a JSSObject, and ID value, or the name of a valid
        object.

        """
        # There is a size tag which the JSS manages for us, so we can ignore
        # it.
        if self.findtext("is_smart") == 'false':
            self.add_object_to_path(device, container)
        else:
            # Technically this isn't true. It will strangely accept them, and
            # they even show up as members of the group!
            raise ValueError("Devices may not be added to smart groups.")


class ComputerGroupEditor(GroupEditor):
    """Add methods for ComputerGroups."""
    def add_computer(self, device):
        """Add a computer to the group."""
        super(ComputerGroupEditor, self).add_device(device, "computers")

    def remove_computer(self, device):
        """Remove a computer from the group."""
        super(ComputerGroupEditor, self).remove_object_from_list(device,
                                                                 "computers")


class MobileDeviceGroupEditor(GroupEditor):
    """Add methods for MobileDeviceGroups."""
    def add_mobile_device(self, device):
        """Add a mobile_device to the group."""
        super(MobileDeviceGroupEditor, self).add_device(device,
                                                        "mobile_devices")

    def remove_mobile_device(self, device):
        """Remove a mobile_device from the group."""
        super(MobileDeviceGroupEditor, self).remove_object_from_list(device,
                "mobile_devices")


class PolicyEditor(XMLEditor):
    """Adds methods for manipulating common Policy elements."""
    def add_object_to_scope(self, obj):
        """Add an object 'obj' to the appropriate scope block."""
        if isinstance(obj, Computer):
            self.add_object_to_path(obj, "scope/computers")
        elif isinstance(obj, ComputerGroup):
            self.add_object_to_path(obj, "scope/computer_groups")
        elif isinstance(obj, Building):
            self.add_object_to_path(obj, "scope/buildings")
        elif isinstance(obj, Department):
            self.add_object_to_path(obj, "scope/departments")
        else:
            raise TypeError

    def clear_scope(self):
        """Clear all objects from the scope, including exclusions."""
        clear_list = ["computers", "computer_groups", "buildings",
                      "departments", "limit_to_users/user_groups",
                      "limitations/users", "limitations/user_groups",
                     "limitations/network_segments", "exclusions/computers",
                     "exclusions/computer_groups", "exclusions/buildings",
                     "exclusions/departments", "exclusions/users",
                     "exclusions/user_groups", "exclusions/network_segments"]
        for section in clear_list:
            self.clear_list("%s%s" % ("scope/", section))


    def add_object_to_exclusions(self, obj):
        """Add an object 'obj' to the appropriate scope exclusions block.

        obj should be an instance of Computer, ComputerGroup, Building,
        or Department.

        """
        if isinstance(obj, Computer):
            self.add_object_to_path(obj, "scope/exclusions/computers")
        elif isinstance(obj, ComputerGroup):
            self.add_object_to_path(obj, "scope/exclusions/computer_groups")
        elif isinstance(obj, Building):
            self.add_object_to_path(obj, "scope/exclusions/buildings")
        elif isinstance(obj, Department):
            self.add_object_to_path(obj, "scope/exclusions/departments")
        else:
            raise TypeError

    def add_package(self, pkg):
        """Add a jss.Package object to the policy with action=install.

        obj should be an instance of Computer, ComputerGroup, Building,
        or Department.

        """
        if isinstance(pkg, Package):
            self.add_object_to_path(pkg, "package_configuration/packages")
            package = ElementTree.Element("package")
            id_ = ElementTree.SubElement(package, "id")
            id_.text = pkg.id
            name = ElementTree.SubElement(package, "name")
            name.text = pkg.name
            action = ElementTree.SubElement(package, "action")
            action.text = "Install"

    def set_self_service(self, state=True):
        """Convenience setter for self_service."""
        self.set_bool(self.find("self_service/use_for_self_service"), state)

    def set_recon(self, state=True):
        """Convenience setter for recon."""
        self.set_bool(self.find("maintenance/recon"), state)

    def set_category(self, category):
        """Set the policy's category.

        category should be a category object.

        """
        pcategory = self.find("general/category")
        pcategory.clear()
        id_ = ElementTree.SubElement(pcategory, "id")
        id_.text = category.id
        name = ElementTree.SubElement(pcategory, "name")
        name.text = category.name


class PackageEditor(XMLEditor):
    """Editor methods for Packages."""
    def set_os_requirements(self, requirements):
        """Sets package OS Requirements. Pass in a string of comma seperated
        OS versions. A lowercase 'x' is allowed as a wildcard, e.g. '10.9.x'

        """
        self.find("os_requirements").text = requirements

    def set_category(self, category):
        """Sets package category to 'category', which can be a string of an
        existing category's name, or a Category object.

        """
        # For some reason, packages only have the category name, not the ID.
        if isinstance(category, Category):
            name = category.name
        else:
            name = category
        self.find("category").text = name


class JSSObjectFactory(object):
    """Create JSSObjects intelligently based on a single data argument."""
    def __init__(self, jss):
        self.jss = jss

    def get_object(self, obj_class, data=None):
        """Return a subclassed JSSObject instance by querying for existing
        objects or posting a new object. List operations return a
        JSSObjectList.

        obj_class is the class to retrieve.
        data is flexible.
            If data is type:
                None:   Perform a list operation, or for non-container objects,
                        return all data.
                int:    Retrieve an object with ID of <data>
                str:    Retrieve an object with name of <str>. For some
                        objects, this may be overridden to include searching
                        by other criteria. See those objects for more info.
                dict:   Get the existing object with <dict>['id']
                xml.etree.ElementTree.Element:    Create a new object from xml

                Warning! Be sure to pass ID's as ints, not str!

        """
        # List objects
        if data is None:
            url = obj_class.get_url(data)
            if obj_class.can_list and obj_class.can_get:
                result = self.jss.get(url)
                if obj_class.container:
                    result = result.find(obj_class.container)
                response_objects = [item for item in result if item is not None
                                    and item.tag != 'size']
                objects = [JSSListData(obj_class,
                                       {i.tag: i.text for i
                                        in response_object})
                           for response_object in response_objects]

                return JSSObjectList(self, obj_class, objects)
            elif obj_class.can_get:
                # Single object
                xmldata = self.jss.get(url)
                return obj_class(self.jss, xmldata)
            else:
                raise JSSMethodNotAllowedError(obj_class.__class__.__name__)
        # Retrieve individual objects
        elif type(data) in [str, int, unicode]:
            if obj_class.can_get:
                url = obj_class.get_url(data)
                xmldata = self.jss.get(url)
                if xmldata.find('size') is not None:
                    # May need above treatment, with .find(container), and
                    # refactoring out this otherwise duplicate code.

                    # Get returned a list.
                    response_objects = [item for item in xmldata
                                        if item is not None and
                                        item.tag != 'size']
                    objects = [JSSListData(obj_class,
                                           {i.tag: i.text for i
                                            in response_object})
                               for response_object in response_objects]

                    return JSSObjectList(self, obj_class, objects)
                else:
                    return obj_class(self.jss, xmldata)
            else:
                raise JSSMethodNotAllowedError(obj_class.__class__.__name__)
        # Create a new object
        elif isinstance(data, JSSObjectTemplate):
            if obj_class.can_post:
                url = obj_class.get_post_url()
                return self.jss.post(obj_class, url, data)
            else:
                raise JSSMethodNotAllowedError(obj_class.__class__.__name__)


class JSSObject(ElementTree.Element):
    """Base class for representing all available JSS API objects.

    """
    _url = None
    can_list = True
    can_get = True
    can_put = True
    can_post = True
    can_delete = True
    id_url = '/id/'
    container = ''
    default_search = 'name'
    search_types = {'name': '/name/'}

    def __init__(self, jss, data):
        """Initialize a new JSSObject

        jss:    JSS object.
        data:   Valid XML.

        """
        self.jss = jss
        if not isinstance(data, ElementTree.Element):
            raise TypeError("JSSObjects data argument must be of type "
                            "xml.etree.ElemenTree.Element")
        super(JSSObject, self).__init__(tag=data.tag)
        for child in data.getchildren():
            self.append(child)

    def makeelement(self, tag, attrib):
        """Return an Element."""
        # We use ElementTree.SubElement() a lot. Unfortunately, it relies on a
        # super() call to its __class__.makeelement(), which will fail due to
        # the method resolution order / multiple inheritence of our objects
        #(they have an editor AND a template or JSSObject parent class).
        # This handles that issue.
        return ElementTree.Element(tag, attrib)

    @classmethod
    def get_url(cls, data):
        """Return the URL for a get request based on data type."""
        # Test for a string representation of an integer
        try:
            data = int(data)
        except (ValueError, TypeError):
            pass
        if isinstance(data, int):
            return '%s%s%s' % (cls._url, cls.id_url, data)
        elif data is None:
            return cls._url
        else:
            if '=' in data:
                key, value = data.split('=')
                if key in cls.search_types:
                    return '%s%s%s' % (cls._url, cls.search_types[key], value)
                else:
                    raise JSSUnsupportedSearchMethodError("This object cannot"
                            "be queried by %s." % key)
            else:
                return '%s%s%s' % (cls._url,
                                   cls.search_types[cls.default_search], data)

    @classmethod
    def get_post_url(cls):
        """Return the post URL for this object class."""
        return '%s%s%s' % (cls._url, cls.id_url, '0')

    def get_object_url(self):
        """Return the complete API url to this object."""
        return '%s%s%s' % (self._url, self.id_url, self.id)

    def delete(self):
        """Delete this object from the JSS."""
        if not self.can_delete:
            raise JSSMethodNotAllowedError(self.__class__.__name__)
        self.jss.delete(self.get_object_url())

    def update(self):
        """Update this object on the JSS.

        Data validation is up to the client.

        """
        if not self.can_put:
            raise JSSMethodNotAllowedError(self.__class__.__name__)

        url = self.get_object_url()
        self.jss.put(url, self)
        self._root = self.jss.get(url)

    # Shared properties:
    # Almost all JSSObjects have at least name and id properties, so provide a
    # convenient accessor.
    @property
    def name(self):
        """Return object name or None."""
        return self.findtext('name') or \
                    self.findtext('general/name')

    @property
    def id(self):
        """Return object ID or None."""
        # Most objects have ID nested in general. Groups don't.
        result = self.findtext('id') or self.findtext('general/id')
        # After much consideration, I will treat id's as strings.
        #   We can't assign ID's, so there's no need to perform arithmetic on
        #   them.
        #   Having to convert to str all over the place is gross.
        #   str equivalency still works.
        return result


class JSSContainerObject(JSSObject):
    """Subclass for object types which can contain lists.

    e.g. Computers, Policies.

    """
    list_type = 'JSSContainerObject'

    def as_list_data(self):
        """Return an Element with id and name data for adding to lists."""
        element = ElementTree.Element(self.list_type)
        id_ = ElementTree.SubElement(element, "id")
        id_.text = self.id
        name = ElementTree.SubElement(element, "name")
        name.text = self.name
        return element


class JSSDeviceObject(JSSContainerObject):
    """Provides convenient accessors for properties of devices.

    This is helpful since Computers and MobileDevices allow us to query
    based on these properties.

    """
    @property
    def udid(self):
        """Return device's UDID or None."""
        return self.findtext('general/udid')

    @property
    def serial_number(self):
        """Return device's serial number or None."""
        return self.findtext('general/serial_number')


class JSSFlatObject(JSSObject):
    """Subclass for JSS objects which do not return a list of objects."""
    search_types = {}

    @classmethod
    def get_url(cls, data):
        """Return the URL for a get request based on data type."""
        if data is not None:
            raise JSSUnsupportedSearchMethodError("This object cannot"
                    "be queried by %s." % data)
        else:
            return cls._url

    def get_object_url(self):
        """Return the complete API url to this object."""
        return self.get_url(None)


class Account(XMLEditor, JSSContainerObject):
    _url = '/accounts'
    container = 'users'
    id_url = '/userid/'
    search_types = {'userid': '/userid/', 'username': '/username/',
                    'name': '/username/'}


class AccountGroup(XMLEditor, JSSContainerObject):
    """Account groups are groups of users on the JSS. Within the API
    hierarchy they are actually part of accounts, but I seperated them.

    """
    _url = '/accounts'
    container = 'groups'
    id_url = '/groupid/'
    search_types = {'groupid': '/groupid/', 'groupname': '/groupname/',
                    'name': '/groupname/'}


class ActivationCode(XMLEditor, JSSFlatObject):
    _url = '/activationcode'
    can_delete = False
    can_post = False
    can_list = False


class AdvancedComputerSearch(XMLEditor, JSSContainerObject):
    _url = '/advancedcomputersearches'


class AdvancedMobileDeviceSearch(XMLEditor, JSSContainerObject):
    _url = '/advancedmobiledevicesearches'


class AdvancedUserSearch(XMLEditor, JSSContainerObject):
    _url = '/advancedusersearches'


class Building(XMLEditor, JSSContainerObject):
    _url = '/buildings'
    list_type = 'building'


class Category(XMLEditor, JSSContainerObject):
    _url = '/categories'


class Class(XMLEditor, JSSContainerObject):
    _url = '/classes'


class Computer(XMLEditor, JSSDeviceObject):
    """Computer objects include a 'match' search type which queries across
    multiple properties.

    """
    list_type = 'computer'
    _url = '/computers'
    search_types = {'name': '/name/', 'serial_number': '/serialnumber/',
                    'udid': '/udid/', 'macaddress': '/macadress/',
                    'match': '/match/'}

    @property
    def mac_addresses(self):
        """Return a list of mac addresses for this device."""
        # Computers don't tell you which network device is which.
        mac_addresses = [self.findtext('general/mac_address')]
        if self.findtext('general/alt_mac_address'):
            mac_addresses.append(self.findtext(\
                    'general/alt_mac_address'))
            return mac_addresses


class ComputerCheckIn(XMLEditor, JSSFlatObject):
    _url = '/computercheckin'
    can_delete = False
    can_list = False
    can_post = False

class ComputerCommand(XMLEditor, JSSContainerObject):
    _url = '/computercommands'
    can_delete = False
    can_put = False


class ComputerExtensionAttribute(XMLEditor, JSSContainerObject):
    _url = '/computerextensionattributes'


class ComputerGroup(ComputerGroupEditor, JSSContainerObject):
    _url = '/computergroups'
    list_type = 'computer_group'


class ComputerInventoryCollection(XMLEditor, JSSFlatObject):
    _url = '/computerinventorycollection'
    can_list = False
    can_post = False
    can_delete = False


class ComputerInvitation(XMLEditor, JSSContainerObject):
    _url = '/computerinvitations'
    can_put = False
    search_types = {'name': '/name/', 'invitation': '/invitation/'}


class ComputerReport(XMLEditor, JSSContainerObject):
    _url = '/computerreports'
    can_put = False
    can_post = False
    can_delete = False


class Department(XMLEditor, JSSContainerObject):
    _url = '/departments'
    list_type = 'department'

class DirectoryBinding(XMLEditor, JSSContainerObject):
    _url = '/directorybindings'


class DiskEncryptionConfiguration(XMLEditor, JSSContainerObject):
    _url = '/diskencryptionconfigurations'


class DistributionPoint(XMLEditor, JSSContainerObject):
    _url = '/distributionpoints'


class DockItem(XMLEditor, JSSContainerObject):
    _url = '/dockitems'


class EBook(XMLEditor, JSSContainerObject):
    _url = '/ebooks'


# Need to think about how to handle this.
#class FileUpload(JSSObject):
#    _url = '/fileuploads'
#    can_put = False
#    can_delete = False
#    can_get = False
#    can_list = False


class GSXConnection(XMLEditor, JSSFlatObject):
    _url = '/gsxconnection'
    can_list = False
    can_post = False
    can_delete = False


class JSSUser(XMLEditor, JSSFlatObject):
    """JSSUser is deprecated."""
    _url = '/jssuser'
    can_list = False
    can_post = False
    can_put = False
    can_delete = False
    search_types = {}


class LDAPServer(XMLEditor, JSSContainerObject):
    _url = '/ldapservers'


class LicensedSoftware(XMLEditor, JSSContainerObject):
    _url = '/licensedsoftware'


class ManagedPreferenceProfile(XMLEditor, JSSContainerObject):
    _url = '/managedpreferenceprofiles'


class MobileDevice(XMLEditor, JSSDeviceObject):
    """Mobile Device objects include a 'match' search type which queries across
    multiple properties.

    """
    _url = '/mobiledevices'
    list_type = 'mobile_device'
    search_types = {'name': '/name/', 'serial_number': '/serialnumber/',
                    'udid': '/udid/', 'macaddress': '/macadress/',
                    'match': '/match/'}

    @property
    def wifi_mac_address(self):
        """Return device's WIFI MAC address or None."""
        return self.findtext('general/wifi_mac_address')

    @property
    def bluetooth_mac_address(self):
        """Return device's Bluetooth MAC address or None."""
        return self.findtext('general/bluetooth_mac_address') or \
                self.findtext('general/mac_address')


class MobileDeviceApplication(XMLEditor, JSSContainerObject):
    _url = '/mobiledeviceapplications'


class MobileDeviceCommand(XMLEditor, JSSContainerObject):
    _url = '/mobiledevicecommands'
    can_put = False
    can_delete = False
    search_types = {'name': '/name/', 'uuid': '/uuid/',
                    'command': '/command/'}
    # TODO: This object _can_ post, but it works a little differently
    can_post = False


class MobileDeviceConfigurationProfile(XMLEditor, JSSContainerObject):
    _url = '/mobiledeviceconfigurationprofiles'


class MobileDeviceEnrollmentProfile(XMLEditor, JSSContainerObject):
    _url = '/mobiledeviceenrollmentprofiles'
    search_types = {'name': '/name/', 'invitation': '/invitation/'}


class MobileDeviceExtensionAttribute(XMLEditor, JSSContainerObject):
    _url = '/mobiledeviceextensionattributes'


class MobileDeviceInvitation(XMLEditor, JSSContainerObject):
    _url = '/mobiledeviceinvitations'
    can_put = False
    search_types = {'invitation': '/invitation/'}


class MobileDeviceGroup(MobileDeviceGroupEditor, JSSContainerObject):
    _url = '/mobiledevicegroups'
    list_type = 'mobile_device_group'


class MobileDeviceProvisioningProfile(XMLEditor, JSSContainerObject):
    _url = '/mobiledeviceprovisioningprofiles'
    search_types = {'name': '/name/', 'uuid': '/uuid/'}


class NetbootServer(XMLEditor, JSSContainerObject):
    _url = '/netbootservers'


class NetworkSegment(XMLEditor, JSSContainerObject):
    _url = '/networksegments'


class OSXConfigurationProfile(XMLEditor, JSSContainerObject):
    _url = '/osxconfigurationprofiles'


class Package(PackageEditor, JSSContainerObject):
    _url = '/packages'
    list_type = 'package'


class Peripheral(XMLEditor, JSSContainerObject):
    _url = '/peripherals'
    search_types = {}


class PeripheralType(XMLEditor, JSSContainerObject):
    _url = '/peripheraltypes'
    search_types = {}


class Policy(PolicyEditor, JSSContainerObject):
    _url = '/policies'


class Printer(XMLEditor, JSSContainerObject):
    _url = '/printers'


class RestrictedSoftware(XMLEditor, JSSContainerObject):
    _url = '/restrictedsoftware'


class RemovableMACAddress(XMLEditor, JSSContainerObject):
    _url = '/removablemacaddresses'


class SavedSearch(XMLEditor, JSSContainerObject):
    _url = '/savedsearches'
    can_put = False
    can_post = False
    can_delete = False


class Script(XMLEditor, JSSContainerObject):
    _url = '/scripts'


class Site(XMLEditor, JSSContainerObject):
    _url = '/sites'


class SoftwareUpdateServer(XMLEditor, JSSContainerObject):
    _url = '/softwareupdateservers'


class SMTPServer(XMLEditor, JSSFlatObject):
    _url = '/smtpserver'
    id_url = ''
    can_list = False
    can_post = False
    search_types = {}


class UserExtensionAttribute(XMLEditor, JSSContainerObject):
    _url = '/userextensionattributes'


class User(XMLEditor, JSSContainerObject):
    _url = '/users'


class UserGroup(XMLEditor, JSSContainerObject):
    _url = '/usergroups'


class JSSObjectTemplate(ElementTree.Element):
    """Base class for generating the skeleton XML required to post a new
    object.

    """
    template_type = 'abstract_object_template'
    def __init__(self, **kwargs):
        """Init an Element with the right template_type."""
        super(JSSObjectTemplate, self).__init__(tag=self.template_type,
                                                **kwargs)

    def makeelement(self, tag, attrib):
        """Return an element."""
        # We use ElementTree.SubElement() a lot. Unfortunately, it relies on a
        # super() call to its __class__.makeelement(), which will fail due to
        # the method resolution order / multiple inheritence of our objects
        #(they have an editor AND a template or JSSObject parent class).
        # This handles that issue.
        return ElementTree.Element(tag, attrib)


class JSSSimpleTemplate(JSSObjectTemplate):
    """Abstract class for simple JSS Objects."""
    template_type = 'abstract_simple_object'
    def __init__(self, name, **kwargs):
        super(JSSSimpleTemplate, self).__init__(**kwargs)
        element_name = ElementTree.SubElement(self, "name")
        element_name.text = name


class CategoryTemplate(XMLEditor, JSSSimpleTemplate):
    template_type = 'category'


class ComputerGroupTemplate(ComputerGroupEditor, JSSObjectTemplate):
    template_type = "computer_group"
    def __init__(self, name, smartness=False):
        """Creates a computer group template.

        Smart groups with no criteria by default select ALL computers.

        """
        super(ComputerGroupTemplate, self).__init__()
        element_name = ElementTree.SubElement(self, "name")
        element_name.text = name
        self.is_smart = ElementTree.SubElement(self, "is_smart")
        self.set_bool(self.is_smart, smartness)
        if smartness:
            self.criteria = ElementTree.SubElement(self, "criteria")

    def add_computer(self, device):
        """Add a computer to the group."""
        super(ComputerGroupTemplate, self).add_device(device, "computers")


class SearchCriteria(JSSObjectTemplate):
    """Object for encapsulating a smart group search criteria."""
    template_type = "criterion"
    def __init__(self, name, priority, and_or, search_type, value):
        super(SearchCriteria, self).__init__()
        crit_name = ElementTree.SubElement(self, "name")
        crit_name.text = name
        crit_priority = ElementTree.SubElement(self, "priority")
        crit_priority.text = str(priority)
        crit_and_or = ElementTree.SubElement(self, "and_or")
        crit_and_or.text = and_or
        crit_search_type = ElementTree.SubElement(self, "search_type")
        crit_search_type.text = search_type
        crit_value = ElementTree.SubElement(self, "value")
        crit_value.text = value


class PolicyTemplate(PolicyEditor, JSSObjectTemplate):
    """Object for adding policy methods."""
    template_type = "policy"

    def __init__(self, name='Unknown', category=None):
        """Create a barebones policy.

        name:       Policy name
        category:   An instance of Category

        """
        super(PolicyTemplate, self).__init__()
        # General
        self.general = ElementTree.SubElement(self, "general")
        self.name = ElementTree.SubElement(self.general, "name")
        self.name.text = name
        self.enabled = ElementTree.SubElement(self.general, "enabled")
        self.set_bool(self.enabled, True)
        self.frequency = ElementTree.SubElement(self.general, "frequency")
        self.frequency.text = "Once per computer"
        self.category = ElementTree.SubElement(self.general, "category")
        if category:
            # Without a category, the JSS will add an id of -1, with name
            # "Unknown".
            self.category_name = ElementTree.SubElement(self.category, "name")
            self.category_name.text = category.name

        # Scope
        self.scope = ElementTree.SubElement(self, "scope")
        self.computers = ElementTree.SubElement(self.scope, "computers")
        self.computer_groups = ElementTree.SubElement(self.scope,
                                                      "computer_groups")
        self.buildings = ElementTree.SubElement(self.scope, "buldings")
        self.departments = ElementTree.SubElement(self.scope, "departments")
        self.exclusions = ElementTree.SubElement(self.scope, "exclusions")
        self.excluded_computers = ElementTree.SubElement(self.exclusions,
                                                         "computers")
        self.excluded_computer_groups = ElementTree.SubElement(self.exclusions,
                "computer_groups")
        self.excluded_buildings = ElementTree.SubElement(self.exclusions,
                                                         "buildings")
        self.excluded_departments = ElementTree.SubElement(self.exclusions,
                                                           "departments")

        # Self Service
        self.self_service = ElementTree.SubElement(self, "self_service")
        self.use_for_self_service = ElementTree.SubElement(self.self_service,
                "use_for_self_service")
        self.set_bool(self.use_for_self_service, True)

        # Package Configuration
        self.pkg_config = ElementTree.SubElement(self, "package_configuration")
        self.pkgs = ElementTree.SubElement(self.pkg_config, "packages")

        # Maintenance
        self.maintenance = ElementTree.SubElement(self, "maintenance")
        self.recon = ElementTree.SubElement(self.maintenance, "recon")
        self.set_bool(self.recon, True)


class PackageTemplate(PackageEditor, JSSObjectTemplate):
    """Template for constructing package objects."""
    template_type = "package"
    def __init__(self, filename, cat_name="Unknown"):
        super(PackageTemplate, self).__init__()
        name = ElementTree.SubElement(self, "name")
        name.text = filename
        category = ElementTree.SubElement(self, "category")
        category.text = cat_name
        fname = ElementTree.SubElement(self, "filename")
        fname.text = filename
        ElementTree.SubElement(self, "info")
        ElementTree.SubElement(self, "notes")
        priority = ElementTree.SubElement(self, "priority")
        priority.text = "10"
        reboot = ElementTree.SubElement(self, "reboot_required")
        reboot.text = "false"
        fut = ElementTree.SubElement(self, "fill_user_template")
        fut.text = "false"
        feu = ElementTree.SubElement(self, "fill_existing_users")
        feu.text = "false"
        boot_volume = ElementTree.SubElement(self, "boot_volume_required")
        boot_volume.text = "false"
        allow_uninstalled = ElementTree.SubElement(self, "allow_uninstalled")
        allow_uninstalled.text = "false"
        ElementTree.SubElement(self, "os_requirements")
        required_proc = ElementTree.SubElement(self, "required_processor")
        required_proc.text = "None"
        switch_w_package = ElementTree.SubElement(self, "switch_with_package")
        switch_w_package.text = "Do Not Install"
        install_if = ElementTree.SubElement(self,
                                            "install_if_reported_available")
        install_if.text = "false"
        reinstall_option = ElementTree.SubElement(self, "reinstall_option")
        reinstall_option.text = "Do Not Reinstall"
        ElementTree.SubElement(self, "triggering_files")
        send_notification = ElementTree.SubElement(self, "send_notification")
        send_notification.text = "false"


class TemplateFromFile(XMLEditor, JSSObjectTemplate):
    """Generic template class for filling by an external file."""
    def __init__(self, filename):
        tree = ElementTree.parse(filename)
        root = tree.getroot()
        tag = root.tag
        super(TemplateFromFile, self).__init__()
        self.tag = tag
        self._children = root._children


class TemplateFromString(XMLEditor, JSSObjectTemplate):
    """Generic template class for filling with a passed string."""
    def __init__(self, data):
        root = ElementTree.fromstring(data)
        tag = root.tag
        super(TemplateFromString, self).__init__()
        self.tag = tag
        self._children = root._children


class JSSListData(dict):
    """Holds information retrieved as part of a list operation."""
    def __init__(self, obj_class, d):
        self.obj_class = obj_class
        super(JSSListData, self).__init__(d)

    @property
    def id(self):
        return int(self['id'])

    @property
    def name(self):
        return self['name']

class JSSObjectList(list):
    """A list style collection of JSSObjects.

    List operations retrieve only minimal information for most object types.
    Further, we may want to know all Computer(s) to get their ID's, but that
    does not mean we want to do a full object search for each one. Thus,
    methods are provided to both retrieve individual members' full
    information, and to retrieve the full information for the entire list.

    """
    def __init__(self, factory, obj_class, objects):
        self.factory = factory
        self.obj_class = obj_class
        super(JSSObjectList, self).__init__(objects)


    def __repr__(self):
        """Make our data human readable.

        Note: Large lists of large objects may take a long time due to
        indenting!

        """
        delimeter = 50 * '-' + '\n'
        output_string = delimeter
        for obj in self:
            output_string += "List index: \t%s\n" % self.index(obj)
            for k, v in obj.items():
                output_string += "%s:\t\t%s\n" % (k, v)
            output_string += delimeter
        return output_string.encode('utf-8')

    def sort(self):
        """Sort list elements by ID."""
        super(JSSObjectList, self).sort(key=lambda k: k.id)

    def sort_by_name(self):
        """Sort list elements by name."""
        super(JSSObjectList, self).sort(key=lambda k: k.name)

    def retrieve(self, index):
        """Return a JSSObject for the JSSListData element at index."""
        return self.factory.get_object(self.obj_class, self[index].id)

    def retrieve_by_id(self, id_):
        """Return a JSSObject for the JSSListData element with ID id_."""
        list_index = [int(i) for i, j in enumerate(self) if j.id == id_]
        if len(list_index) == 1:
            list_index = list_index[0]
            return self.factory.get_object(self.obj_class, self[list_index].id)

    def retrieve_all(self):
        """Return a list of all JSSListData elements as full JSSObjects.

        At least on my JSS, I end up with some harmless SSL errors, which are
        dealt with.

        Note: This can take a long time given a large number of objects, and
        depending on the size of each object.

        """
        final_list = []
        for i in range(0, len(self)):
            result = self.factory.get_object(self.obj_class,
                                             int(self[i]['id']))
            final_list.append(result)

        return final_list
