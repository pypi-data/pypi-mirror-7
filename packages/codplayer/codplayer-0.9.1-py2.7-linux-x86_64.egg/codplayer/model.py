# codplayer - data model for discs and tracks
#
# Copyright 2013-2014 Peter Liljenberg <peter.liljenberg@gmail.com>
#
# Distributed under an MIT license, please see LICENSE in the top dir.

"""
Classes representing discs and tracks.

The unit of time in all objects is one audio frame, i.e. one sample
for each channel.

Confusingly, the CD format has it's own definition of frame.  There
are 75 CD frames per second, each consisting of 588 audio frames.
"""

import re

from musicbrainzngs import mbxml

from . import serialize

# Basic data formats


class PCM:
    channels = 2
    bytes_per_sample = 2
    bytes_per_frame = 4
    rate = 44100
    big_endian = True

    audio_frames_per_cd_frame = 588

    @classmethod
    def msf_to_frames(cls, msf):
        """Translate an MM:SS:FF to number of PCM audio frames."""

        d = msf.split(':')
        if len(d) != 3:
            raise ValueError(msf)

        m = int(d[0], 10)
        s = int(d[1], 10)
        f = int(d[2], 10)

        return (((m * 60) + s) * 75 + f) * cls.audio_frames_per_cd_frame



class RAW_CD:
    file_suffix = '.cdr'


# Various exceptions

class DiscInfoError(Exception):
    pass

    
#
# Base data classes containing the basic attributes that are used both
# in the database and in communication with external components
#

class Disc(serialize.Serializable):

    MAPPING = (
        serialize.Attr('disc_id', str),
        serialize.Attr('mb_id', str, optional = True),
        serialize.Attr('cover_mb_id', str, optional = True),
        serialize.Attr('catalog', serialize.str_unicode, optional = True),
        serialize.Attr('title', serialize.str_unicode, optional = True),
        serialize.Attr('artist', serialize.str_unicode, optional = True),
        serialize.Attr('barcode', serialize.str_unicode, optional = True),
        serialize.Attr('date', serialize.str_unicode, optional = True),

        # tracks mapping is added by the subclasses
        )

    def __init__(self):
        self.disc_id = None
        self.mb_id = None
        self.cover_mb_id = None
        
        self.tracks = []
        
        # Information we might get from the TOC, or failing that MusicBrainz
        self.catalog = None
        self.title = None
        self.artist = None

        # Additional information we might get from MusicBrainz (not
        # every possible morsel, but what might be useful to keep locally)
        self.barcode = None
        self.date = None

    def __str__(self):
        return u'{self.disc_id}: {self.artist}/{self.title}'.format(self = self).encode('utf-8')


class Track(serialize.Serializable):
    MAPPING = (
        serialize.Attr('isrc', serialize.str_unicode, optional = True),
        serialize.Attr('title', serialize.str_unicode, optional = True),
        serialize.Attr('artist', serialize.str_unicode, optional = True),

        # Length fields are added by the subclasses

        # Edit fields
        serialize.Attr('skip', bool, optional = True),
        serialize.Attr('pause_after', bool, optional = True),
        )

    def __init__(self):
        self.number = 0
        self.length = 0

        # Where index switch from 0 to 1
        self.pregap_offset = 0

        # Any additional indices
        self.index = []

        # Information we might get from the TOC, or failing that MusicBrainz
        self.isrc = None
        self.title = None
        self.artist = None

        # Edit information
        self.skip = False
        self.pause_after = False


#
# Database versions of disc and track classes
#

class DbTrack(Track):
    """Represents one track on a disc and its offsets and indices.
    All time values are in frames.
    """

    MAPPING = Track.MAPPING + (
        serialize.Attr('number', int),
        serialize.Attr('length', int),
        serialize.Attr('pregap_offset', int),
        serialize.Attr('index', list_type = int),
        serialize.Attr('file_offset', int),
        serialize.Attr('file_length', int),
        serialize.Attr('pregap_silence', int),
        )

    MUTABLE_ATTRS = (
        'isrc',
        'title',
        'artist',
        'skip',
        'pause_after',
        )

    def __init__(self):
        super(DbTrack, self).__init__()
        
        self.file_offset = 0
        self.file_length = 0

        # If part or all of the pregap isn't contained in the data
        # file at all
        self.pregap_silence = 0
        

