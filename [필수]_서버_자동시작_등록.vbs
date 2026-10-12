Set WshShell = CreateObject("WScript.Shell")
Set oXML = CreateObject("MSXML2.DOMDocument.6.0")

taskXML = "<?xml version='1.0' encoding='UTF-16'?>" & vbCrLf & _
"<Task version='1.2' xmlns='http://schemas.microsoft.com/windows/2004/02/mit/task'>" & vbCrLf & _
"  <Triggers><LogonTrigger><Enabled>true</Enabled><Delay>PT1M</Delay></LogonTrigger></Triggers>" & vbCrLf & _
"  <Principals><Principal id='Author'><LogonType>InteractiveToken</LogonType><RunLevel>HighestAvailable</RunLevel></Principal></Principals>" & vbCrLf & _
"  <Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><ExecutionTimeLimit>PT0S</ExecutionTimeLimit><Priority>7</Priority></Settings>" & vbCrLf & _
"  <Actions Context='Author'>" & vbCrLf & _
"    <Exec>" & vbCrLf & _
"      <Command>pythonw</Command>" & vbCrLf & _
"      <Arguments>""C:\Users\zkfnt\Desktop\&#xD55C;&#xAD6D; &#xB9C8;&#xCF00;&#xD305;&#xBD07;\kmarket-marketing-engine\server.py""</Arguments>" & vbCrLf & _
"      <WorkingDirectory>C:\Users\zkfnt\Desktop\&#xD55C;&#xAD6D; &#xB9C8;&#xCF00;&#xD305;&#xBD07;\kmarket-marketing-engine</WorkingDirectory>" & vbCrLf & _
"    </Exec>" & vbCrLf & _
"  </Actions>" & vbCrLf & _
"</Task>"

' Save XML to temp file
Dim fso, f
Set fso = CreateObject("Scripting.FileSystemObject")
Set f = fso.CreateTextFile("C:\Users\zkfnt\AppData\Local\Temp\mktbot_task.xml", True, True)
f.Write taskXML
f.Close

' Register via schtasks
Dim cmd
cmd = "schtasks /create /tn ""한국마케팅봇_서버_자동시작"" /xml ""C:\Users\zkfnt\AppData\Local\Temp\mktbot_task.xml"" /f"
WshShell.Run "cmd /c " & cmd, 0, True

WScript.Echo "[완료] 자동시작 작업 스케줄러 등록 완료"
