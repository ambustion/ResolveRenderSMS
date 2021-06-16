import smtplib
import os
import platform
import socket
import sys
import time
import configparser
import base64

ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

ScriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
configFile = os.path.join(ScriptDir,'sms.ini')
if os.path.exists(configFile):
    print("found config file")
else:
    print("no config file found")
    exit()
config = configparser.ConfigParser()
config.read(configFile)
carriers = {}
for item in config['carriers']:
    print(item)
    carriers.update({item:config['carriers'][item]})

print(carriers)

email = config['sms']['email']
phoneNumber = config['sms']['phoneNumber']
passwd = base64.b64decode(config['sms']['passwd']).decode("utf-8")
carrier = config['sms']['carrier']

setupBool = False





renamed = ""





project = resolve.GetProjectManager().GetCurrentProject()

def submitConfig(email,pw,phone,carrier):

    config['sms']['email'] = email
    config['sms']['phoneNumber'] = phone
    config['sms']['passwd'] = pw
    config['sms']['carrier'] = carrier

    with open(configFile, 'w') as configfile:
        config.write(configfile)

def initialSetup():
    dlg = disp.AddWindow({"WindowTitle": "SMSScript", "ID": "MyWin", "Geometry": [1000, 100, 200, 300], },
                         [
                             ui.VGroup({"Spacing": 2, },
                                       [
                                           # Add your GUI elements here:
                                           ui.Label({"ID": "Title", "Text": "Before you can use \n this sms script \n you must enter your\ncredentials", "setWordWrao": True,"Weight":0, "Alignment" : {"AlignHCenter" : True,"AlignTop" : True}}),
                                           ui.Label({"Text": "email", "Weight": 0.5}),
                                           ui.LineEdit({"ID": "email", "Text":""}),
                                           ui.VGap(0, .2),
                                           ui.Label({"Text": "password",
                                                     "Weight": 0.5}),
                                           ui.LineEdit({"ID": "Password", "Text": ""}),
                                           ui.VGap(0, .2),
                                           ui.Label({"Text": "Phone Number(5550001111)",
                                                     "Weight": 0.5}),
                                           ui.LineEdit({"ID": "Phone Number", "Text": ""}),
                                           ui.VGap(0, .2),
                                           ui.Label({"Text": "Carrier",
                                                     "Weight": 0.5}),
                                           ui.ComboBox({"ID": "Carrier", "Text": ""}),
                                           ui.VGap(0, .2),
                                           ui.Button({"ID": "Submit", "Text": "Submit"})


                                       ]),

                         ])
    itm = dlg.GetItems()
    itm['Password'].SetEchoMode('Password')
    for k in carriers.keys():
        #print(k)
        itm["Carrier"].AddItem(k)

    def _func(ev):
        email = itm["email"].Text
        print("email set as: " + email)
        pw = itm["Password"].Text
        pw = str(base64.b64encode(pw.encode('ascii')).decode("utf-8"))
        print("pw set as: " + str(pw))
        ph = itm["Phone Number"].Text
        print("phone set as: " + ph)
        ca = itm["Carrier"].CurrentText
        print("carrier set as: " + ca)
        submitConfig(email,pw,str(ph),ca)
        disp.ExitLoop()

    dlg.On.Submit.Clicked = _func
    def _func(ev):
        disp.ExitLoop()

    dlg.On.MyWin.Close = _func

    dlg.Show()
    disp.RunLoop()
    dlg.Hide()



def send(message):
    to_number = phoneNumber + carriers[carrier]
    print(to_number)
    auth = (email, passwd)

    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    # Send text message through SMS gateway of destination number
    server.sendmail(auth[0], to_number, message)

def renderwait(jobID, jobNum):
    while int(project.GetRenderJobStatus(jobID)['CompletionPercentage']) < 100:
        time.sleep(2)
        print(str(int(project.GetRenderJobStatus(jobID)['CompletionPercentage'])) + "is the render completion")
        print("waiting")
        if project.GetRenderJobStatus(jobID)['JobStatus'] == "Cancelled":
            break

    if project.GetRenderJobStatus(jobID)['JobStatus'] == "Complete":
        msg = jobNum + " is finished rendering in Davinci Resolve"
        print("sending message")
        send(msg)

if email == "" or phoneNumber == "" or passwd == "" or carrier == "":
    setupBool = False
    initialSetup()
time.sleep(1)

for x in project.GetRenderJobList():
    #print(x['JobId'])
    jobNum = x['RenderJobName']
    jobID = x['JobId']
    #print(project.GetRenderJobStatus(jobID))
    if project.GetRenderJobStatus(jobID)['JobStatus'] == "Rendering":
        #print("launching renderwait")
        renderwait(jobID, jobNum)

