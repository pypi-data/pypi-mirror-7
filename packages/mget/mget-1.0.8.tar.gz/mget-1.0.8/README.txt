MGet - Download from video sharing sites and MGet is a file downloader which currently support HTTP.

# SYNOPSIS
mget [OPTIONS] URL [URL...]

# INSTALLATION

To install it right away for all UNIX users (Linux, OS X, etc.), type:

    sudo wget http://mssg3r.cz.cc/downloads/latest/mget -O /usr/local/bin/mget
    sudo chmod a+x /usr/local/bin/mget

# DESCRIPTION
**MGet** is a small command-line program to download videos from
Mp4upload and a few more sites. It requires the Python interpreter, version
3.+, and it is not platform specific. It should work on
your Unix box, on Windows or on Mac OS X. It is released to the public domain,
which means you can modify it, redistribute it or use it however you like.

# OPTIONS
usage: 	mget [options..] URL [URL..]

optional arguments:
  -h, --help             show this help message and exit
  --version              show program's version number and exit

General arguments:
  -e, --list-extractors  Print supported Video sharing sites.
  -I, --ignore-errors    continue on download errors, e.g. to skip unavailable videos in urlfile.
  -m, --mirror           Download from mirror link.
  --ignore-config        o not read configuration files (./mget.conf).
  -p PERCENT             How much percent to download default: (100.0).
  -U USER-AGENT          User Agent to use.

Download arguments:
  -T INT, --timeout INT  set timeout values in SECONDS.
  --no-resize-buffer     Do not resize the downloading buffer size.
  --buffer SIZE          Download buffer size (--buffer 3) default 1 [1024].
  --proxy PROXY          Use the specified HTTP/HTTPS proxy.

Simulate arguments:
  -q, --quit             activates quiet mode.
  -g, --get-url          Print Download url and exit.
  -j, --dump-info        simulate, but print information.
  --dump-user-agent      Print User-Agent in use.
  --write-info           simulate, and write information to 'mget_info'.
  --verbose              print various debugging information.
  --newline              output progress bar as new lines.
  --write-pages          Write downloaded pages to files in the current directory to debug.

Filesystem arguments:
  -c, --continue         Fource to resume download.
  --restart              Do not resume partially downloaded files (restart from beginning).
  --default-page PAGE    Change the default page name (normally this is `index.html'.).
  --cookies FILE         file to read cookies from and dump cookie jar in.
  -i FILE                File with list of url to download.
  -O FILENAME            File name to save the output..

Download file with ease! Send your request to r4v0n3@gmail.com.

Examples:
    #Download Embed video
    mget [options..] http://mp4upload.com/embed-([a-z-A-Z-0-9]).html

    #Download some amount(Percent%) of file only
    mget [options..] -p 90 <URL>

    #Download File buffer size (KB)
    mget [options..] --buffer 3 <URL>

    #Download list of files from a file
    mget [options..] -i <file>

    #Download with proxy
    mget [options..] --proxy IP:PORT <URL>

    # Check mget -h for more options

# FAQ

### I get HTTP error 402 when trying to download a video. What's this?

Apparently Some site requires some clearance before downloading, So please point the url to browser and export the cookie-file use that file to pass the clearance

### I have downloaded a video but how can I play it?

Once the video is fully downloaded, use any video player, such as [vlc](http://www.videolan.org) or [mplayer](http://www.mplayerhq.hu/).

## Read Source ##

MGet is packed as an executable zipfile, simply unzip it (might need renaming to `mget.zip` first on some systems). If you modify the code, you can run it by executing the `__main__.py` file. To recompile the executable, run `./install.sh`.

####################################################################################################

Send your Request to r4v0n3@gmail.com.

