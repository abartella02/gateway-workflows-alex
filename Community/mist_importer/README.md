<!--  Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
 -*- coding: utf-8 -*-

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 By: Akira Goto (agoto@bluecatnetworks.com)
 Date: 2019-10-30
 Gateway Version: 20.12.1
 Description: Mist Importer README.md -->  

# Juniper Mist Importer  
**Bluecat Gateway Version:** v19.8.1 and greater  
**BlueCat Address Manager Version:** v9.1 and greater  

This workflow will import the client device information stored in the Juniper Mist Cloud Instance into BlueCat Address Manager.  
When import is executed, BlueCat Address Manager will perform IP address reconciliation depending on what is imported.  


## Prerequisites  
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  

    <img src = "img/BAM_default_settings.jpg" width = "600px">  


2. **Additional Python Code**  
This workflow requires addtional python code.  
Copy directory *"mist"* under `additional/` to `/portal/bluecat_portal/customizations/integrations/` inside the BlueCat Gateway container.  

3. **jqGrid**  
This workflow requires jqGrid.  
Download jqGrid from [HERE](http://www.trirand.com/blog/?page_id=6).  
After downloading, extract the following three files: *"ui.jqgrid.css"*, *"jquery.jqGrid.min.js"* and *"grid.locale-xx.js"*.  
*"grid.locale-xx.js"* will change depending on the locale you choose to use.  
(For instance, for Japan it will be *"grid.locale-ja.js"*)  
Copy *"ui.jqgrid.css"* and *"jquery.jqGrid.min.js"* under `/portal/static/js/vendor/jqgrid/` inside the Bluecat Gateway container.  
Create a new directory `jqgrid` under `/portal/static/js/vendor/` if none exists.  
Copy *"grid.locale-xx.js"* under `/portal/static/js/vendor/jqgrid/i18n/` inside the Bluecat Gateway container.  
Create a new directory `i18n` under `/portal/static/js/vendor/jqgrid` if none exists.   

4. **UDF**  
This workflow requires additional UDF to the **MAC Address object** in BAM.  
Add the following UDF to the **MAC Address object** in BAM.  
  - System  
  Field Name: System    
  Display Name: System   
  Type: Text  
  - Imported Source    
  Field Name: ImportedSource  
  Display Name: Imported Source   
  Type: Text  
  - Detail Link  
  Field Name: DetailLink  
  Display Name: Detail Link  
  Type: URL


## Usage   
1. **Setting Mist Importer Parameters**  
Click the *"Juniper Mist Configuration"* pull down menu to open up parameter settings.  
Set the following parameters.    

    <img src = "img/mist_importer1.jpg" width = "600px">  


- Organization ID:  
This can be obtained from your Mist Cloud Instance browser address bar.  
Please refer to the link below for more details.  
[https://www.mist.com/documentation/find-org-site-id/](https://www.mist.com/documentation/find-org-site-id/)      

- API Token:  
This will be the token used for authentication when connecting via API.  
Please refer to the Mist "API Token" API documentation for further details.  
[https://api.mist.com/api/v1/docs/Auth#api-token](https://api.mist.com/api/v1/docs/Auth#api-token).   

- Site Name:  
This corresponds to the *Organization Name* in the **Organization settings** menu.  
Make sure it is the same name (case sensitive) as in the Mist Cloud Instance web UI. (*Organization* -> *Settings*)  
  <img src = "img/mist_org_name.jpg" width = "300px">  
  Please refer to the Mist "Organization" API documentation if you wish to obtain this via API.  
  [https://api.mist.com/api/v1/docs/Org#org-setting](https://api.mist.com/api/v1/docs/Org#org-setting)     

2. **Loading Mist Client Lists**  

    <img src = "img/mist_client_list_initial.jpg" width = "600px">  

    By clicking the *"LOAD"* button, client information stored in Mist Cloud Instance will be loaded to the list.  
    By default, only the clients which **DO NOT MATCH** will be loaded to the list.  
    **DO NOT MATCH** means that there is either a *"mismatched IP address"* or an *"unknown IP address"* between the information stored in Mist Cloud Instance and the information stored in BlueCat Address Manager.  

+ *"Mismatched IP address"* => An IP address that exists in both BlueCat Address Manager and in Mist Cloud Instance, but where the MAC address does not match.  

+ *"Unknown IP address"* => An IP address that exists in Mist Cloud Instance, but not in BlueCat Address Manager. This likely represents an address that has been added to the network since the last discovery.  

**Loading Options**  
There are two loading options which you can toggle on or off when loading. Default is toggled off.  
- Include Matches  
When this option is toggled on, it will additionally load the clients which **MATCH**, meaning IP addresses that exists in both BlueCat Address Manager and in Mist Cloud Instance where the MAC address match as well.  

- Include IPAM only  
When this option is toggled on, it will load the clients which only exists in BlueCat Address Manager. These clients will be listed as a *"reclaimable IP address"*.  

    + *"Reclaimable IP Address"* => An IP address that exists in BlueCat Address Manager, but not in Mist Cloud Instance. This may represent a device that was turned off at the time of the discovery, or the address may no longer exist on the network.

**Mist Client List**    
  <img src = "img/mist_client_list_loaded.jpg" width = "600px">   

- IP Address  
The IP Address of the loaded client.  

- MAC Address  
The MAC Address of the loaded client.  

- Name  
The host name of the loaded client (if exists).  

- System  
The device type of the loaded client (if exists).  

- State  
The IP address state of the loaded client.  
  + This icon ![screenshot](img/check.gif) represents the state **Matched**. When a client of this state is imported, it will not update the IP address and MAC address information in BlueCat Address Manager (since it is already a match) but will add additional information obtained by Mist Cloud Instance.  

  + This icon ![screenshot](img/about.gif "about") represents the state **Mismatched**. When a client of this state is imported, it will update the MAC address information in BlueCat Address Manager and add additional information obtained by Mist Cloud Instance.  

  + This icon ![screenshot](img/help.gif "help") represents the state **Unknown**. When a client of this state is imported, it will update both IP address and MAC address information in BlueCat Address Manager and add additional information obtained by Mist Cloud Instance.  

  + This icon ![screenshot](img/data_delete.gif "data_delete") represents the state **Reclaimable**. When a client of this state is imported, it will reclaim the IP address in BlueCat Address Manager.  

- Last Discovered  
Timestamp of the last time Mist discovered the client. The importer will determine whether an IP address is reclaimable or not depending on the last discovered time. If more than 30 days have passed since the last discovered time, the importer will assume the IP address is reclaimable and change the *"state"* icon of the client to **Reclaimable** (![screenshot](img/data_delete.gif "data_delete") )    
**IMPORTANT:**  
Before reclaiming an IP address, please bear in mind that there is a good possibility that even though an IP address shows as a **Reclaimable** state in the list, it is actually still assigned and thus should not be reclaimed. This will happen when more than 30 days have passed since the last discovered time. Make sure the IP address is reclaimable before actually reclaiming it.       

3. **Importing**  
After thoroughly checking the state of the loaded clients, select the clients you wish to import by checking on the checkbox. You can either select them one by one or select all by checking the top left check box in the list.  

    <img src = "img/mist_client_list_check.jpg" width = "600px">  


    Click *IMPORT* to import data into BlueCat Address Manager.  
    By Clicking *CANCEL*, the whole list will be cleared.  

    **DHCP range IP addresses**  
    If the imported IP address happens to be within a DHCP range, then it will **NOT** update the IP address and MAC address information in BlueCat Address Manager and will only add additional information obtained by Mist Cloud Instance.  

4. **Checking imported information**  
Once imported, check the device information in BlueCat Address Manager.  

    <img src = "img/mist_bam_device_info.jpg" width = "600px">  


    In addition to the added information from Mist Cloud Instance, a direct link to the Mist Cloud Instance client information page will appear.  


    <img src = "img/mist_client_info.jpg" width = "600px">  

---

## Additional   

1. **Language**  
You can switch to a Japanese menu by doing the following.  
    1. Create *ja.txt* in the BlueCat Gateway container.  
    ```
    cd /portal/Administration/create_workflow/text/  
    cp en.txt ja.txt  
    ```  
    2. In the BlueCat Gateway Web UI, go to Administration > Configurations > General Configuration.   
    In General Configuration, select the *Customization* tab.  
    Under *Language:* type in `ja` and save.  

          <img src = "img/langauge_ja.jpg" width = "500px" height = "400px">  


2. **Appearance**  
This will make the base html menus a little bit wider.  
    1. Copy all files under the directory `additional/templates` to `/portal/templates` inside the Bluecat Gateway container.



## Author   
- Akira Goto (agoto@bluecatnetworks.com)  
- Ryu Tamura (rtamura@bluecatnetworks.com)  

## License
©2021 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