class DbDisc(Disc):
    """Represents a CD, consisting of a number of tracks.  All time
    values are in frames.
    """

    MAPPING = Disc.MAPPING + (
        serialize.Attr('tracks', list_type = DbTrack),
        serialize.Attr('data_file_name', serialize.str_unicode),
        serialize.Attr('data_file_format', enum = (RAW_CD, )),
        serialize.Attr('audio_format', enum = (PCM, )),
        )

    MUTABLE_ATTRS = (
        'mb_id',
        'cover_mb_id',
        'catalog', 
        'title',
        'artist',
        'barcode',
        'date',
        )

    def __init__(self):
        super(DbDisc, self).__init__()
        
        self.data_file_name = None
        self.data_file_format = None
        self.audio_format = None


    def add_track(self, track):
        self.tracks.append(track)
        track.number = len(self.tracks)


    @classmethod
    def from_toc(cls, toc, disc_id):
        """Parse a TOC generated by cdrdao into a DbDisc instance.

        This is not a full parse of all varieties that cdrdao itself
        allows, as this function is only intended to be used on TOCs
        generated by cdrdao itself.

        @param toc: a cdrdao TOC as a string
        @param disc_id: a Musicbrainz disc ID (not calculated from the TOC)

        @return: A L{DbDisc} object.

        @raise DiscInfoError: if the TOC can't be parsed.
        """

        disc = cls()
        disc.disc_id = disc_id

        track = None
        cd_text = CDText()

        iter_toc = iter_toc_lines(toc)
        for line in iter_toc:

            # Don't bother about disc flags
            if line in ('CD_DA', 'CD_ROM', 'CD_ROM_XA'):
                pass

            elif line.startswith('CATALOG '):
                disc.catalog = get_toc_string_arg(line)

            # Start of a new track
            elif line.startswith('TRACK '):

                if track is not None:
                    disc.add_track(track)

                if line == 'TRACK AUDIO':
                    track = DbTrack()
                else:
                    # Just skip non-audio tracks
                    track = None

            # Ignore some track flags that don't matter to us
            elif line in ('TWO_CHANNEL_AUDIO',
                          'COPY', 'NO COPY',
                          'PRE_EMPHASIS', 'NO PRE_EMPHASIS'):
                pass

            # Anyone ever seen one of these discs?
            elif line == 'FOUR_CHANNEL_AUDIO':
                raise DiscInfoError('no support for four-channel audio')

            # Implement CD_TEXT later
            elif line.startswith('CD_TEXT '):
                info = cd_text.parse(line[7:], iter_toc, track is None)
                if info:
                    if track is None:
                        disc.artist = info.get('artist')
                        disc.title = info.get('title')
                    else:
                        track.artist = info.get('artist')
                        track.title = info.get('title')


            # Pick up the offsets within the data file
            elif line.startswith('FILE '):
                filename = get_toc_string_arg(line)

                if disc.data_file_name is None:
                    disc.data_file_name = filename

                    if filename.endswith(RAW_CD.file_suffix):
                        disc.data_file_format = RAW_CD
                        disc.audio_format = PCM
                    else:
                        raise DiscInfoError('unknown file format: "%s"'
                                            % filename)

                elif disc.data_file_name != filename:
                    raise DiscInfoError('expected filename "%s", got "%s"'
                                        % (disc.data_file_name, filename))


                p = line.split()

                # Just assume the last two are either 0 or an MSF
                if len(p) < 4:
                    raise DiscInfoError('missing offsets in file: %s' % line)

                offset = p[-2]
                length = p[-1]

                if offset == '0':
                    track.file_offset = 0
                else:
                    try:
                        track.file_offset = PCM.msf_to_frames(offset)
                    except ValueError:
                        raise DiscInfoError('bad offset for file: %s' % line)

                try:
                    track.file_length = PCM.msf_to_frames(length)
                except ValueError:
                    raise DiscInfoError('bad length for file: %s' % line)

                # Add in any silence before the track to the total length
                track.length = track.file_length + track.pregap_silence


            elif line.startswith('SILENCE '):
                track.pregap_silence = get_toc_msf_arg(line)

            elif line.startswith('START '):
                track.pregap_offset = get_toc_msf_arg(line)

            elif line.startswith('INDEX '):
                # Adjust indices to be relative start of track instead
                # of pregap
                track.index.append(get_toc_msf_arg(line)
                                   + track.pregap_offset)

            elif line.startswith('ISRC '):
                track.isrc = get_toc_string_arg(line)

            elif line.startswith('DATAFILE '):
                pass

            elif line != '':
                raise DiscInfoError('unexpected line: %s' % line)


        if track is not None:
            disc.add_track(track)

        # Make sure we did read an audio disc
        if not disc.tracks:
            raise DiscInfoError('no audio tracks on disc')

        return disc


    @classmethod
    def from_musicbrainz_disc(cls, mb_disc, filename = None):
        """Translate a L{musicbrainz2.model.Disc} into a L{DbDisc}.
        This object will contain much less information than one read
        from a TOC, but will allow a data file to be played before
        cdrdao has finished writing the TOC.

        @param mb_disc: a L{musicbrainz2.model.Disc} object

        @param filename: the filename for the data file that is
        expected to be generated by cdrdao.

        @return: a L{DbDisc} object.
        """

        tracks = mb_disc.getTracks()

        # Make sure we have any tracks
        if not tracks:
            raise DiscInfoError('no audio tracks on disc')

        disc = cls()
        disc.disc_id = mb_disc.getId()


        if filename is not None:
            disc.data_file_name = filename

            if filename.endswith(RAW_CD.file_suffix):
                disc.data_file_format = RAW_CD
                disc.audio_format = PCM
            else:
                raise DiscInfoError('unknown file format: "%s"'
                                    % filename)


        # Translate from CD frames into audio frames relative to the data file
        # that cdrdao will generate
        first_frame = tracks[0][0]

        for start, length in tracks:
            track = DbTrack()
            track.file_offset = (start - first_frame) * PCM.audio_frames_per_cd_frame
            track.length = length * PCM.audio_frames_per_cd_frame
            track.file_length = track.length
            disc.add_track(track)

        return disc
    

    def get_disc_file_size_frames(self):
        """Return expected length of the file representing this disc,
        in frames.  This assumes that the disc tracks have not been shuffled.
        """
        if self.tracks:
            t = self.tracks[-1]
            return t.file_offset + t.file_length
        else:
            return 0

    def get_disc_file_size_bytes(self):
        """Return expected length of the file representing this disc,
        in bytes.  This assumes that the disc tracks have not been shuffled.
        """
        return self.get_disc_file_size_frames() * self.audio_format.bytes_per_frame



