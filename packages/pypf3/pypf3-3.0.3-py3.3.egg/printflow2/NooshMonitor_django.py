'''
Created on Sep 19, 2013

@author: "Colin Manning"
'''
import requests
import datetime
import time
import os
import json
import logging
import smtplib
import traceback
import pyinotify
from email.mime.text import MIMEText
from email.header import Header
from django.utils.timezone import utc
import utils

COMMASPACE = ', '    

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from workgroups.models import Workgroup, Client, User

class NooshMonitor_django(pyinotify.ProcessEvent):
    '''
    Monitor Noosh for project and specifications
    '''
    config_data = None
    
    DJANGO = 'django'

    DROPBOX = 'dropbox'
    OWNCLOUD = 'owncloud'
    
    WORKGROUP_CLASS = 'workgroup'
    PROJECT_CLASS = 'project'
    SPECIFICATION_CLASS = 'specification'
    FILE_CLASS = 'file'
    USER_CLASS = 'user'
    nooshApiUrl = "http://demo.scd.noosh.com/api/v1"
    cumulusApiUrl = "http://dis.printflow2.com"
    cumulusBaseUrl = "http://localhost:8080/disweb"
    accessToken = ""
    pdfoolboxPath = "/opt/priontflow2/callas_1/bin/pdfToolboxServer.bin"
    check_interval = 10
    dbDir = ''
    jds = None
    workgroupId = None
    theWorkgroup = {}
    db_workgroup = None
    ready = False
    logger = None
    mail_server = None
    mailer = None
    mail_signature_logo = None
    company_web_address = None
    wm = None
    notifier = None
    wdd = None
    fileSystemMonitor = None
    upload_via = None
    
    CREATE_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CREATE']
    MODIFY_EVENT = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_MODIFY']
    watch_mask = CREATE_EVENT | MODIFY_EVENT
   
    def __init__(self,config_file, workgroup_id, file_system_monitor, upload_via):
        self.config_data = config_file
        self.upload_via = upload_via
        if os.path.exists(config_file):
            with open(config_file) as f:
                self.config_data = json.load(f)
                f.close()
        if self.config_data is not None:
            self.logger = logging.getLogger('printflow2')

            self.nooshApiUrl = self.config_data['nooshapi']
            self.cumulusApiUrl = self.config_data['cumulusapi']
            self.cumulusBaseUrl = self.config_data['cumulusbaseurl']
            self.accessToken = self.config_data['accesstoken']
            self.pdfoolboxPath = self.config_data['pdftoolbox']
            self.check_interval = self.config_data['checkinterval']
            self.dbDir = self.config_data['dbdir']
            self.logger.info("Database directory: " + self.dbDir)
            self.logger.info("Noosh API: " + self.nooshApiUrl)
            self.logger.info("Cumulus API: " + self.cumulusApiUrl)
            self.logger.info("Cumulus Base URL: " + self.cumulusBaseUrl)
            self.logger.info("PDF Toolbox: " + self.pdfoolboxPath)
            self.logger.info("Noosh check interval: " + str(self.check_interval))
            self.mail_server = self.config_data['mail_server']
            self.setup_mailer(self.mail_server)
            self.company_web_address = self.config_data['company_web_address']

            ('\n'
             '            self.jds = JDs(self.dbDir, self.os_userid, self.os_groupid)\n'
             '            self.jds.register_class(self.WORKGROUP_CLASS)\n'
             '            self.jds.register_class(self.PROJECT_CLASS)\n'
             '            self.jds.register_class(self.SPECIFICATION_CLASS)\n'
             '            self.jds.register_class(self.FILE_CLASS)\n'
             '            self.jds.register_class(self.USER_CLASS)\n'
             '            '
            )
            self.workgroupId = workgroup_id

            ('\n'
             '            getWorkgroupUrl = "http://localhost:8000/workgroups/" + self.workgroupId + \'/clients\'\n'
             '            response = requests.get(getWorkgroupUrl)\n'
             '            if response.status_code == 200:\n'
             '                # now link to category\n'
             '                self.theWorkgroup = response.json()\n'
             '            '
            )
 
            self.fileSystemMonitor = file_system_monitor
            
            self.db_workgroup = Workgroup.objects.select_related().get(noosh_id=self.workgroupId)
            self.db_workgroup.clients_cache = self.db_workgroup.clients.all()
            self.db_workgroup.clients_users_cache = {}
            for client in self.db_workgroup.clients_cache:
                self.db_workgroup.clients_users_cache[client.pk] = client.users.all()
            self.ensureClientFoldersForUser(self.db_workgroup)
            
            if 'killfile' in self.config_data:
                pyinotify.ProcessEvent.__init__(self)
                self.wm = pyinotify.WatchManager()
                self.notifier = pyinotify.ThreadedNotifier(self.wm, self)
                self.wdd = self.wm.add_watch(os.path.dirname(self.config_data['killfile']), self.watch_mask, rec=False, auto_add=True)
                self.ready = True
        else:
            self.ready = False
            print(('Failed to load config file: ', config_file))

    def ensureClientFoldersForUser(self, workgroup):
        # assume all is correctly setup in workgroup, and if not, let it die
        rootFolder = workgroup.dropbox_root
        clients = workgroup.clients_cache
        for client in clients:
            clientFolder = os.path.join(rootFolder, client.name)
            #projectsFolder = os.path.join(clientFolder, 'Projects')
            if not os.path.exists(clientFolder):
                os.makedirs(clientFolder, mode=0o777)
            os.chown(clientFolder, workgroup.os_userid, workgroup.os_groupid)
            #os.chown(projectsFolder, self.os_userid, self.os_groupid)

                     
    def process_IN_CREATE(self, event):
        if event.pathname == self.config_data['killfile']:
            self.stop()
        
    def process_IN_MODIFY(self, event):
        if event.pathname == self.config_data['killfile']:
            self.stop()

    def setup_mailer(self, mail_server):
        self.mailer = smtplib.SMTP(mail_server['host'], mail_server['port'])
        self.mail_signature_logo = mail_server['signature_logo']
        try:
            self.mailer.login(mail_server['default_login'], mail_server['default_password'])
        except:
            self.logger.error('Failed to login to mail server')
        
    def send_mail(self, receivers, subject, message):
        try:
            send_message = MIMEText(message, 'plain')
            send_message['Subject'] = subject
            send_message['From'] = self.mail_server['default_login']
            send_message['To'] = COMMASPACE.join(receivers)
            try:
                self.mailer.sendmail(self.mail_server['default_login'], receivers, send_message.as_string())
            except:
                # assume mailserver died, login again and retry
                self.setup_mailer(self.mail_server)
                self.mailer.sendmail(self.mail_server['default_login'], receivers, send_message.as_string())
        except:
            self.logger.error('problem sending plain text email')            
            self.logger.error(traceback.format_exc())
            traceback.print_exc()
                
    def send_html_mail(self, receivers, subject, message):
        try:
            send_message = MIMEText(message.encode('utf-8'), 'html', 'utf-8')
            send_message['Subject'] = Header(subject, 'utf-8')
            send_message['From'] = self.mail_server['default_login']
            send_message['To'] = COMMASPACE.join(receivers)
            try:
                self.mailer.sendmail(self.mail_server['default_login'], receivers, send_message.as_string())
            except:
                # assume mailserver died, login again and retry
                self.setup_mailer(self.mail_server)
                self.mailer.sendmail(self.mail_server['default_login'], receivers, send_message.as_string())
        except:
            self.logger.error('problem sending html email')            
            self.logger.error(traceback.format_exc())
            traceback.print_exc()
            
    def is_ready(self):
        return self.ready
            
    def start(self):
        while self.ready:
            try:
                ok = True
                t = time.localtime()
                now = datetime.datetime.utcnow().replace(tzinfo=utc)
                dt = datetime.datetime.fromtimestamp(time.mktime(t))
                this_check_time = now.strftime('%Y%m%d%H%M%S')        
        
                self.logger.info("Checking Noosh for project activity in workgroup: '" + self.db_workgroup.name + "' with id: '"+ str(self.db_workgroup.id) + "' at " + str(this_check_time))
                last_check_time = self.db_workgroup.last_check
                #last_check_time = time.strptime(self.db_workgroup.last_check, '%Y%m%d%H%M%S')
                ok = self.checkForProjects(self.db_workgroup, 'create_date_from', True) # check for creates
                if ok:
                    ok = self.checkForProjects(self.db_workgroup, 'last_spec_update_from', False) # check for spec updates
                else:
                    self.logger.info('check for project creates did not return ok')
     
                # save check time after all done
                #print 'COLIN>>>>> done checking projects, about to save workgroup data with time: "+this_check_time'
                if ok:
                    self.db_workgroup.last_check = now
                    self.db_workgroup.save()
                    #self.jds.update(self.WORKGROUP_CLASS, self.theWorkgroup)
                    #self.fileSystemMonitor.scanFolders()
                else:
                    self.logger.info('check for project spec updates did not return ok')
            except:
                self.logger.error('Problem communicating with Noosh - will try again in '+self.check_interval+' seconds.')
            finally:
                time.sleep(self.check_interval)
                
    def stop(self):
        self.ready = False
 
    '''
     The worker methods
    '''
    def createDamProjectCategory(self, workgroup, project, client):
        # http://dis.printflow2.com/data/vodacom/create?item=category&path=$Categories:Demo:Colin
        project_path = client['name'] +":Projects:" + str(project['project_id']) + ' - ' + project['project_name']
        category_path = '$Categories:' + project_path
        requestUrl = self.cumulusApiUrl +"/data/" + workgroup.dam_site + '/create?item=category&path=' + category_path.replace('&', '%26')
        disResponse = requests.get(requestUrl)
        response = disResponse.json()
        result = {}
        result['class'] = self.PROJECT_CLASS
        result['id'] = project['project_id']
        result['id_parent'] = project['workgroup_id']
        result['class_parent'] = self.WORKGROUP_CLASS
        result['noosh_project'] = project
        
        cumulus_project = {}
        cumulus_project['dam_category_path'] = category_path
        cumulus_project['dam_category_id'] = response['id']
        cumulus_project['dam_site'] = workgroup.dam_site
        result['cumulus_project'] = cumulus_project
        
        #result['dropbox_path'] = workgroup['dropbox_root'] + '/' + project['client_account'] +"/Projects/" + str(project['project_id'])
        result['dropbox_path'] = workgroup.dropbox_root + '/' + client['name']
        utils.ensureDirectoryExistsForUser(result['dropbox_path'], self.os_userid, self.os_groupid, 0o777)
        if 'project_folders' in self.theWorkgroup:
            for f in self.theWorkgroup['project_folders']:
                fp = os.path.join(result['dropbox_path'], f)
                utils.ensureDirectoryExistsForUser(fp, workgroup.os_userid, workgroup.os_groupid, 0o777)                    
        return result

    def createDamSpecificationCategory(self, client, project, spec):
        try:
            category_path = project['cumulus_project']['dam_category_path'] + ":" + spec['reference_number']
            requestUrl = self.cumulusApiUrl +"/data/" + project['cumulus_project']['dam_site'] + '/create?item=category&path=' + category_path.replace('&', '%26')
            disResponse = requests.get(requestUrl)
            result = {}
            response = disResponse.json()
            result['class'] = self.SPECIFICATION_CLASS
            result['id'] = spec['reference_number']
            result['id_parent'] = project['id']
            result['class_parent'] = self.PROJECT_CLASS
            result['noosh_specification'] = spec
            
            cumulus_specification = {}
            cumulus_specification['dam_category_path'] = category_path
            cumulus_specification['dam_category_id'] = response['id']
            cumulus_specification['dam_site'] = project['cumulus_project']['dam_site']
            result['cumulus_specification'] = cumulus_specification
            cb = result['noosh_specification']['created_by']
            result['creator_name'] = cb['first_name'] + ' ' + cb['last_name']
            result['creator_email'] = cb['email']
            result['id_project'] = project['id']
            result['project_name'] = project['noosh_project']['project_name']
        
            if 'default_dropbox_folder' not in client:
                project_folder = project['dropbox_path'] + "/" + result['creator_name'] + '/Project-' + str(result['id_project'])
                utils.ensureDirectoryExistsForUser(project_folder, self.os_userid, self.os_groupid, 0o777)            
                result['dropbox_path'] = project_folder + '/' + str(spec['reference_number'])
                utils.ensureDirectoryExistsForUser(result['dropbox_path'], self.db_workgroup.os_userid, self.db_workgroup.os_groupid, 0o777)            
            else:
                default_dropbox_folder = project['dropbox_path'] + "/" + client['default_dropbox_folder']
                utils.ensureDirectoryExistsForUser(default_dropbox_folder, self.os_userid, self.os_groupid, 0o777)
                project_folder = default_dropbox_folder + '/Project-' + str(result['id_project'])
                utils.ensureDirectoryExistsForUser(project_folder, self.db_workgroup.os_userid, self.db_workgroup.os_groupid, 0o777)            
                result['dropbox_path'] = project_folder + '/' + str(spec['reference_number'])
                utils.ensureDirectoryExistsForUser(result['dropbox_path'], self.os_userid, self.db_workgroup.os_groupid, 0o777)
                '''
                if 'specification_folders' in self.theWorkgroup:
                    for f in self.theWorkgroup['specification_folders']:
                        fp = os.path.join(result['dropbox_path'], f)
                        utils.ensureDirectoryExistsForUser(fp, self.db_workgroup.os_userid, self.db_workgroup.os_groupid, 0o777)
                '''
            # also set up dropbox for any project team owners
            '''
            if ('team_owners' in project) and (project['team_owners'] is not None):
                for team_owner in project['team_owners'].split(', '):
                    project_folder = os.path.join(project['dropbox_path'], team_owner + '/Project-' + str(result['id_project']))
                    utils.ensureDirectoryExistsForUser(project_folder, self.os_userid, self.os_groupid, 0o777)            
                    team_owner_path = project_folder + '/' + str(spec['reference_number'])
                    utils.ensureDirectoryExistsForUser(team_owner_path, self.os_userid, self.os_groupid, 0o777)
            '''
                      
            # and finally the account manager
            if 'account_managers' in client and 'users' in client:
                users = client['users']
                ams = client['account_managers']
                for am_id in client['account_managers']:
                    if am_id in users:
                        am_project_path = os.path.join(project['dropbox_path'], users[am_id]['dropbox_folder'] + \
                                               '/Project-' + str(result['id_project']))
                        utils.ensureDirectoryExistsForUser(am_project_path, self.os_userid, self.os_groupid, 0o777)            
                        am_spec_path = am_project_path +  '/' + str(spec['reference_number'])
                        utils.ensureDirectoryExistsForUser(am_spec_path, self.os_userid, self.os_groupid, 0o777)      
                        '''      
                        if 'specification_folders' in self.theWorkgroup:
                            for f in self.theWorkgroup['specification_folders']:
                                fp = os.path.join(am_spec_path, f['name'])
                                utils.ensureDirectoryExistsForUser(fp, self.os_userid, self.os_groupid, 0o777)  
                        '''                  
           
            # create a file that shows the spec name for convenience
            # name_file = os.path.join(result['dropbox_path'], result['noosh_specification']['spec_name']) + '.json'
            #name_file = os.path.join(result['dropbox_path'], result['noosh_specification']['spec_name'])
            name_file = os.path.join(result['dropbox_path'], '.'+result['noosh_specification']['spec_name'].replace('/', '_'))
            try:
                with open(name_file, "w") as f:
                    f.write(json.dumps(result, indent=3))
                    os.chown(name_file, self.db_workgroup.os_userid, self.db_workgroup.os_groupid)
            except:
                self.logger.error('Problem writing file: '+name_file)
        except:
            self.logger.error(traceback.format_exc())
            traceback.print_exc()
        return result

    def checkForProjectSpecifications(self, client, workgroup, project, proj_is_new):
        offset = 0
        count = 5000
        filters = '{"limit":5000, "offset":0}'
        #filters = urllib.quote_plus(filters)
        requestUrl = self.nooshApiUrl + "/workgroups/" + str(workgroup.id) + "/projects/" + str(project['id']) + "/specs?access_token=" + self.accessToken + "&filters=" + filters
        nooshResponse = requests.get(requestUrl)
        response = nooshResponse.json()
        specs = None
        while response['status_code'] == 200:
            specs = response['results']
            for i in range(len(specs)):
                db_spec = self.jds.fetch(self.SPECIFICATION_CLASS, specs[i]['reference_number'])
                #spec_is_new = (db_spec is None)
                self.processSpecification(workgroup, client, project, specs[i], proj_is_new, db_spec)
            offset += count
            filters = '{"limit":'+str(count)+', "offset":' + str(offset)+'}'
            #filters = urllib.quote_plus(filters)
            requestUrl = self.nooshApiUrl + "/workgroups/" + str(workgroup.id) + "/projects/" + str(project['id']) + "/specs?access_token=" + self.accessToken + "&filters=" + filters
            nooshResponse = requests.get(requestUrl)
            response = nooshResponse.json()
        return specs

    def getNooshProjectDetails(self, workgroup, project):
        requestUrl = self.nooshApiUrl + "/workgroups/" + str(workgroup['id']) + "/projects/" + str(project['project_id']) +"?access_token=" + self.accessToken
        nooshResponse = requests.get(requestUrl)
        result = nooshResponse.json()
        if result['status_code'] == 200:
            return result['result']            
    
    def processProject(self, workgroup_last_check, workgroup, project, project_filter, send_email):
        print(('Processing project: ', str(project['project_id']), project['project_name'] +" for '" + project_filter +"'"))
        proj = self.jds.fetch(self.PROJECT_CLASS, project['project_id'])
        proj_is_new = (proj is None)
        if 'client_account' in project and project['client_account'] is not None:
            project['client_account'] = project['client_account'].replace('&', 'and')    
        project_details = self.getNooshProjectDetails(workgroup, project)
        project_details['workgroup_id'] = workgroup['id']
            # we need a client account, if not existing, then we need to pick it up in modification
        client = None
        if project['client_account'] in workgroup['clients'] and 'users' in workgroup.clients[project['client_account']]:
            client = workgroup.clients[project['client_account']]
        elif 'identify_filter_key' in workgroup and 'custom_fields' in project_details:
            k = workgroup['identify_filter_key']
            for custom_field in project_details['custom_fields']:
                if client is not None:
                    break
                if k == custom_field['param_name']:
                    if custom_field['string_value'] is not None:
                        v = custom_field['string_value']
                    elif custom_field['number_value'] is not None:
                        v = custom_field['number_value']
                    for a_client_name in workgroup['clients']:
                        a_client = workgroup['clients'][a_client_name]
                        if 'identify_filter_value' in a_client and a_client['identify_filter_value'] == v:
                            client = a_client
                            break
        elif len(workgroup['clients']) == 1:
            # just gert the first one
            client = next(iter(workgroup['clients'].values()))
        else:
            print((' - aborting project', str(project['project_id']), ', no client account available'))
            return
        
        if client is None:
            print((' - aborting project', str(project['project_id']), ', no client account found'))
            return
        if project_details['project_description'] is None:
            project_details['project_description'] = ''
        if project_details['comments'] is None:
            project_details['comments'] = ''
        db_project = self.createDamProjectCategory(workgroup, project_details, client)
        self.jds.create(self.PROJECT_CLASS, db_project)
        specs = self.checkForProjectSpecifications(client, workgroup, db_project, proj_is_new)
        proj = db_project['noosh_project']
        if proj_is_new and send_email:
            subject = 'Project Created for ' + client['name']
            message = self.get_email_project_create_body(proj)
            if specs is not None:            
                for i in range(len(specs)):
                    spec = specs[i]
                    message += self.get_email_specification_body(proj, spec)
            message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)
            mail_list = []
            if 'account_manager_emails' in client:
                mail_list = client['account_manager_emails']
            if 'project_notify_emails' in client:
                for fi in range(len(client['project_notify_emails'])):
                    if client['project_notify_emails'][fi] not in mail_list:
                        mail_list.append(client['project_notify_emails'][fi])
            self.send_html_mail(mail_list, subject, message)    
            if 'flowdock_accesstoken' in workgroup['clients'][client['name']]:
                self.inform_flowdock(workgroup['clients'][client['name']]['flowdock_accesstoken'], proj, specs)                                   
            
    def inform_flowdock(self, accesstoken, proj, specs):
        
        subject = 'Project ' + proj['project_name'] + ' created'
        #message = 'A new project '+proj['project_name']+' has been created with id: "'+str(proj['project_id']) + '. \
