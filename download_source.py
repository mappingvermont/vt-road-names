import os
import requests
import zipfile


root_dir = os.path.dirname(__file__)
data_dir = os.path.join(root_dir, 'data')

if not os.path.exists(data_dir):
	os.mkdir(data_dir)

rds_url = r'http://maps.vcgi.vermont.gov/gisdata/vcgi/packaged_zips/EmergencyE911_RDS.zip'
town_boundary_url = r'http://maps.vcgi.vermont.gov/gisdata/vcgi/packaged_zips/BoundaryTown_TWNBNDS.zip'


def download_file(url):
	# Source: http://stackoverflow.com/questions/16694907/

    local_filename = url.split('/')[-1]
    local_path = os.path.join(data_dir, local_filename)
    print 'Starting download for {0}'.format(local_filename)

    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

    return local_path


def unzip(file_path):
    print 'Unzipping {0}'.format(os.path.basename(file_path))
    zip_ref = zipfile.ZipFile(file_path, 'r')

    output_dir = os.path.dirname(file_path)
    zip_ref.extractall(output_dir)
    zip_ref.close()


for download_url in [rds_url, town_boundary_url]:
    local_zip = download_file(download_url)
    unzip(local_zip)

    os.remove(local_zip)