#
# External views of the database objects
#

class ExtTrack(Track):
    """External view of a track, hiding internal details and exposing
    all lengths as whole seconds.
    """

    MAPPING = Track.MAPPING + (
        serialize.Attr('number', int, optional = True),
        serialize.Attr('length', int, optional = True),
        serialize.Attr('pregap_offset', int, optional = True),
        serialize.Attr('index', list_type = int, optional = True),
        )
    
    def __init__(self, track = None, disc = None):
        super(ExtTrack, self).__init__()
        
        if track:
            assert isinstance(track, DbTrack)
            assert isinstance(disc, DbDisc)
            
            self.number = track.number
            self.length = int(track.length / disc.audio_format.rate)
            self.pregap_offset = int(track.pregap_offset / disc.audio_format.rate)
            self.index = [int(i / disc.audio_format.rate) for i in track.index]
            self.isrc = track.isrc
            self.title = track.title
            self.artist = track.artist
            self.skip = track.skip
            self.pause_after = track.pause_after


class ExtDisc(Disc):
    """External view of a Disc, hiding internal details and exposing
    all lengths as whole seconds.
    """

    MAPPING = Disc.MAPPING + (
        serialize.Attr('tracks', list_type = ExtTrack),
        )

    def __init__(self, disc = None):
        super(ExtDisc, self).__init__()
        
        if disc:
            assert isinstance(disc, DbDisc)
            self.disc_id = disc.disc_id
            self.mb_id = disc.mb_id
            self.cover_mb_id = disc.cover_mb_id
            self.tracks = [ExtTrack(t, disc) for t in disc.tracks]
            self.catalog = disc.catalog
            self.title = disc.title
            self.artist = disc.artist
            self.barcode = disc.barcode
            self.date = disc.date


    @classmethod
    def get_from_mb_xml(cls, xml, disc_id):
        """Parse Musicbrainz XML for a given disc_id. The XML should
        have been returned from a
        "/ws/2/discid/DISC_ID?inc=recordings artist" query.

        This returns a list of matching discs.
        """

        return cls.get_from_mb_dict(mbxml.parse_message(xml), disc_id)

    @classmethod
    def get_from_mb_dict(cls, mb_dict, disc_id):
        """Parse a Musicbrainz dict for a given disc_id. The dict should
        have been returned from a
        "/ws/2/discid/DISC_ID?inc=recordings artist" query.

        This returns a list of matching discs.
        """

        discs = []

        # Dig down until we find a medium (== disc) matching the
        # provided disc_id

        if mb_dict.has_key('disc'):
            for release in mb_dict['disc']['release-list']:
                for medium in release['medium-list']:
                    for mb_disc_id in medium['disc-list']:
                        if disc_id == mb_disc_id['id']:
                            add_mb_ext_disc(discs, cls, disc_id, release, medium)

        elif mb_dict.has_key('cdstub'):
            add_cdstub_ext_disc(discs, cls, disc_id, mb_dict['cdstub'])

        return discs

