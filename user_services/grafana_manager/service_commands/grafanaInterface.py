import requests, json, os
from os.path import exists
from urllib3.exceptions import InsecureRequestWarning

# Settings

# Prevents invalid certificate warning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) 

class GrafanaManager(object):
    """
    Grafana Manager interacts with Grafana Host using Grafana's REST APIs 

    :param host: Grafana Host 
    :type host: str
    :param username: Grafana Admin Username
    :type username: str
    :param password: Grafana Admin Password
    :type password: str
    :param infoFilePath: Path to User Information File
    :type infoFilePath: str
    :param infoFileDelimiter: User Information File Delimiter
    :type infoFileDelimiter: str
    :param key: Grafana API token
    :type key: str
    """
    def __init__(self, host=None, username=None, password=None, infoFilePath=None, infoFileDelimiter=None, key=None):
        """
        Constructor Method
        """
        self.host = host 
        self.apiKey = key

        self.username = username
        self.password = password

        # Constant attributes for user local database

        self.infoFilePath = infoFilePath
        self.infoFileDelimiter = infoFileDelimiter

        # Create User Information file if it does not exist
        if infoFilePath is not None:
            if not exists(infoFilePath):
                fout = open(self.infoFilePath, 'w')
                fout.close()

        # Store admin username and password
        if username is not None and password is not None and infoFilePath is not None:
            self.storeUserInfo(username, password)
    
    def getHost(self):
        return self.host
    
    def setHost(self, host):
        self.host = host
    
    def getAPIKey(self):
        return self.apiKey

    def setAPIKey(self, key):
        self.apiKey = key
    
    def getUsername(self):
        return self.username
    
    def setUsername(self, username):
        self.username = username
    
    def getPassword(self):
        return self.password

    def setPassword(self, password):
        self.password = password
    
    def setUserLogin(self, username, password):
        self.username = username
        self.password = password

    def setUserInfoFile(self, userInfoFilePath, userInfoFileDelimiter):
        """
        Assigns existing user information file path and delimiter to object.

        :param userInfoFilePath: The user information file path
        :type userInfoFilePath: str
        :param userInfoFileDelimiter: The delimiter of the user information file
        :type userInfoFileDelimiter: str
        :return: Function Status
        :rtype: JSON dictionary
        """
        response = {
            'success': False,
            'msg': None
        }

        if exists(userInfoFilePath):
            self.infoFilePath = userInfoFilePath
            self.infoFileDelimiter = userInfoFileDelimiter
            response['success'] = True
            response['msg'] = "Successfully assigned path and delimiter."
        else:
            response['msg'] = "File path does not exist. Failed to assign path and delimiter."

        return response

    # File Handling Methods

    def createConfigFile(self, fileName, delimiter):
        """
        Creates configuration file representation of Grafana Manager object. 
        Config file contains host, admin username, admin password, and API token. 

        :param fileName: The path and file for where to create configuration file
        :type fileName: str
        :param delimiter: The delimiter of the configuration file
        :type delimiter: str
        :return: Function Status
        :rtype: JSON dictionary
        """
        response = {
            "success": False,
            "msg":""
        }

        configFileHost = configFileUsername = configFilePassword = configFileKey = ""

        if self.host is not None:
            configFileHost = self.host
        
        if self.username is not None:
            configFileUsername = self.username

        if self.password is not None:
            configFilePassword = self.password

        if self.apiKey is not None:
            configFileKey = self.apiKey

        with open(fileName, 'w') as cf:
            cf.write('host' + delimiter + configFileHost + '\n')
            cf.write('username' + delimiter + configFileUsername + '\n')
            cf.write('password' + delimiter + configFilePassword + '\n')
            cf.write('apiKey' + delimiter + configFileKey)
            
            response['success'] = True
            response['msg'] = "Successfully created configuration file."
    
        return response

    def parseConfigFile(self, configFile, delimiter):
        """
        Reads config file representation of Grafana Manager object and overwrites current object's values.

        :param configFile: The configuration file path
        :type configFile: str
        :param delimiter: The delimiter of the configuration file
        :type delimiter: str
        :return: Function Status
        :rtype: JSON dictionary
        """
        response = {
            "success": False,
            "msg":""
        }

        # Check if the configuration file exists
        if(exists(configFile)):
            # Assign default host and key 
            with open(configFile, 'r') as cf:
                for currentLine in cf:
                    line = currentLine.split(delimiter)
                    if(line[0] == 'host'):
                        host = str(line[1]).strip()
                        self.host = host
                    elif(line[0] == 'username'):
                        username = str(line[1]).strip()
                        self.username = username
                    elif(line[0] == 'password'):
                        password = str(line[1]).strip()
                        self.password = password
                    elif(line[0] == 'apiKey'):
                        key = str(line[1]).strip()
                        self.apiKey = key

                response['success'] = True
                response['msg'] = "Successfully parsed config file."
        else:
            response['msg'] = "No config file found. Failed to parse config file."

        return response
    
    def storeUserInfo(self, username, password):
        """
        Stores username and password to user information file. 

        :param username: Account username to be stored
        :type username: str
        :param password: Account password to be stored
        :type password: str
        :return: Function Status
        :rtype: JSON dictionary
        """
        response = {
            "success": False,
            "msg":""
        }

        if not exists(self.infoFilePath):
            response['msg'] = "User Info File not found."
            return response

        # Attempt to find user
        user = self.getUserInfo(username)

        # If user exist in info file
        if user['success']:
            previousLines = ""

            with open(self.infoFilePath,'r') as infoF:
                for line in infoF:
                    if len(line.strip()) > 0:
                        currentLine = line.split(self.infoFileDelimiter)
                        if currentLine[0] != username:
                            previousLines += line.strip() + '\n'

            previousLines += username + self.infoFileDelimiter + password + '\n'

            with open(self.infoFilePath, 'w') as infoF:
                infoF.write(previousLines)

            response['success'] = True
            response['msg'] = "Replaced user info in info file."
        # If user does not exist in info file
        else:
            with open(self.infoFilePath,'a') as infoF:
                infoF.write(username + self.infoFileDelimiter + password + '\n')
                response['success'] = True
                response['msg'] = "Added user info to info file."

        return response

    def getUserInfo(self, username):
        """
        Finds username and password from user information file given the username. 

        :param username: Account username to be searched
        :type username: str
        :return: Function Status
        :rtype: JSON dictionary
        """
        response = {
            "success": False,
            "msg":""
        }

        if not exists(self.infoFilePath):
            response['msg'] = "User Info File not found."
            return response

        with open(self.infoFilePath,'r') as infoF:
            for line in infoF:
                if len(line.strip()) > 0:
                    currentLine = line.split(self.infoFileDelimiter)
                    if(currentLine[0] == username):
                        response['success'] = True
                        response['msg'] = "User found."
                        user = {
                            "username": str(currentLine[0]).strip(),
                            "password": str(currentLine[1]).strip()
                        }
                        response['data'] = user

                        return response
            
            response['msg'] = "User not found."

        return response

    def getAllUserInfo(self):
        """
        Obtains all usernames and passwords from user information file.

        :return: Function Status
        :rtype: JSON dictionary
        """
        response = {
            "success": False,
            "msg":""
        }

        if not exists(self.infoFilePath):
            response['msg'] = "User Info File not found."
            return response

        with open(self.infoFilePath,'r') as infoF:
            storedUsers = []
            for line in infoF:
                if len(line.strip()) > 0:
                    currentLine = line.split(self.infoFileDelimiter)
                    user = {
                        "username": str(currentLine[0]).strip(),
                        "password": str(currentLine[1]).strip()
                    }
                    storedUsers.append(user)

            response['success'] = True
            response['msg'] = "Users stored in data."
            response['data'] = storedUsers

        return response

    # Admin Methods

    def createNewUser(self, newUserName, newUserEmail, newUserLogin, newUserPassword):
        """
        Creates new Grafana user, automatically assigning to default organization

        :param newUserName: New Grafana User Name
        :type newUserName: str
        :param newUserEmail: New Grafana User Email
        :type newUserEmail: str
        :param newUserLogin: New Grafana User Login Username
        :type newUserLogin: str
        :param newUserPassword: New Grafana User Password
        :type newUserPassword: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        session = requests.session()

        newUser = {
            "name": newUserName, 
            "email": newUserEmail, 
            "login": newUserLogin, 
            "password": newUserPassword
        }

        if self.password is None:
            response['msg'] = "No Grafana host admin password specified to object."
            return response
        
        if self.username is None:
            response['msg'] = "No Grafana host username specified to object."
            return response

        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response
        
        if self.infoFilePath is None:
            response['msg'] = "No user information file path specified to object."
            return response
        
        # Login to Grafana
        session.post(
            'https://' + self.host + '/grafana/login', 
            headers={'Content-Type': 'application/json'},
            json={"password": self.password,"user": self.username}, 
            verify=False
        )
        # Create New User
        x = session.post(
            'https://' + self.host + '/grafana/api/admin/users', 
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, 
            json=newUser, 
            verify=False
        )

        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully created new Grafana user."
            response['data'] = x

            self.storeUserInfo(newUserLogin, newUserPassword)
        else:
            response['msg'] = "Failed to create new Grafana user."
            response['data'] = x

        session.close()

        return response
    
    def findUser(self, credential):
        """
        Find Grafana user

        :param credential: Grafana username or email to find
        :type credential: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        session = requests.session()

        if self.password is None:
            response['msg'] = "No Grafana host admin password specified to object."
            return response
        
        if self.username is None:
            response['msg'] = "No Grafana host username specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response
        
        # Login to Grafana
        session.post(
            'https://' + self.host + '/grafana/login', 
            headers={'Content-Type': 'application/json'},
            json={"password": self.password,"user": self.username}, 
            verify=False
        )
        # Find User
        x = session.get(
            'https://' + self.host + '/grafana/api/users/lookup?loginOrEmail=' + str(credential), 
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, 
            verify=False
        )

        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully found Grafana user."
            response['data'] = x
        else:
            response['msg'] = "Failed to find Grafana user."
            response['data'] = x

        session.close()

        return response
    
    def getAllUsers(self):
        response = {
            "success": False,
            "msg":""
        }

        session = requests.session()

        if self.password is None:
            response['msg'] = "No Grafana host admin password specified to object."
            return response
        
        if self.username is None:
            response['msg'] = "No Grafana host username specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response
        
        # Login to Grafana
        session.post(
            'https://' + self.host + '/grafana/login', 
            headers={'Content-Type': 'application/json'},
            json={"password": self.password,"user": self.username}, 
            verify=False
        )
        # Get Users
        x = session.get(
            'https://' + self.host + '/grafana/api/users', 
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, 
            verify=False
        )

        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully found Grafana user."
            response['data'] = x
        else:
            response['msg'] = "Failed to find Grafana user."
            response['data'] = x

        session.close()

        return response
    
    def changePassword(self, credential, newPassword):
        """
        Change Grafana user password

        :param credential: Grafana username or email to be updated
        :type credential: str
        :param newPassword: New Password of given user
        :type newPassword: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        session = requests.session()

        if self.password is None:
            response['msg'] = "No Grafana host admin password specified to object."
            return response
        
        if self.username is None:
            response['msg'] = "No Grafana host username specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        if self.infoFilePath is None:
            response['msg'] = "No user information file path specified to object."
            return response
        
        # Login to Grafana
        session.post(
            'https://' + self.host + '/grafana/login', 
            headers={'Content-Type': 'application/json'},
            json={"password": self.password,"user": self.username}, 
            verify=False
        )

        # Find user with credential
        jsonResponse = self.findUser(credential)

        responseData = jsonResponse['data']

        # Return if user does not exist
        if responseData.status_code != 200:
            response['msg'] = "Failed to change password. User not found."
            response['data'] = responseData
            return response

        # Get User ID
        userId = json.loads(responseData.text)['id']

        # Change Password
        x = session.put(
            'https://' + self.host + '/grafana/api/admin/users/' + str(userId) + '/password', 
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, 
            json={"password": newPassword},
            verify=False
        )

        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully changed password for Grafana user."
            response['data'] = x

            self.storeUserInfo(credential, newPassword)
        else:
            response['msg'] = "Failed to change password for Grafana user."
            response['data'] = x
        
        session.close()

        return response

    def changeAdminPermission(self, credential, makeAdmin):
        """
        Change Grafana user admin permissions

        :param credential: Grafana username or email to be updated
        :type credential: str
        :param makeAdmin: Give Admission Permission
        :type makeAdmin: bool
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        session = requests.session()

        if self.password is None:
            response['msg'] = "No Grafana host admin password specified to object."
            return response
        
        if self.username is None:
            response['msg'] = "No Grafana host username specified to object."
            return response

        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response
        
        # Login to Grafana
        session.post(
            'https://' + self.host + '/grafana/login', 
            headers={'Content-Type': 'application/json'},
            json={"password": self.password,"user": self.username}, 
            verify=False
        )

        # Find user with credential
        jsonResponse = self.findUser(credential)

        responseData = jsonResponse['data']

        # Return if user does not exist
        if responseData.status_code != 200:
            response['msg'] = "Failed to change admin permissions. User not found."
            response['data'] = responseData
            return response

        # Get User ID
        userId = json.loads(responseData.text)['id']

        # Change Admin Permission
        x = session.put(
            'https://' + self.host + '/grafana/api/admin/users/' + str(userId) + '/permissions', 
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, 
            json={"isGrafanaAdmin": makeAdmin},
            verify=False
        )

        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully changed admin permissions for Grafana user."
            response['data'] = x
        else:
            response['msg'] = "Failed to change admin permissions for Grafana user."
            response['data'] = x

        session.close()

        return response

    def createAdminToken(self, tokenName="newToken"):
        """
        Generate new admin API token for object

        :param tokenName: Name of new token
        :type tokenName: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        session = requests.session()

        if self.password is None:
            response['msg'] = "No Grafana host admin password specified to object."
            return response
        
        if self.username is None:
            response['msg'] = "No Grafana host username specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        try:
            # Login to Grafana
            session.post(
                'https://' + self.host + '/grafana/login', 
                headers={'Content-Type': 'application/json'},
                json={"password": self.password,"user": self.username}, 
                verify=False
            )
            # Get API key
            x = session.post(
                'https://' + self.host + '/grafana/api/auth/keys', 
                headers={'Content-Type': 'application/json'}, 
                json={"name": tokenName, "role":"Admin"}, 
                verify=False
            )

            if x.status_code == 200:
                self.apiKey = json.loads(x.text)['key']
                response['success'] = True
                response['msg'] = "Successfully created new Grafana API token."
                response['data'] = x
            else:
                response['msg'] = "Failed to create new Grafana API token."
                response['data'] = x
        except KeyError:
            response['msg'] = "Grafana API token with given name has already been created."
        except:
            response['msg'] = "Failed to create new Grafana API token."

        session.close()

        return response
 
    # Dashboard Methods

    def createDashboard(self, fileDir):
        """
        Creates Grafana dashboard from given JSON file

        :param fileDir: Path to JSON containing Grafana dashboard
        :type fileDir: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        if self.apiKey is None:
            response['msg'] = "No Grafana API token specified to object."
            return response

        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        url = 'https://' + self.host + '/grafana/api/dashboards/db'

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
            'Authorization': "Bearer " + self.apiKey
        }
        
        dashboardFile = open(fileDir)
        dashboardObject = dashboardFile.read()
        dashboardFile.close()

        x = requests.post(url, headers=headers, data=dashboardObject, verify=False)

        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully uploaded dashboard."
            response['data'] = x
        else:
            response['msg'] = "Failed to upload dashboard."
            response['data'] = x
        
        return response

    def deleteDashboard(self, dashboardUID):
        """
        Deletes given dashboard unique ID in Grafana host 

        :param dashboardUID: Grafana Dashboard Unique ID, usually written within JSON
        :type dashboardUID: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        if self.apiKey is None:
            response['msg'] = "No Grafana API token specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        url = 'https://' + self.host + '/grafana/api/dashboards/uid/' + dashboardUID

        headers = {
            'Authorization': "Bearer " + self.apiKey
        }

        x = requests.delete(url, headers=headers, verify=False)

        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully deleted dashboard."
            response['data'] = x
        else:
            response['msg'] = "Failed to delete dashboard."
            response['data'] = x
        
        return response

    def findDashboard(self, dashboardUID):
        """
        Locates given dashboard unique ID in Grafana host 

        :param dashboardUID: Grafana Dashboard Unique ID, usually written within JSON
        :type dashboardUID: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        if self.apiKey is None:
            response['msg'] = "No Grafana API token specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        url = 'https://' + self.host + '/grafana/api/dashboards/uid/' + dashboardUID

        headers = {
            'Authorization': "Bearer " + self.apiKey
        }

        x = requests.get(url, headers=headers, verify=False)
        
        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully found dashboard."
            response['data'] = x
        else:
            response['msg'] = "Failed to find dashboard."
            response['data'] = x
        
        return response
    
    def getHomeDashboard(self):
        """
        Locates home dashboard in Grafana host

        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        if self.apiKey is None:
            response['msg'] = "No Grafana API token specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        url = 'https://' + self.host + '/grafana/api/dashboards/home'

        headers = {
            'Authorization': "Bearer " + self.apiKey
        }

        x = requests.get(url, headers=headers, verify=False)
        
        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully found home dashboard."
            response['data'] = x
        else:
            response['msg'] = "Failed to find home dashboard."
            response['data'] = x
        
        return response
    
    def uploadDashboards(self, dashboardDir):
        """
        Uploads all dashboards in given dashboard directory

        :param dashboardDir: Path containing directory of dashboards to be uploaded
        :type dashboardDir: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        if self.apiKey is None:
            response['msg'] = "No Grafana API token specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        if(exists(dashboardDir)):
            dashboardUploadStatus = {}
            for root, dirs, files in os.walk(dashboardDir):
                for file in files:
                    response = self.createDashboard(dashboardDir + '/' + file)
                    dashboardUploadStatus[file] = response
            response['success'] = True
            response['msg'] = "Successfully uploaded dashboards. Check data for specific information."
            response['data'] = dashboardUploadStatus
        else:
            response['msg'] = "Given directory not found. Failed to upload dashboards."

        return response



    # Setup Datasources
    def createDatasource(self, fileDir):
        """
        Creates Grafana datasource from given JSON file

        :param fileDir: Path to JSON containing Grafana datasource
        :type fileDir: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        if self.apiKey is None:
            response['msg'] = "No Grafana API token specified to object."
            return response

        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        url = 'https://' + self.host + '/grafana/api/datasources'

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
            'Authorization': "Bearer " + self.apiKey
        }
        
        datasourceFile = open(fileDir)
        datasourceObject = datasourceFile.read()
        datasourceFile.close()

        x = requests.post(url, headers=headers, data=datasourceObject, verify=False)

        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully uploaded datasource."
            response['data'] = x
        else:
            response['msg'] = "Failed to upload datasource."
            response['data'] = x
        
        return response

    # def deleteDashboard(self, dashboardUID):
    #     """
    #     Deletes given dashboard unique ID in Grafana host 

    #     :param dashboardUID: Grafana Dashboard Unique ID, usually written within JSON
    #     :type dashboardUID: str
    #     :return: Function Status
    #     :rtype: JSON dictionary 
    #     """
    #     response = {
    #         "success": False,
    #         "msg":""
    #     }

    #     if self.apiKey is None:
    #         response['msg'] = "No Grafana API token specified to object."
    #         return response
        
    #     if self.host is None:
    #         response['msg'] = "No Grafana host specified to object."
    #         return response

    #     url = 'https://' + self.host + '/grafana/api/dashboards/uid/' + dashboardUID

    #     headers = {
    #         'Authorization': "Bearer " + self.apiKey
    #     }

    #     x = requests.delete(url, headers=headers, verify=False)

    #     if x.status_code == 200:
    #         response['success'] = True
    #         response['msg'] = "Successfully deleted dashboard."
    #         response['data'] = x
    #     else:
    #         response['msg'] = "Failed to delete dashboard."
    #         response['data'] = x
        
    #     return response

    def findDatasource(self, datasourceUID):
        """
        Locates given datasource unique ID in Grafana host 

        :param datasourceUID: Grafana Datasource Unique ID, usually written within JSON
        :type datasourceUID: str
        :return: Function Status
        :rtype: JSON dictionary 
        """
        response = {
            "success": False,
            "msg":""
        }

        if self.apiKey is None:
            response['msg'] = "No Grafana API token specified to object."
            return response
        
        if self.host is None:
            response['msg'] = "No Grafana host specified to object."
            return response

        url = 'https://' + self.host + '/grafana/api/datasource/uid/' + dashboardUID

        headers = {
            'Authorization': "Bearer " + self.apiKey
        }

        x = requests.get(url, headers=headers, verify=False)
        
        if x.status_code == 200:
            response['success'] = True
            response['msg'] = "Successfully found datasource."
            response['data'] = x
        else:
            response['msg'] = "Failed to find datasource."
            response['data'] = x
        
        return response