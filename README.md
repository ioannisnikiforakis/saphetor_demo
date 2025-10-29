# saphetor_demo
Assignment for Saphetor
Author: Ioannis Nikiforakis

1. Description:

This application implements a simple REST API that will manipulate data imported on an sqlite DB from a VCF file.
To do that it utilises Django/DRF (plus various middleware) and the VCFpy parser library. When a modification is done
to the original data (Adding rows/lines, Editing or deleting them), a Celery task (via Redis) will implement the changes to
the physical file that was copied in the files project folder, by the import script (see below).

2. Installation (linux/mac):
It is suggested that you create a virtual environment to install and test this application in, so i.e.

# Create a new directory to keep everything contained and create/activate your env i.e.
mkdir saphetor_demo
cd saphetor_demo
python3 -m venv saphetor_env
source saphetor_env/bin/activate

# Clone the repo from github and cd in the project folder
git clone git@github.com:ioannisnikiforakis/saphetor_demo.git
cd saphetor_demo/


# Some Prerequisites(Important):
# 1. Install Redis, follow the instructions on https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/ 
# fitting for your system i.e. on mac you would use Homebrew: "brew install redis"
# 2. If you do not have pip on your system install the appropriate version via: https://pip.pypa.io/en/latest/installation/

# Run the setup script. This will install all the necessary Django/DRF related modules plus Celery and VCFpy
./set_dependencies.sh 

# Run the project tests
# NOTE: You should see "Ran XX tests" and an OK as a result
python3 manage.py test --settings=saph_assignment.test_settings

3. Running the project (linux/mac):

# Insert a VCF file into the project. The file will take a while to import depending on size. 
# On success it should be copied on the files folder where it will be modified henceforth.
# NOTE: The dbupdate.sh script that will perform the insert will also do a first time sqlite db
# setup via Django migrations. You can also rerun it with any valid VCF file you like and it
# will rewrite application data. You need to stop the app first (see below)
# To run the update script from the scripts folder i.e. 
./scripts/dbupdate.sh -f ../NA12877_API_10_2025.vcf 

# After succesfull data insertion the App is ready to use. You can run it via supervisor with the command
# below. This application will run Redis , the Dev Django server on port 8000 and Celery (see vcfApi.conf)
# NOTE: You can stop the app by Control-C or kill it via "kill -15 <pid>" if you run it on the background via & 
supervisord -c vcfapi.conf
Or
supervisord -c vcfapi.conf & 

4. Testing the App/ Examples of Use

You obviously can use Postman or any method you like. The tests below are performed via httpie.
(i.e. python -m pip install httpie)
IMPORTANT NOTE: The secret key, for the APIs that require it, is preset to "saph_vcf_123456" for this prototype (see below)

# Get a paginated page of the data with a page_size other than the default 10

http --print HBhb --json GET "http://127.0.0.1:8000/vcfapi/VcfRows?page_size=5&page=2" Accept:"application/json"
GET /vcfapi/VcfRows?page_size=5&page=2 HTTP/1.1
Accept: application/json
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4



HTTP/1.1 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Length: 520
Content-Type: application/json
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:33:58 GMT
ETag: "d43888660dafff435407c15521b24cc6"
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
    "count": 202463,
    "next": "http://127.0.0.1:8000/vcfapi/VcfRows?page=3&page_size=5",
    "previous": "http://127.0.0.1:8000/vcfapi/VcfRows?page_size=5",
    "results": [
        {
            "alt": "C",
            "chrom": "chr1",
            "id": "rs28402963",
            "pos": 62203,
            "ref": "T"
        },
        {
            "alt": "G",
            "chrom": "chr1",
            "id": "rs1263932941",
            "pos": 131281,
            "ref": "C"
        },
        {
            "alt": "C",
            "chrom": "chr1",
            "id": "rs1198932538",
            "pos": 131310,
            "ref": "G"
        },
        {
            "alt": "A",
            "chrom": "chr1",
            "id": "rs371468694",
            "pos": 133160,
            "ref": "G"
        },
        {
            "alt": "T",
            "chrom": "chr1",
            "id": "rs369820305",
            "pos": 133483,
            "ref": "G"
        }
    ],
    "total_pages": 40493
}