#
# Musicbrainz helper functions
#
    
def add_mb_ext_disc(discs, cls, disc_id, release, medium):
    disc = cls()
    disc.disc_id = disc_id
    disc.mb_id = release['id']

    if len(release['medium-list']) == 1:
        disc.title = release['title']
    else:
        disc.title = u'{0} (disc {1})'.format(release['title'], medium['position'])

    disc.artist = release['artist-credit-phrase']
    disc.date = release.get('date')
    disc.barcode = release.get('barcode')

    disc._cover_count = int(release['cover-art-archive']['count'])
    disc.cover_mb_id = disc.mb_id if disc._cover_count > 0 else None

    for mbtrack in medium['track-list']:
        track = ExtTrack()
        track.number = int(mbtrack['position'])
        track.length = int(mbtrack['length']) / 1000
        track.title = mbtrack['recording']['title']
        track.artist = mbtrack['recording']['artist-credit-phrase']

        disc.tracks.append(track)

    disc.tracks.sort(lambda a, b: cmp(a.number, b.number))

    # If an identical disc is already in the list, don't add it
    for other in discs:
        if same_disc_title_and_artist(disc, other):
            # Keep the oldest date to get something closer to the
            # original release.
            if (disc.date is not None
                and (other.date is None or disc.date < other.date)):
                other.date = disc.date
                other.mb_id = disc.mb_id

            # Keep track of the release with the most artworks
            if (disc.cover_mb_id is not None
                and (other.cover_mb_id is None
                     or other._cover_count < disc._cover_count)):
                other.cover_mb_id = disc.cover_mb_id
                other._cover_count = disc._cover_count

            # Nothing to add here
            return

    # This was the first time we saw this disc
    discs.append(disc)


def same_disc_title_and_artist(disc, other):
    if disc.title != other.title: return False
    if disc.artist != other.artist: return False

    if len(disc.tracks) != len(other.tracks): return False

    for dt, ot in zip(disc.tracks, other.tracks):
        if dt.title != ot.title: return False
        if dt.artist != ot.artist: return False

    return True

def add_cdstub_ext_disc(discs, cls, disc_id, cdstub):
    disc = cls()
    disc.disc_id = disc_id
    disc.title = cdstub['title']
    disc.artist = cdstub['artist']

    for mb_track in cdstub['track-list']:
        track = ExtTrack()
        track.number = len(disc.tracks) + 1
        track.title = mb_track['title']
        track.length = int(mb_track['length']) / 1000
        disc.tracks.append(track)
        
    discs.append(disc)
    
