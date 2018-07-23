# Invoke-FBBombLikes

## Introduction

C'est probablement la chose la plus insensée que vous puissiez faire avec Powershell, cette fonction permet de Like toutes les publications de l'un de vos amis 😅

![invoke-fbbomblikes-03](../../../assets/img/powershell/function-module/fun/invoke-fbbomblikes-03.gif#center)

## Fonction

``` Powershell
function Invoke-FBBombLikes {

    param(
        [Parameter(Mandatory = $true)]
        [String]$ProfileURL,
        [Parameter(Mandatory = $true)]
        [Int]$count,
        [Parameter(Mandatory = $false)]
        [Int]$Interval = 5
    )

    write-host "Opening Facebook Profile URL"
    $ie = New-Object -ComObject "InternetExplorer.application"
    $ie.Visible = $false
    $ie.Navigate("$ProfileURL")

    while ($ie.Busy -eq $true){
        # Wait for the page to load
        Start-Sleep -seconds 5;
    }

    $start = Get-Date;
    $VerticalScroll = 0

    Write-Host "Scrolling down for more likables"
    While((Get-Date) -lt $($start + [timespan]::new(0,0,$count))) {

        $ie.Document.parentWindow.scrollTo(0,$VerticalScroll)
        $VerticalScroll = $VerticalScroll + 100
    }

    Write-Host "Scroll done"

    $likes = $ie.Document.IHTMLDocument3_getElementsByTagName('a') | ? {$_.classname -eq "UFILikeLink _4x9- _4x9_ _48-k"}
    $like_count = $likes.Length

    $counter = 0
    Write-Host "Now the fun part, the liking!"
    foreach($item in $likes[0..$count]){
        $counter++;
        $item.click();
        Write-Progress -Activity "Liking Posts.." -CurrentOperation $item -PercentComplete (($counter / $likes[0..$count].count) * 100);
        sleep (get-random  -Minimum $Interval -Maximum ($Interval + 10))

    }

    write-host "Hahahah! Done!"
}
```

!!! info
    Avant de pouvoir exécuter cette fonction, connectez-vous avant sur Facebook avec Internet Explorer.

## Exemple

Vous trouverez ci-dessous un exemple d'utilisation de cette fonction.

``` Powershell
PS> Invoke-FBBombLikes -ProfileURL https://www.facebook.com/Profil -Count 100 -Interval 5
```

![invoke-fbbomblikes-01](../../../assets/img/powershell/function-module/fun/invoke-fbbomblikes-01.png#center)

![invoke-fbbomblikes-02](../../../assets/img/powershell/function-module/fun/invoke-fbbomblikes-02.png#center)