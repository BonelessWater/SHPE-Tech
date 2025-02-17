Set objShell = CreateObject("WScript.Shell")
objShell.SendKeys "%{TAB}"
Set objShell = CreateObject("WScript.Shell")

If WScript.Arguments.Count > 0 Then
    If LCase(WScript.Arguments(0)) = "/reverse" Then
        ' Send Alt+Shift+Tab for reverse tab switching.
        objShell.SendKeys "%+{TAB}"
    Else
        ' Default: send Alt+Tab.
        objShell.SendKeys "%{TAB}"
    End If
Else
    ' No argument provided: send Alt+Tab.
    objShell.SendKeys "%{TAB}"
End If
