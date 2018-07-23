# Invoke-VideoTroll

## Introduction

Parce que parfois, une journée de travail, c'est long, très long. Il arrive même qu'on s'ennuie (un peu, si peu). Une manière de tuer ce temps au travail, c'est de faire légèrement chier ses collègues 😇

Je vous propose alors une fonction **Powershell** qui permetra d'ouvrir **Internet Explorer** en tache de fond avec une video, sans oublier que cette fonction oblige l'ordinateur a garder le volume de l'ordinateur à **💯%**.

![invoke-videotroll-01](../../../assets/img/powershell/function-module/fun/invoke-videotroll-01.gif#center)

!!! danger
    Il est préférable de rester à **proximité** de votre collègue pour que la blague ne dure trop longtemps et qu'il/elle ne finisse pas par appeler la hotline, ce qui vous evitera bien des problèmes.

## Fonction

``` Powershell
Function Invoke-VideoTroll
{
    [CmdletBinding()]
    Param (
        [Parameter(Mandatory = $False, Position = 0)]
        [String] $URL = "https://www.youtube.com/watch?v=PUn4n-nGraM",
        [Parameter(Mandatory = $false, Position = 0)]
        [Int]$Duration = 90
    )
    Try {
        Function Set-Speaker($Volume){$wshShell = new-object -com wscript.shell;1..50 | % {$wshShell.SendKeys([char]174)};1..$Volume | % {$wshShell.SendKeys([char]175)}}
        Set-Speaker -Volume 50

        #Create hidden IE Com Object
        $IEComObject = New-Object -com "InternetExplorer.Application"
        $IEComObject.visible = $true
        $IEComObject.navigate($URL)

        Start-Sleep -s 5

        $EndTime = (Get-Date).addseconds($Duration)

        # ghetto way to do this but it basically presses volume up to raise volume in a loop for 90 seconds
        do {
            $WscriptObject = New-Object -com wscript.shell
            $WscriptObject.SendKeys([char]175)
        }
        until ((Get-Date) -gt $EndTime)
    }
    Catch {
        write-error "Error to load Video : $_"
    }
    Finally {
        $IEComObject.Parent.Quit()
    }
}
```

## Exemple

Vous trouverez ci-dessous un exemple d'utilisation de cette fonction.

``` Powershell
PS> Invoke-VideoTroll -URL "https://www.youtube.com/watch?v=PUn4n-nGraM" -Duration 90
```