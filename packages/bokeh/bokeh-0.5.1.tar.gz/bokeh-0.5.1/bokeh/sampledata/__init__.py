from __future__ import absolute_import, print_function

from os import mkdir
from os.path import exists, expanduser, isdir, join
from sys import stdout
from six.moves.urllib.request import urlopen

def _bokeh_dir(create=False):
    bokeh_dir = expanduser("~/.bokeh")
    if not exists(bokeh_dir):
        if not create: return bokeh_dir
        print("Creating ~/.bokeh directory")
        try:
            mkdir(bokeh_dir)
        except OSError:
            raise RuntimeError("could not create bokeh config directory at %s" % bokeh_dir)
    else:
        if not isdir(bokeh_dir):
            raise RuntimeError("%s exists but is not a directory" % bokeh_dir)
    return bokeh_dir

def _data_dir(file_name=None, create=False):
    try:
        import yaml
    except ImportError:
        raise RuntimeError("'yaml' and 'pyyaml' are required to use bokeh.sampledata functions")
    bokeh_dir = _bokeh_dir(create=create)
    data_dir = join(bokeh_dir, "data")
    try:
        config = yaml.load(open(join(bokeh_dir, 'config')))
        data_dir = expanduser(config['sampledata_dir'])
    except (IOError, TypeError):
        pass
    if not exists(data_dir):
        if not create:
            raise RuntimeError('bokeh sample data directory does not exist, please execute bokeh.sampledata.download()')
        print("Creating %s directory" % data_dir)
        try:
            mkdir(data_dir)
        except OSError:
            raise RuntimeError("could not create bokeh data directory at %s" % data_dir)
    else:
        if not isdir(data_dir):
            raise RuntimeError("%s exists but is not a directory" % data_dir)
    if file_name is not None:
        return join(data_dir, file_name)
    else:
        return data_dir

def download(progress=True):
    '''
    Download larger data sets for various Bokeh examples.
    '''
    data_dir = _data_dir(create=True)
    print("Using data directory: %s" % data_dir)

    s3 = 'https://s3.amazonaws.com/bokeh_data/'
    files = [
        (s3, 'CGM.csv'),
        (s3, 'US_Counties.csv'),
        (s3, 'unemployment09.csv'),
        (s3, 'AAPL.csv'),
        (s3, 'FB.csv'),
        (s3, 'GOOG.csv'),
        (s3, 'IBM.csv'),
        (s3, 'MSFT.csv'),
        ('http://esa.un.org/unpd/wpp/SpecialAggregates/ASCII_FILES', 'WPP2012_SA_DB03_POPULATION_QUINQUENNIAL.CSV'),
    ]

    for base_url, file_name in files:
        _getfile(base_url, file_name, data_dir, progress=progress)

def _getfile(base_url, file_name, data_dir, progress=True):
    url = join(base_url, file_name)
    u = urlopen(url)
    f = open(join(data_dir, file_name), 'wb')
    meta = u.headers
    file_size = int(meta["Content-Length"])
    print("Downloading: %s (%d bytes)" % (file_name, file_size))

    file_size_dl = 0
    block_sz = 8192

    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)

        if progress:
            status = "\r%10d [%6.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            stdout.write(status)
            stdout.flush()

    f.close()
    print()
