#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Name class for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.secondaryobj import SecondaryObject
from gen.lib.privacybase import PrivacyBase
from gen.lib.srcbase import SourceBase
from gen.lib.notebase import NoteBase
from gen.lib.datebase import DateBase
from gen.lib.surnamebase import SurnameBase
from gen.lib.nametype import NameType
from gen.lib.const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Personal Name
#
#-------------------------------------------------------------------------
class Name(SecondaryObject, PrivacyBase, SurnameBase, SourceBase, NoteBase,
           DateBase):
    """
    Provide name information about a person.

    A person may have more that one name throughout his or her life. The Name
    object stores one of them
    """

    DEF  = 0  # Default format (determined by gramps-wide prefs)
    LNFN = 1  # last name first name
    FNLN = 2  # first name last name
    FN   = 4  # first name
    
    NAMEFORMATS = (DEF, LNFN, FNLN, FN)
    #deprecated :
    PTFN = 3  # patronymic first name

    def __init__(self, source=None, data=None):
        """Create a new Name instance, copying from the source if provided.
        We should connect here to 'person-groupname-rebuild' and do something
        correct when first parameter is the name, and second parameter is
        different from the group here. However, that would be complicated and
        no real errors that cannot be ammended can be done if group is 
        saved differently.
        """
        PrivacyBase.__init__(self, source)
        SurnameBase.__init__(self, source)
        SourceBase.__init__(self, source)
        NoteBase.__init__(self, source)
        DateBase.__init__(self, source)
        if data:
            (privacy, source_list, note, date,
             self.first_name, surname_list, self.suffix, self.title, name_type,
             self.group_as, self.sort_as, self.display_as, self.call,
             self.nick, self.famnick) = data
            self.type = NameType(name_type)
            SurnameBase.unserialize(self, surname_list)
            PrivacyBase.unserialize(self, privacy)
            SourceBase.unserialize(self, source_list)
            NoteBase.unserialize(self, note)
            DateBase.unserialize(self, date)
        elif source:
            self.first_name = source.first_name
            self.suffix = source.suffix
            self.title = source.title
            self.type = source.type
            self.group_as = source.group_as
            self.sort_as = source.sort_as
            self.display_as = source.display_as
            self.call = source.call
            self.nick = source.nick
            self.famnick = source.famnick
        else:
            self.first_name = ""
            self.suffix = ""
            self.title = ""
            self.type = NameType()
            self.group_as = ""
            self.sort_as = self.DEF
            self.display_as = self.DEF
            self.call = u''
            self.nick = u''
            self.famnick = u''

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (PrivacyBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                DateBase.serialize(self),
                self.first_name, 
                SurnameBase.serialize(self),
                self.suffix, self.title,
                self.type.serialize(), 
                self.group_as, self.sort_as, self.display_as, self.call,
                self.nick, self.famnick)

    def is_empty(self):
        """
        Indicate if the name is empty.
        """
        namefieldsempty = (self.first_name == u"" and
                self.suffix == u"" and self.title == u"" and self.nick ==u""
                and self.famnick == u"")
        surnamefieldsempty = not (False in 
                            [surn.is_empty() for surn in self.surname_list])
        return namefieldsempty and surnamefieldsempty

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (privacy, source_list, note_list, date,
         self.first_name, surname_list, self.suffix, self.title, name_type,
         self.group_as, self.sort_as, self.display_as, self.call, 
         self.nick, self.famnick) = data
        self.type = NameType(name_type)
        PrivacyBase.unserialize(self, privacy)
        SurnameBase.unserialize(self, surname_list)
        SourceBase.unserialize(self, source_list)
        NoteBase.unserialize(self, note_list)
        DateBase.unserialize(self, date)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.first_name, self.suffix, self.title,
                str(self.type), self.call, self.nick, self.famnick]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.source_list + self.surname_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may 
                refer notes.
        :rtype: list
        """
        return self.source_list

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        
        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.source_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return self.get_referenced_note_handles()

    def is_equivalent(self, other):
        """
        Return if this name is equivalent, that is agrees in type, first,
        call, surname_list, suffix, title and date, to other.

        :param other: The name to compare this name to.
        :rtype other: Name
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        # TODO what to do with sort and display?
        if self.get_text_data_list() != other.get_text_data_list() or \
            self.get_date_object() != other.get_date_object() or \
            SurnameBase.serialize(self) != SurnameBase.serialize(other):
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this name.
        Normally the person merge code should opt for adding an alternate 
        name if names are actually different (like not equal surname list)

        Lost: type, first, call, suffix, title, nick, famnick and date of
        acquisition.

        :param acquisition: The name to merge with the present name.
        :rtype acquisition: Name
        """
        # TODO what to do with sort and display?
        self._merge_privacy(acquisition)
        self._merge_surname_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_source_reference_list(acquisition)

    def set_group_as(self, name):
        """
        Set the grouping name for a person. 
        
        Normally, this is the person's surname. However, some locales group 
        equivalent names (e.g. Ivanova and Ivanov in Russian are usually 
        considered equivalent.
        
        Note that there is also a database wide grouping set_name_group_mapping
          So one might map a name Smith to SmithNew, and have one person still
          grouped with name Smith. Hence, group_as can be equal to surname!
        """
        self.group_as = name

    def get_group_as(self):
        """
        Return the grouping name, which is used to group equivalent surnames.
        """
        return self.group_as

    def get_group_name(self):
        """
        Return the grouping name, which is used to group equivalent surnames.
        """
        if self.group_as:
            return self.group_as
        else:
            return self.get_primary_surname().get_surname()

    def set_sort_as(self, value):
        """
        Specifies the sorting method for the specified name. 
        
        Typically the locale's default should be used. However, there may be 
        names where a specific sorting structure is desired for a name. 
        """
        self.sort_as = value

    def get_sort_as(self):
        """
        Return the selected sorting method for the name. 
        
        The options are LNFN (last name, first name), FNLN (first name, last 
        name), etc.
        """
        return self.sort_as 

    def set_display_as(self, value):
        """
        Specifies the display format for the specified name. 
        
        Typically the locale's default should be used. However, there may be 
        names where a specific display format is desired for a name. 
        """
        self.display_as = value

    def get_display_as(self):
        """
        Return the selected display format for the name. 
        
        The options are LNFN (last name, first name), FNLN (first name, last 
        name), etc.
        """
        return self.display_as

    def get_call_name(self):
        """
        Return the call name. 
        
        The call name's exact definition is not predetermined, and may be 
        locale specific.
        """
        return self.call

    def set_call_name(self, val):
        """
        Set the call name. 
        
        The call name's exact definition is not predetermined, and may be 
        locale specific.
        """
        self.call = val

    def get_nick_name(self):
        """
        Return the nick name. 
        
        The nick name of the person, a not official name the person is known
        with.
        """
        return self.nick

    def set_nick_name(self, val):
        """
        Set the nick name. 
        
        The nick name of the person, a not official name the person is known
        with.
        """
        self.nick = val

    def get_family_nick_name(self):
        """
        Return the family nick name. 
        
        The family nick name of the family of the person, a not official name
        use to denote the entire family.
        """
        return self.famnick

    def set_family_nick_name(self, val):
        """
        Set the family nick name. 
        
        The family nick name of the family of the person, a not official name
        use to denote the entire family.
        """
        self.famnick = val
        
    def set_type(self, the_type):
        """Set the type of the Name instance."""
        self.type.set(the_type)

    def get_type(self):
        """Return the type of the Name instance."""
        return self.type

    def set_first_name(self, name):
        """Set the given name for the Name instance."""
        self.first_name = name

    def get_first_name(self):
        """Return the given name for the Name instance."""
        return self.first_name

    def set_suffix(self, name):
        """Set the suffix (such as Jr., III, etc.) for the Name instance."""
        self.suffix = name

    def get_suffix(self):
        """Return the suffix for the Name instance."""
        return self.suffix

    def set_title(self, title):
        """Set the title (Dr., Reverand, Captain) for the Name instance."""
        self.title = title

    def get_title(self):
        """Return the title for the Name instance."""
        return self.title

    def get_name(self):
        """
        Return a name string built from the components of the Name instance, 
        in the form of: surname, Firstname.
        """
        first = self.first_name
        surname = self.get_surname()
        if self.suffix:
            return "%s, %s %s" % (surname, first, self.suffix)
        else:
            return "%s, %s" % (surname, first)

    def get_upper_name(self):
        """
        Return a name string built from the components of the Name instance, 
        in the form of SURNAME, Firstname.
        """
        first = self.first_name
        surname = self.get_surname().upper()
        if self.suffix:
            return "%s, %s %s" % (surname, first, self.suffix)
        else:
            return "%s, %s" % (surname, first)

    def get_regular_name(self):
        """
        Return a name string built from the components of the Name instance, 
        in the form of Firstname surname.
        """
        first = self.first_name
        surname = self.get_surname()
        if (self.suffix == ""):
            return "%s %s" % (first, surname)
        else:
            return "%s %s, %s" % (first, surname, self.suffix)

    def get_gedcom_parts(self):
        """
        Returns a GEDCOM-formatted name dictionary.
        Note, field patronymic and prefix are deprecated, prefix_list and 
        surname list, added.
        """
        retval = {}
        retval['given'] = self.first_name.strip()
        retval['surname'] = self.get_surname().replace('/', '?')
        retval['suffix'] = self.suffix
        retval['title'] = self.title
        retval['surnamelist'] = self.get_surnames()
        retval['prefixes'] = self.get_prefixes()
        retval['connectors'] = self.get_connectors()
        retval['nick'] = self.nick
        retval['famnick'] = self.famnick
        return retval

    def get_gedcom_name(self):
        """
        Returns a GEDCOM-formatted name.
        """
        firstname = self.first_name.strip()
        surname = self.get_surname().replace('/', '?')
        suffix = self.suffix
        title = self.title
        if suffix == "":
            return '%s /%s/' % (firstname, surname)
        else:
            return '%s /%s/ %s' % (firstname, surname, suffix)