#
# TOC parser helper classes
#

class CDText:
    LANGUAGE_MAP_RE = re.compile(r'LANGUAGE_MAP +\{')
    LANGUAGE_RE = re.compile(r'LANGUAGE +([0-9]+) +\{ *$')
    MAPPING_RE = re.compile(r'\b([0-9]+)\s*:\s*([0-9A-Z]+)\b')
    
    def __init__(self):
        self.language = None

    def parse(self, line, toc_iter, for_disc = False):
        """Parse a CD_TEXT block.

        Returns a dict with the extracted values, if any.
        """

        info = None
        
        if line.strip() != '{':
            raise DiscInfoError('expected "\{" but got "{0}"'.format(line))

        for line in toc_iter:
            if line == '}':
                return info
            
            m = self.LANGUAGE_MAP_RE.match(line)
            if m:
                if not for_disc:
                    raise DiscInfoError('unexpected LANGUAGE_MAP in track CD_TEXT block')
                
                self.parse_language_map(line[m.end():], toc_iter)
                continue

            m = self.LANGUAGE_RE.match(line)
            if m:
                if self.language is None:
                    # No LANGUAGE_MAP, so just use whatever language
                    # ID we find here (it's probably 0)
                    self.language = m.group(1)

                if self.language == m.group(1):
                    info = self.parse_language_block(toc_iter)
                else:
                    # Just parse and throw away the result
                    self.parse_language_block(toc_iter)

                continue

            raise DiscInfoError('unexpected CD_TEXT line: {0}'.format(line))

        raise DiscInfoError('unexpected EOF in CD_TEXT block')


    def parse_language_map(self, line, toc_iter):
        i = line.find('}')
        if i != -1:
            # entire mapping on one line
            mapstr = line[:i]
        else:
            mapstr = line
            for line in toc_iter:
                i = line.find('}')
                if i != -1:
                    # end of mapping
                    mapstr += ' ' + line[:i]
                    break
                else:
                    mapstr += ' ' + line

        mappings = self.MAPPING_RE.findall(mapstr)
        for langnum, langcode in mappings:
            # Find an English code
            if langcode == '9' or langcode == 'EN':
                self.language = langnum
                return

        # Use first language mapping, if any
        if mappings:
            self.language = mappings[0][0]
        else:
            raise DiscInfoError('found no language mappings: {0}'.format(mapstr))


    def parse_language_block(self, toc_iter):
        info = {}
        for line in toc_iter:
            if line == '}':
                return info
            elif line.startswith('TITLE '):
                info['title'] = get_toc_string_arg(line)
            elif line.startswith('PERFORMER '):
                info['artist'] = get_toc_string_arg(line)
            elif '{' in line:
                if '}' not in line:
                    self.skip_binary_data(toc_iter)
                    
        raise DiscInfoError('unexpected EOF in CD_TEXT LANGUAGE block')

    def skip_binary_data(self, toc_iter):
        for line in toc_iter:
            if '}' in line:
                return

        raise DiscInfoError('unexpected EOF in binary CD_TEXT data')
    

def iter_toc_lines(toc):
    for line in toc.split('\n'):
        # Strip comments and whitespace
        p = line.find('//')
        if p != -1:
            line = line[:p]
            
        line = line.strip()

        # Hand over non-empty lines
        if line:
            yield line


def get_toc_string_arg(line):
    """Parse out a string argument from a TOC line."""
    s = line.find('"')
    if s == -1:
        raise DiscInfoError('no string argument in line: %s' % line)

    e = line.find('"', s + 1)
    if s == -1:
        raise DiscInfoError('no string argument in line: %s' % line)

    return line[s + 1 : e]


def get_toc_msf_arg(line):
    """Parse an MSF from a TOC line."""

    p = line.split()
    if len(p) != 2:
        raise DiscInfoError(
            'expected a single MSF argument in line: %s' % line)

    try:
        return PCM.msf_to_frames(p[1])
    except ValueError:
        raise DiscInfoError('bad MSF in line: %s' % line)


