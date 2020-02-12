# ✨ Azure usage

Repository for the WebApp and complimentary notebooks to analyse Azure usage at the Alan Turing Institute.

## 🗄️ Data

The data for the Turing is available from the `Research Engineering` OneDrive / Sharepoint Documents folder (⁨see Research Engineering - Documents⁩ ▸ ⁨Research_Computing_Platforms⁩ ▸ ⁨Azure⁩ ▸ ⁨usage_data⁩ ▸ ⁨sponsorship_portal⁩ ▸ concatenated).

Data in the form of csv file(s) as extracted from the portal should be placed in the `data` folder in the main directory:

- Copy all usage data files into a `data` folder in the top-level of this repository.

- **Or**, from the main Azure_usage directory execute the following command in order to prepare a single csv file to be imported by the WebApp:

  `python utils/prep_data.py -o data/ -i <full_path_to_extracted_data_files>`

## ☁️ Building and publishing on **Azure**

From command line in the main directory:

To build: `make build`

To publish: `make push`

Webhooks will notice the push of the new deployment and automatically update the webapp.

## 🖥️ Running WebApp locally

### Dependencies

- Python >= 3.6
- Pip
- Additional libraries as listed in requirements.txt

  Python libraries can be installed using pip as follows:
  `pip install -r requirements.txt`

### Local deployment

To launch the WebApp execute the following command in the terminal in the main directory:
`./RUN.sh`

The WebApp is then accessible via a browser:
`http://localhost:80`


## Azure Deployment Settings

- Login to https://portal.azure.com
- Click "Create a resource"
- Choose "Web App"
  - Basics
    - Select subscription, e.g. Research Engineering
    - resource group, e.g. turingazureusagerg
    - web app name, e.g. turingazureusage (this needs to match the address in server.sh)
    - For Publish select `Docker Image`
    - Operating system `Linux`
    - Region `UK South`
    - Linux Plan, e.g. turingazureusageplan
    - Size, e.g. Premium V2 P1v2 (£96.27 / Month)
  - Docker
    - Options: Docker Compose
    - Image Source: Docker Hub
    - Docker Hub Options (This is temporary)
      - Access Type: Private
      - Username: < user name >
      - Password: < password >
      - Add configuration
      - Continuous Deployment: ON
      - Optional: Add webhook to the docker hub (Repository->webhooks->new webhook)
  - Authentication
    - App Service Authentication: ON
    - Log in with Azure Active Directory
    - Azure Active Directory
      - Express
      - Select Existing AD App
        - APP NAME: TuringAzureUsage
      - Save

- Click `Review and create` and `then create`

### Port forwarding

- Configuration -> Application settings -> + New application setting

```
Name: PORT
Value: 80:80
```
- Click `OK`
- Click `Save`

### Recommended: Whitelisting Turing IP addresses

Networking -> Access Restrictions -> Add rule(s)
```
Name: Turing IP addresses
Action: Allow
Priority: 300
Type: IPv4
IP Address Block(s):

193.60.220.240/32 (Turing)
193.60.220.253/32 (Turing)

137.205.213.46/32 (Bristol temporary / remove in October, 2019)

```

#### General deployment steps (Azure)

- Prepare data
- Build container
- Push container