# Getting an xml payload

http --print HBhb --json GET "http://127.0.0.1:8000/vcfapi/VcfRows?page_size=2&page=2" Accept:"application/xml"
GET /vcfapi/VcfRows?page_size=2&page=2 HTTP/1.1
Accept: application/xml
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4



HTTP/1.1 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Length: 472
Content-Type: application/xml; charset=utf-8
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:34:50 GMT
ETag: "fda61a7c75b796f29725deceafecc0d0"
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

<?xml version="1.0" encoding="utf-8"?>
<root>
  <count>202463</count>
  <next>http://127.0.0.1:8000/vcfapi/VcfRows?page=3&amp;page_size=2</next>
  <previous>http://127.0.0.1:8000/vcfapi/VcfRows?page_size=2</previous>
  <total_pages>101232</total_pages>
  <results>
    <list-item>
      <chrom>chr1</chrom>
      <pos>13118</pos>
      <id>rs62028691</id>
      <ref>A</ref>
      <alt>G</alt>
    </list-item>
    <list-item>
      <chrom>chr1</chrom>
      <pos>13656</pos>
      <id>rs1263393206</id>
      <ref>CAG</ref>
      <alt>C</alt>
    </list-item>
  </results>
</root>

# Using the Etag Header functionality

http --print HBhb --json GET "http://127.0.0.1:8000/vcfapi/VcfRows?page_size=5&page=2" Accept:"application/json" If-None-Match:"\"d43888660dafff435407c15521b24cc6\""
GET /vcfapi/VcfRows?page_size=5&page=2 HTTP/1.1
Accept: application/json
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Type: application/json
Host: 127.0.0.1:8000
If-None-Match: "d43888660dafff435407c15521b24cc6"
User-Agent: HTTPie/3.2.4



HTTP/1.1 304 Not Modified
Content-Length: 0
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:36:24 GMT
ETag: "d43888660dafff435407c15521b24cc6"
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff

# Querying by id field

http --print HBhb --json GET "http://127.0.0.1:8000/vcfapi/VcfRows/id=rs369820305" Accept:"*/*"
GET /vcfapi/VcfRows/id=rs369820305 HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4



HTTP/1.1 200 OK
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
Content-Length: 136
Content-Type: application/json
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:37:25 GMT
ETag: "cf74fccdf0f10341dc43264d1d1aea09"
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "alt": "T",
            "chrom": "chr1",
            "id": "rs369820305",
            "pos": 133483,
            "ref": "G"
        }
    ],
    "total_pages": 1
}

# Creating a new Row via POST

http --print HBhb --json POST "http://127.0.0.1:8000/vcfapi/VcfRows" Authorization:"saph_vcf_123456" chrom=chr19 id=rs12345678 pos=122319 ref=G alt=A
POST /vcfapi/VcfRows HTTP/1.1
Accept: application/json, */*;q=0.5
Accept-Encoding: gzip, deflate
Authorization: saph_vcf_123456
Connection: keep-alive
Content-Length: 79
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4

{
    "alt": "A",
    "chrom": "chr19",
    "id": "rs12345678",
    "pos": "122319",
    "ref": "G"
}


HTTP/1.1 201 Created
Allow: GET, POST, HEAD, OPTIONS
Content-Length: 68
Content-Type: application/json
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:38:38 GMT
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
    "alt": "A",
    "chrom": "chr19",
    "id": "rs12345678",
    "pos": 122319,
    "ref": "G"
}

# Trying to create with an invalid value

http --print HBhb --json POST "http://127.0.0.1:8000/vcfapi/VcfRows" Authorization:"saph_vcf_123456" chrom=chr23 id=rs12345678 pos=122319 ref=G alt=A
POST /vcfapi/VcfRows HTTP/1.1
Accept: application/json, */*;q=0.5
Accept-Encoding: gzip, deflate
Authorization: saph_vcf_123456
Connection: keep-alive
Content-Length: 79
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4

