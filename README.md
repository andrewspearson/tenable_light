# tenable_light
tenable_light.py is a lightweight, dependency free, wrapper for interacting with Tenable APIs.

tenable_light follows these principles:
* No external dependencies. Follow Python's "batteries included" motto. All requests leverage Python's native [urllib](https://docs.python.org/3/library/urllib.request.html#module-urllib.request).
* Work with system installs of Python 3. No need to create Python virtual environments.
* All functions are provided in a single file for easy portability.
* Provide authentication functions for Tenable APIs.
* Provide a single raw API request function.


See Tenable's [pyTenable](https://github.com/tenable/pyTenable) for a full featured API library.
## Requirements
* Python3
## Installation
Drop tenable_light.py in the same directory as your program.
### git
```
$ git clone https://github.com/andrewspearson/tenable_light.git
```
### curl
```
$ curl https://raw.githubusercontent.com/andrewspearson/tenable_light/main/tenable_light.py -O
```

**NOTE:** macOS users running Python 3.6+ will need to [install certificates](https://bugs.python.org/issue28150).

TLDR, run this command:
```
$ /Applications/Python {version}/Install Certificates.command
```
This seems to only be an issue on MacOS.
## Usage
Authentication information may be passed directly or through an INI file. See ```tenable.ini.example``` for INI file usage.

### Client creation

Tenable Downloads client reading Bearer token directly
```python
downloads = tenable_light.Downloads('BEARER_TOKEN')
```
Tenable Downloads client reading Bearer token through an INI file
```python
downloads = tenable_light.Downloads()
```
Tenable.IO client reading API keys directly
```python
tio = tenable_light.TenableIO('ACCESS_KEY', 'SECRET_KEY')
```
Tenable.IO client reading username / password directly
```python
tio = tenable_light.TenableIO(username='USERNAME', password='PASSWORD')
```
Tenable.IO client reading API keys through an INI file
```python
tio = tenable_light.TenableIO()
```
Tenable.SC client reading API keys directly
```python
tsc = tenable_light.TenableSC('ACCESS_KEY', 'SECRET_KEY')
```
Tenable.SC client reading username / password directly
```python
tsc = tenable_light.TenableSC(username='USERNAME', password='PASSWORD')
```
Tenable.SC client reading API keys through an INI file
```python
tsc = tenable_light.TenableSC()
```

If connection data is entered directly and through an INI, then connection data will be honored in the following order:
1. API keys passed directly
2. Username and password passed directly
3. API keys passed via INI file

In order to avoid unexpected behavior, you cannot mix data from multiple sources. For example, if API keys are passed directly then options in the INI file will be ignored.


HTTPS proxy ```proxy=``` and SSL verification ```verify=``` options are also available to every client.

### API request

After a client is established, you can use the request function.

GET example
```python
response = tio1.request('GET', '/scans')
for scan in json.load(response)['scans']:
    print(scan['name'] + ': ' + scan['status'])
```
POST example
```python
scan_id = str(100)
response = tio1.request(
    method='POST',
    endpoint='/scans/' + scan_id + '/export',
    data={
        "format": "csv"
    }
)
```
