import gflags
import httplib
import httplib2
import logging
import os
import pprint
import sys
import types
import subprocess
import json
import UserDict
import re
import hashlib
import string
import bz2
import zlib
import fcntl
import time
import threading

from keep import *
from stream import *
import config
import errors
import util

def normalize_stream(s, stream):
    stream_tokens = [s]
    sortedfiles = list(stream.keys())
    sortedfiles.sort()

    blocks = {}
    streamoffset = 0L
    for f in sortedfiles:
        for b in stream[f]:
            if b[arvados.LOCATOR] not in blocks:
                stream_tokens.append(b[arvados.LOCATOR])
                blocks[b[arvados.LOCATOR]] = streamoffset
                streamoffset += b[arvados.BLOCKSIZE]

    for f in sortedfiles:
        current_span = None
        fout = f.replace(' ', '\\040')
        for segment in stream[f]:
            segmentoffset = blocks[segment[arvados.LOCATOR]] + segment[arvados.OFFSET]
            if current_span == None:
                current_span = [segmentoffset, segmentoffset + segment[arvados.SEGMENTSIZE]]
            else:
                if segmentoffset == current_span[1]:
                    current_span[1] += segment[arvados.SEGMENTSIZE]
                else:
                    stream_tokens.append("{0}:{1}:{2}".format(current_span[0], current_span[1] - current_span[0], fout))
                    current_span = [segmentoffset, segmentoffset + segment[arvados.SEGMENTSIZE]]

        if current_span != None:
            stream_tokens.append("{0}:{1}:{2}".format(current_span[0], current_span[1] - current_span[0], fout))

        if len(stream[f]) == 0:
            stream_tokens.append("0:0:{0}".format(fout))            

    return stream_tokens    

def normalize(collection):
    streams = {}
    for s in collection.all_streams():
        for f in s.all_files():
            filestream = s.name() + "/" + f.name()
            r = filestream.rindex("/")
            streamname = filestream[:r]
            filename = filestream[r+1:]
            if streamname not in streams:
                streams[streamname] = {}
            if filename not in streams[streamname]:
                streams[streamname][filename] = []
            for r in f.segments:
                streams[streamname][filename].extend(s.locators_and_ranges(r[0], r[1]))

    normalized_streams = []
    sortedstreams = list(streams.keys())
    sortedstreams.sort()
    for s in sortedstreams:
        normalized_streams.append(normalize_stream(s, streams[s]))
    return normalized_streams


class CollectionReader(object):
    def __init__(self, manifest_locator_or_text):
        if re.search(r'^[a-f0-9]{32}(\+\d+)?(\+\S+)*$', manifest_locator_or_text):
            self._manifest_locator = manifest_locator_or_text
            self._manifest_text = None
        elif re.search(r'^\S+( [a-f0-9]{32,}(\+\S+)*)*( \d+:\d+:\S+)+\n', manifest_locator_or_text):
            self._manifest_text = manifest_locator_or_text
            self._manifest_locator = None
        else:
            raise errors.ArgumentError(
                "Argument to CollectionReader must be a manifest or a collection UUID")
        self._streams = None

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def _populate(self):
        if self._streams != None:
            return
        if not self._manifest_text:
            try:
                c = arvados.api('v1').collections().get(
                    uuid=self._manifest_locator).execute()
                self._manifest_text = c['manifest_text']
            except Exception as e:
                logging.warning("API lookup failed for collection %s (%s: %s)" %
                                (self._manifest_locator, type(e), str(e)))
                self._manifest_text = Keep.get(self._manifest_locator)
        self._streams = []
        for stream_line in self._manifest_text.split("\n"):
            if stream_line != '':
                stream_tokens = stream_line.split()
                self._streams += [stream_tokens]
        self._streams = normalize(self)

        # now regenerate the manifest text based on the normalized stream

        #print "normalizing", self._manifest_text
        self._manifest_text = ''.join([StreamReader(stream).manifest_text() for stream in self._streams])
        #print "result", self._manifest_text


    def all_streams(self):
        self._populate()
        resp = []
        for s in self._streams:
            resp.append(StreamReader(s))
        return resp

    def all_files(self):
        for s in self.all_streams():
            for f in s.all_files():
                yield f

    def manifest_text(self):
        self._populate()
        return self._manifest_text

