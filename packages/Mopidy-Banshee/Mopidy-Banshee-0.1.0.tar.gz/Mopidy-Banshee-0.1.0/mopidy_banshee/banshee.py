# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Thomas Amland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

import os
import sqlite3
from mopidy.models import Track, Artist, Album, Playlist


class BansheeDB(object):

    def __init__(self, database_file, art_dir):
        self.database_file = database_file
        self.art_dir = art_dir

    def get_tracks(self):
        con = sqlite3.connect(self.database_file)
        con.row_factory = sqlite3.Row
        q = """
            SELECT CoreTracks.Title AS TrackName, CoreTracks.Uri,
            CoreTracks.TrackNumber, CoreTracks.Year, CoreTracks.Duration,
            CoreArtists.Name AS ArtistName, CoreAlbums.Title AS AlbumName,
            CoreAlbums.ArtworkID
            FROM CoreTracks
            LEFT OUTER JOIN CoreArtists ON CoreArtists.ArtistID = CoreTracks.ArtistID
            LEFT OUTER JOIN CoreAlbums ON CoreAlbums.AlbumID = CoreTracks.AlbumID
            """
        tracks = [self._create_track(row) for row in con.execute(q)]
        con.close()
        return tracks

    def get_playlists(self):
        con = sqlite3.connect(self.database_file)
        con.row_factory = sqlite3.Row
        q = """SELECT PlaylistID, Name FROM CorePlaylists"""
        playlists = [Playlist(uri='banshee:playlist:%d' % int(row[b'PlaylistID']),
                              name=row[b'Name']) for row in con.execute(q)]
        con.close()
        return playlists

    def get_playlist_tracks(self, playlist_id):
        con = sqlite3.connect(self.database_file)
        con.row_factory = sqlite3.Row
        q = """
            SELECT CoreTracks.Title AS TrackName, CoreTracks.Uri,
            CoreTracks.TrackNumber, CoreTracks.Year, CoreTracks.Duration,
            CoreArtists.Name AS ArtistName, CoreAlbums.Title AS AlbumName,
            CoreAlbums.ArtworkID
            FROM CorePlaylistEntries
            LEFT OUTER JOIN CoreTracks ON CoreTracks.TrackID = CorePlaylistEntries.TrackID
            LEFT OUTER JOIN CoreArtists ON CoreArtists.ArtistID = CoreTracks.ArtistID
            LEFT OUTER JOIN CoreAlbums ON CoreAlbums.AlbumID = CoreTracks.AlbumID
            WHERE CorePlaylistEntries.PlaylistID = ?
            """
        tracks = [self._create_track(row) for row in con.execute(q, (playlist_id,))]
        con.close()
        return tracks


    def _create_track(self, row):
        art_id = row[b'ArtworkID']
        images = [os.path.join(self.art_dir, art_id + '.jpg')] if art_id else []
        artist = Artist(name=row[b'ArtistName'],)
        album = Album(
            name=row[b'AlbumName'],
            artists=[artist],
            images=images)
        track = Track(
            name=row[b'TrackName'],
            track_no=row[b'TrackNumber'],
            artists=[artist],
            album=album,
            uri=row[b'Uri'],
            date=unicode(row[b'Year']),
            length=row[b'Duration'])
        return track


def _build_sql_query(query):
    args = []
    where = []
    if 'artist' in query:
        where.append("ArtistName = ?")
        args.append(query['artist'][0])

    if 'album' in query:
        where.append("AlbumName = ?")
        args.append(query['album'][0])

    # if 'any' in query:
    #     where.append("(ArtistName = ? OR AlbumName = ?)")
    #     args.append(query['any'])
    #     args.append(query['any'])
    q = " WHERE " + " AND ".join(where) if where else ""
    return q, args