#with the following specifications:'

        message = ('<div>\
<h3>A new project has been created:</h3> \
<table> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Description:</td><td>%s</td></tr>\
<tr><td>Comments:</td><td>%s</td></tr> \
</table></div><br /><div>Specifications:</div><hr />'
        % (proj['project_id'], proj['project_name'], proj['project_description'], proj['comments']))

        for i in range(len(specs)):
            spec = specs[i]
            message += self.get_email_specification_body(proj, spec)

        post_url = 'https://api.flowdock.com/v1/messages/team_inbox/' + accesstoken
        
        data =  { "source": "PrintFlow 2 Service", "from_address" : "colin@printoutsource.com", \
                    "subject": subject, "content" : message, \
                    "project": str(proj['project_id']), \
                    "tags": ["@all", "#project", str(proj['project_id'])] }
        d = json.dumps(data)
        headers = { "Content-Type": "application/json" }
        response = requests.post(post_url, data=d, headers=headers)
        if response.status_code == 200:
            # now link to category
            r = response.json()
        
        
    def get_email_project_create_body(self, proj):
        return ('<div>\
<h3>A new project has been created:</h3> \
<table> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Description:</td><td>%s</td></tr>\
<tr><td>Comments:</td><td>%s</td></tr> \
</table></div><br /><div>Specifications:</div><hr />'
        % (proj['project_id'], proj['project_name'], proj['project_description'], proj['comments']))

    def get_email_specification_create_body(self, proj, spec):
        return ('<div> \
<h3>A new specification has been created:</h3> \
<table> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Reference No:</td><td> %s</td></tr> \
</table> \
<hr /></div>'
        % (proj['project_id'], proj['project_name'], spec['spec_id'], spec['spec_name'], spec['reference_number']))

    def get_email_specification_update_body(self, proj, spec):
        return ('<div> \
<h3>A specification has been updated:</h3> \
<table> \
<tr><td>Project Id:</td><td>%s</td></tr> \
<tr><td>Project Name:</td><td>%s</td></tr> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Reference No:</td><td> %s</td></tr> \
</table> \
<hr /></div>'
        % (proj['project_id'], proj['project_name'], spec['spec_id'], spec['spec_name'], spec['reference_number']))

    def get_email_specification_body(self, proj, spec):
        return ('<div> \
<table> \
<tr><td>Specification Id:</td><td>%s</td></tr> \
<tr><td>Specification Name:</td><td>%s</td></tr> \
<tr><td>Reference No:</td><td> %s</td></tr> \
</table> \
<hr /></div>'
        % (spec['spec_id'], spec['spec_name'], spec['reference_number']))

    def processSpecification(self, workgroup, client, project, spec, proj_is_new, db_spec):
        if db_spec is None:
            print(('Processing specification create: ', str(spec['spec_id']), spec['spec_name']))
            db_spec = self.createDamSpecificationCategory(client, project, spec)
            self.jds.create(self.SPECIFICATION_CLASS, db_spec)
            if not proj_is_new:
                subject = 'Specification created for project: ' + str(project['noosh_project']['project_id']) + \
                    ' - ' + project['noosh_project']['project_name']
                message = self.get_email_specification_create_body(project['noosh_project'], spec)
                message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)
                mail_list = []
                if 'account_manager_emails' in client:
                    mail_list = client['account_manager_emails']
                if 'project_notify_emails' in client:
                    for fi in range(len(client['project_notify_emails'])):
                        if client['project_notify_emails'][fi] not in mail_list:
                            mail_list.append(client['project_notify_emails'][fi])
                self.send_html_mail(mail_list, subject, message)    
                #if 'flowdock_accesstoken' in workgroup['clients'][project['client_account']]:
                #    self.inform_flowdock(workgroup['clients'][project['client_account']]['flowdock_accesstoken'], proj, specs)                                   
        else:
            if db_spec['noosh_specification']['spec_name'] != spec['spec_name']:
                print(('Processing specification update: ', str(spec['spec_id']), spec['spec_name']))
                try:
                    name_file = os.path.join(db_spec['dropbox_path'], '.'+db_spec['noosh_specification']['spec_name'].replace('/', '_'))
                    os.remove(name_file)
                    db_spec['noosh_specification'] = spec
                    self.jds.update(self.SPECIFICATION_CLASS, db_spec)
                    name_file = os.path.join(db_spec['dropbox_path'], '.'+db_spec['noosh_specification']['spec_name'].replace('/', '_'))
                    with open(name_file, "w") as f:
                        f.write(json.dumps(db_spec, indent=3))
                        os.chown(name_file, self.os_userid, self.os_groupid)
                        if not proj_is_new:
                            subject = 'Specification updated for project: ' + str(project['noosh_project']['project_id']) + \
                                ' - ' + project['noosh_project']['project_name']
                            message = self.get_email_specification_update_body(project['noosh_project'], spec)
                            message += utils.get_email_company_footer(self.mail_signature_logo, self.company_web_address)
                            mail_list = []
                            if 'account_manager_emails' in client:
                                mail_list = client['account_manager_emails']
                            if 'project_notify_emails' in client:
                                for fi in range(len(client['project_notify_emails'])):
                                    if client['project_notify_emails'][fi] not in mail_list:
                                        mail_list.append(client['project_notify_emails'][fi])
                            self.send_html_mail(mail_list, subject, message)    
                except:
                    self.logger.error('Problem writing file: '+name_file)
    
    def checkForProjects(self, workgroup, project_filter, send_email):
        ok = False
        try:
            workgroup_id = str(workgroup.id)
            #workgroup_last_check = datetime.datetime.fromtimestamp(workgroup['last_check']).isoformat()
            workgroup_last_check = workgroup.last_check.isoformat()
            #workgroup_last_check = datetime.datetime.fromtimestamp(time.mktime(last_check_time)).isoformat()
            localtime = time.localtime()
            timezone = -(time.altzone if localtime.tm_isdst else time.timezone)
            check_time = workgroup_last_check
            # %2B is +, %2D is -
            check_time += ".000Z" if timezone == 0 else ".000%2B" if timezone > 0 else ".000%2D"
            check_time += time.strftime("%H:%M", time.gmtime(abs(timezone)))
        
            count = 10
            offset = 0
            filters = '{"limit":'+str(count) + ', "offset":' + str(offset) + ',"'+project_filter+'":"' + check_time + '"}'
            #filters = urllib.quote_plus(filters)
            
            requestUrl = self.nooshApiUrl + "/workgroups/" + workgroup_id + "/projects?access_token=" + self.accessToken + "&filters=" + filters
            #print requestUrl
            retries = 0
            done = False
            while not done:
                try:
                    nooshResponse = requests.get(requestUrl)
                    r = nooshResponse.json()
                    done = True
                except:
                    # try again in a few seconds
                    self.logger.error(traceback.format_exc())
                    self.logger.error('going to try again in 30 seconds')
                    time.sleep(30)
                    
            while r['status_code'] == 200:
                projects = r['results']
                for i in range(len(projects)):
                    #print 'COLIN>>>>>: project\n'+json.dumps(projects[i], indent=3)
                    self.processProject(workgroup_last_check, workgroup, projects[i], project_filter, send_email)
                offset += count
                filters = '{"limit":'+str(count) + ', "offset":' + str(offset) + ',"'+project_filter+'":"' + check_time + '"}'
                #filters = urllib.quote_plus(filters)
                
                requestUrl = self.nooshApiUrl + "/workgroups/" + workgroup_id + "/projects?access_token=" + self.accessToken + "&filters=" + filters
                try:
                    nooshResponse = requests.get(requestUrl)
                    r = nooshResponse.json()
                except:
                    # try again in a few seconds
                    self.logger.error(traceback.format_exc())
                    self.logger.error('going to try again in 10 seconds')
                    time.sleep(10)

            ok = True
        except:
            self.logger.error('Problem getting projects data from Noosh')
            self.logger.error(traceback.format_exc())
            ok = False
        return ok
