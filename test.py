#!/usr/bin/env python3.4
import libtorrent as lt
import os
fs = lt.file_storage()
lt.add_files(fs, "/var/tpm-mirror/packages/")
t = lt.create_torrent(fs, flags = 1&8&16)
t.add_tracker("udp://tracker.publicbt.com:80")
print(os.path.isdir("/var/tpm-mirror/packages/"))
lt.set_piece_hashes(t,"/var/tpm-mirror/packages/")
print(t.generate())
