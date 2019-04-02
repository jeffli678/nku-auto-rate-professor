import httplib
import re
import os
from wxPython.wx import *

class MyFrame(wxFrame):
    def __init__(self, parent, ID, title, pos=wxDefaultPosition,
                 size=(280, 380), style=wxDEFAULT_FRAME_STYLE):
        wxFrame.__init__(self, parent, ID, title, pos, size, style)
        self.panel = wxPanel(self, -1)
        
        label_id=wxStaticText(self.panel,1008,"Student ID:")
        label_id.SetPosition(wxPoint(15, 15))
        label_psw=wxStaticText(self.panel,1009,"Password:")
        label_psw.SetPosition(wxPoint(15, 65))
        label_val=wxStaticText(self.panel,1010,"Validate Code:")
        label_val.SetPosition(wxPoint(15, 165))
        
        self.text_id=wxTextCtrl(self.panel,1005)
        self.text_id.SetPosition(wxPoint(120, 15))
        self.text_psw=wxTextCtrl(self.panel,1006)
        self.text_psw.SetPosition(wxPoint(120, 65))
        self.text_val=wxTextCtrl(self.panel,1007)
        self.text_val.SetPosition(wxPoint(120, 165))
        
        button = wxButton(self.panel, 1003, "�˳�")
        button.SetPosition(wxPoint(120, 215))
        EVT_BUTTON(self, 1003, self.OnCloseMe)
        EVT_CLOSE(self, self.OnCloseWindow)

        self.button = wxButton(self.panel, 1004, "����")
        self.button.SetPosition(wxPoint(30, 215))
        EVT_BUTTON(self, 1004, self.OnPressMe)

        #get cookie
        conn=httplib.HTTPConnection("222.30.32.10")
        conn.request("GET","/")
        res=conn.getresponse()
        self.cookie=res.getheader("Set-Cookie")
        conn.close()
        self.headers= {"Content-Type":"application/x-www-form-urlencoded","Cookie":self.cookie}
        #get ValidateCode
        conn=httplib.HTTPConnection("222.30.32.10")
        conn.request("GET","/ValidateCode","",self.headers)
        res=conn.getresponse()
        f=open("ValidateCode.jpg","w+b")
        f.write(res.read())
        f.close()
        conn.close()

        image=wxImage("ValidateCode.jpg",wxBITMAP_TYPE_JPEG)
        val=wxStaticBitmap(self.panel,bitmap=image.ConvertToBitmap())
        val.SetPosition(wxPoint(15, 115))

    def OnCloseMe(self, event):
        self.Close(True)

    def OnPressMe(self, event):
        #��ʾ���Ժ�
        self.button.SetLabel("���Ժ�")
        
        stu_id=self.text_id.GetValue()
        psw=self.text_psw.GetValue()
        val=self.text_val.GetValue()
        params="operation=&usercode_text="+stu_id+"&userpwd_text="+psw+"&checkcode_text="+val+"&submittype=%C8%B7+%C8%CF"
        conn=httplib.HTTPConnection("222.30.32.10")
        conn.request("POST","/stdloginAction.do",params,self.headers);
        res=conn.getresponse()
        conn.close()
        conn=httplib.HTTPConnection("222.30.32.10")
        conn.request("GET","/evaluate/stdevatea/queryCourseAction.do","",self.headers);
        res=conn.getresponse()
        content=res.read()
        num=int(re.findall(r"�� ([0-9]*) ��",content)[0])
        conn.close()
        failcount=0
        for i in range(num):
            conn=httplib.HTTPConnection("222.30.32.10")
            conn.request("GET","/evaluate/stdevatea/queryTargetAction.do?operation=target&index="+str(i),"",self.headers);
            res=conn.getresponse()
            content=res.read()
            content=content.replace("�ý�ʦ���������ӡ��","�ý�ʦ���������ӡ��10��")
            #��������
            item=re.findall(r"��([0-9]*)��",content)
            conn.close()
            #submit
            conn=httplib.HTTPConnection("222.30.32.10")
            params="operation=Store"
            
            for j in range(len(item)):  params+=("&array["+str(j)+"]="+item[j])
            params+="&opinion="
            self.headers= {"Content-Type":"application/x-www-form-urlencoded"
                  ,"Cookie":self.cookie,"Referer":"http://222.30.32.10/evaluate/stdevatea/queryTargetAction.do?operation=target&index="+str(i)}
            conn.request("POST","/evaluate/stdevatea/queryTargetAction.do",params,self.headers);
            rescontent=conn.getresponse().read()
            if -1==rescontent.find("�ɹ����棡"):failcount+=1
            conn.close()
        #��ʾ�ɹ�
        s="���!\n�ܹ�: %d\n�ɹ�: %d" % (num,num-failcount)
        self.label_status=wxStaticText(self.panel,1008,s)
        self.label_status.SetPosition(wxPoint(50, 265))    
        os.remove("ValidateCode.jpg")
        
    def OnCloseWindow(self, event):
        self.Destroy()

class MyApp(wxApp):
    def OnInit(self):
        frame = MyFrame(NULL, -1, "һ������ by Jeff")
        frame.Show(true)
        self.SetTopWindow(frame)
        return true

app = MyApp(0)
app.MainLoop()
