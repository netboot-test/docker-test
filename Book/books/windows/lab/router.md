# Routeur

![router-banner](../../assets/img/windows/lab/router-banner.png#banner)

## Introduction

Dans ce chapitre nous allons voir ensemble comment configurer rapidement un **Routeur** à l'aide d'un serveur windows et de **Powershell**.

Ce serveur nous permettra d'isoler notre laboratoire de votre réseau principal, ce qui vous évitera bien des problèmes 😅

## Configuration

### Systeme

Configuration réseaux de la machine virtuelle.

``` Powershell
# Set Network configuration
$Interfaces =  Get-NetIPAddress -AddressFamily IPV4 | where-object {$_.InterfaceAlias -like "Ethernet*"}
$Lan = $Interfaces | where-object {$_.PrefixOrigin -ne 'DHCP'}
$Wan = $Interfaces | where-object {$_.PrefixOrigin -eq 'DHCP'}
Get-NetAdapter -InterfaceIndex $Lan.InterfaceIndex | New-NetIPAddress -IPAddress 172.16.10.254 -PrefixLength 24
Get-NetAdapter -InterfaceIndex $Lan.InterfaceIndex | Set-DNSClientServerAddress -ServerAddresses 172.16.10.12, 172.16.10.13
Get-NetAdapter -InterfaceIndex $Lan.InterfaceIndex | Rename-NetAdapter -NewName "Lan"
Get-NetAdapter -InterfaceIndex $Wan.InterfaceIndex | Rename-NetAdapter -NewName "Wan"

# Rename computer and join to domain
Add-Computer -DomainName "Netboot.lab" -Credential (get-credential) -NewName SRV-RTR

# Restart
restart-computer
```

### Role

Installation & Configuration du role de routage.
``` Powershell
# Install Windows Feature
install-WindowsFeature Routing -IncludeManagementTools

# Restart
restart-computer
```

``` Powershell
Install-RemoteAccess -VpnType Vpn

$ExternalInterface="Wan"
$InternalInterface="Lan"

cmd.exe /c "netsh routing ip nat install"
cmd.exe /c "netsh routing ip nat add interface $ExternalInterface"
cmd.exe /c "netsh routing ip nat set interface $ExternalInterface mode=full"
cmd.exe /c "netsh routing ip nat add interface $InternalInterface"
```

## Note du Chef

Je recommande vivement d'utiliser pour cette machine virtuelle la version CORE de Windows Serveur, ceci apportera les bénéfices suivant :

- Réduction de la **consommation** CPU/RAM
- Surface d'attaque plus petite
- Moins de Mise à jour
- Amélioration de votre maitrise de **Powershell**

Un bon **Administrateur** se doit de jamais se connecter directement sur le serveur cible, **Microsoft** fournit un large panel d'outil d'administration ( RSAT, Server Manager, Powershell, etc.) vous permetant d'effectuer toutes les taches quotidiennes sans utiliser le bureau a distance.