class CollectionWriter(object):
    KEEP_BLOCK_SIZE = 2**26

    def __init__(self):
        self._data_buffer = []
        self._data_buffer_len = 0
        self._current_stream_files = []
        self._current_stream_length = 0
        self._current_stream_locators = []
        self._current_stream_name = '.'
        self._current_file_name = None
        self._current_file_pos = 0
        self._finished_streams = []

    def __enter__(self):
        pass

    def __exit__(self):
        self.finish()

    def write_directory_tree(self,
                             path, stream_name='.', max_manifest_depth=-1):
        self.start_new_stream(stream_name)
        todo = []
        if max_manifest_depth == 0:
            dirents = sorted(util.listdir_recursive(path))
        else:
            dirents = sorted(os.listdir(path))
        for dirent in dirents:
            target = os.path.join(path, dirent)
            if os.path.isdir(target):
                todo += [[target,
                          os.path.join(stream_name, dirent),
                          max_manifest_depth-1]]
            else:
                self.start_new_file(dirent)
                with open(target, 'rb') as f:
                    while True:
                        buf = f.read(2**26)
                        if len(buf) == 0:
                            break
                        self.write(buf)
        self.finish_current_stream()
        map(lambda x: self.write_directory_tree(*x), todo)

    def write(self, newdata):
        if hasattr(newdata, '__iter__'):
            for s in newdata:
                self.write(s)
            return
        self._data_buffer += [newdata]
        self._data_buffer_len += len(newdata)
        self._current_stream_length += len(newdata)
        while self._data_buffer_len >= self.KEEP_BLOCK_SIZE:
            self.flush_data()

    def flush_data(self):
        data_buffer = ''.join(self._data_buffer)
        if data_buffer != '':
            self._current_stream_locators += [Keep.put(data_buffer[0:self.KEEP_BLOCK_SIZE])]
            self._data_buffer = [data_buffer[self.KEEP_BLOCK_SIZE:]]
            self._data_buffer_len = len(self._data_buffer[0])

    def start_new_file(self, newfilename=None):
        self.finish_current_file()
        self.set_current_file_name(newfilename)

    def set_current_file_name(self, newfilename):
        if re.search(r'[\t\n]', newfilename):
            raise errors.AssertionError(
                "Manifest filenames cannot contain whitespace: %s" %
                newfilename)
        self._current_file_name = newfilename

    def current_file_name(self):
        return self._current_file_name

    def finish_current_file(self):
        if self._current_file_name == None:
            if self._current_file_pos == self._current_stream_length:
                return
            raise errors.AssertionError(
                "Cannot finish an unnamed file " +
                "(%d bytes at offset %d in '%s' stream)" %
                (self._current_stream_length - self._current_file_pos,
                 self._current_file_pos,
                 self._current_stream_name))
        self._current_stream_files += [[self._current_file_pos,
                                       self._current_stream_length - self._current_file_pos,
                                       self._current_file_name]]
        self._current_file_pos = self._current_stream_length

    def start_new_stream(self, newstreamname='.'):
        self.finish_current_stream()
        self.set_current_stream_name(newstreamname)

    def set_current_stream_name(self, newstreamname):
        if re.search(r'[\t\n]', newstreamname):
            raise errors.AssertionError(
                "Manifest stream names cannot contain whitespace")
        self._current_stream_name = '.' if newstreamname=='' else newstreamname

    def current_stream_name(self):
        return self._current_stream_name

    def finish_current_stream(self):
        self.finish_current_file()
        self.flush_data()
        if len(self._current_stream_files) == 0:
            pass
        elif self._current_stream_name == None:
            raise errors.AssertionError(
                "Cannot finish an unnamed stream (%d bytes in %d files)" %
                (self._current_stream_length, len(self._current_stream_files)))
        else:
            if len(self._current_stream_locators) == 0:
                self._current_stream_locators += [config.EMPTY_BLOCK_LOCATOR]
            self._finished_streams += [[self._current_stream_name,
                                       self._current_stream_locators,
                                       self._current_stream_files]]
        self._current_stream_files = []
        self._current_stream_length = 0
        self._current_stream_locators = []
        self._current_stream_name = None
        self._current_file_pos = 0
        self._current_file_name = None

    def finish(self):
        return Keep.put(self.manifest_text())

    def manifest_text(self):
        self.finish_current_stream()
        manifest = ''

        for stream in self._finished_streams:
            if not re.search(r'^\.(/.*)?$', stream[0]):
                manifest += './'
            manifest += stream[0].replace(' ', '\\040')
            manifest += ' ' + ' '.join(stream[1])
            manifest += ' ' + ' '.join("%d:%d:%s" % (sfile[0], sfile[1], sfile[2].replace(' ', '\\040')) for sfile in stream[2])
            manifest += "\n"
        
        #print 'writer',manifest
        #print 'after reader',CollectionReader(manifest).manifest_text()

        return CollectionReader(manifest).manifest_text()

    def data_locators(self):
        ret = []
        for name, locators, files in self._finished_streams:
            ret += locators
        return ret