{
    "alt": "A",
    "chrom": "chr23",
    "id": "rs12345678",
    "pos": "122319",
    "ref": "G"
}


HTTP/1.1 400 Bad Request
Allow: GET, POST, HEAD, OPTIONS
Content-Length: 147
Content-Type: application/json
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:47:08 GMT
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
    "chrom": [
        "CHROM name not valid!  Please use a string prefixed with chr and followed by numbers 1 to 22 or one of letters X,Y,M [Case Sensitive]"
    ]
}


# Modifying the row

http --print HBhb --json PUT "http://127.0.0.1:8000/vcfapi/VcfRows/id=rs12345678" Authorization:"saph_vcf_123456" ref=A chrom=chr21 pos=12345678 alt=G
PUT /vcfapi/VcfRows/id=rs12345678 HTTP/1.1
Accept: application/json, */*;q=0.5
Accept-Encoding: gzip, deflate
Authorization: saph_vcf_123456
Connection: keep-alive
Content-Length: 61
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4

{
    "alt": "G",
    "chrom": "chr21",
    "pos": "12345678",
    "ref": "A"
}


HTTP/1.1 200 OK
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
Content-Length: 0
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:48:38 GMT
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY


http --print HBhb --json GET "http://127.0.0.1:8000/vcfapi/VcfRows/id=rs12345678" Accept:"*/*"
GET /vcfapi/VcfRows/id=rs12345678 HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4



HTTP/1.1 200 OK
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
Content-Length: 138
Content-Type: application/json
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:49:19 GMT
ETag: "3754d05784aa238105458b8a4c84dd68"
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "alt": "G",
            "chrom": "chr21",
            "id": "rs12345678",
            "pos": 12345678,
            "ref": "A"
        }
    ],
    "total_pages": 1
}

# Deleting the row

http --print HBhb --json DELETE "http://127.0.0.1:8000/vcfapi/VcfRows/id=rs12345678" Authorization:"saph_vcf_123456"
DELETE /vcfapi/VcfRows/id=rs12345678 HTTP/1.1
Accept: application/json, */*;q=0.5
Accept-Encoding: gzip, deflate
Authorization: saph_vcf_123456
Connection: keep-alive
Content-Length: 0
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4



HTTP/1.1 204 No Content
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
Content-Length: 0
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:50:15 GMT
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

# Trying to delete a nonexistent row

http --print HBhb --json DELETE "http://127.0.0.1:8000/vcfapi/VcfRows/id=rs12345678" Authorization:"saph_vcf_123456"
DELETE /vcfapi/VcfRows/id=rs12345678 HTTP/1.1
Accept: application/json, */*;q=0.5
Accept-Encoding: gzip, deflate
Authorization: saph_vcf_123456
Connection: keep-alive
Content-Length: 0
Content-Type: application/json
Host: 127.0.0.1:8000
User-Agent: HTTPie/3.2.4



HTTP/1.1 404 Not Found
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
Content-Length: 30
Content-Type: application/json
Cross-Origin-Opener-Policy: same-origin
Date: Wed, 29 Oct 2025 13:50:44 GMT
Referrer-Policy: same-origin
Server: WSGIServer/0.2 CPython/3.12.10
Vary: Accept, Cookie
X-Content-Type-Options: nosniff
X-Frame-Options: DENY

{
    "detail": "No results found."
}


NOTE: The POST, PUT and DELETE Calls all modify the DB data, but also the physical file copy in the files folder.
In the current prorotype implementation, the file will always be uncompressed after the first app modification.
On Multiple modification calls (POST,PUT,DELETE), the file will take a while to finish (again depending on size).
On completion you will see somthing like this in the logs:
"[2025-10-29 13:50:45,597: INFO/ForkPoolWorker-8] Task vcfApi.tasks.modify_file_rows[f081b749-36d0-4935-81ac-30ef5fbd2e5a] succeeded in 30.571275187998253s: 'success'"
The current file saving implementation, as implied, is more of a prototype rather than a complete solution, although 
my tests show it working as expected...
