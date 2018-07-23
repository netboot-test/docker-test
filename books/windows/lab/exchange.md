# Exchange

![exchange-banner](../../assets/img/windows/lab/exchange-banner.png#banner)

## Introduction

Cet article montre comment créer un serveur Exchange dans le cadre de l'élaboration d'une infrastructure de Test.

Pour le deploiement du serveur **Exchange** nous utiliserons **Powershell DSC** ce qui vous permettra d'avoir une certaine consistance sur la configuration du rôle contrairement a l'opération via l'interface Graphique.

## Configuration de l'environnement

Avant de pouvoir effectuer la configuration de ce serveur, Assurez vous d'avoir un serveur Active Directory Préalablement installer ainsi qu'une Autorité de Certification afin de pouvoir fournir du **SSL**

Afin de pouvoir effectuer l'instalation du serveur exhange installer les mises à jour du serveur, car nous avons besoin de la mise à jour [KB3206632](http://www.catalog.update.microsoft.com/Search.aspx?q=KB3206632) pour pouvoir effectuer l'installation du serveur Exchange 2016.

Pour finir télécharger les ressources ci-dessous qui vous serons utiles pour le lancement de la configuration.

- [Unified Communications Managed API 5.0 Runtime](http://www.catalog.update.microsoft.com/Search.aspx?q=KB3206632)
- Iso de Exchange 2016

### Systeme

Avant de pouvoir effectuer la configuration de ce serveur, je vous invite à effectuer quelques configurations système à l'aide de Powershell. Ce qui aura pour effet de féfinir les paramètres de la carte réseaux & de rejoindre votre domaine Active Directory.

``` Powershell
# Set Network configuration
$NetAdapter = Get-NetAdapter
$NetAdapter | New-NetIPAddress -IPAddress 172.16.10.15 -PrefixLength 24 -DefaultGateway 172.16.10.10
$NetAdapter | Set-DNSClientServerAddress -ServerAddresses 172.16.10.12, 172.16.10.13

# Rename computer and join to domain
Add-Computer -DomainName "Netboot.lab" -Credential (get-credential) -NewName SRV-EXCH01

# Restart
restart-computer
```

## Installation

A l'aide de [Powershell DSC](/powershell/desired-state-configuration/introduction) nous allons effectuer la configuration de votre serveur Exchange. La configuration que je vous partage peu être exécutées directement sur le serveur ou bien via un [Serveur Pull]().


### Prérequis

Avant de pouvoir effectuer l'exécution de cette configuration, vous allez devoir effectuer l'installation de quelques modules Powershell DSC a l'aide de la commande ci-dessous.

``` Powershell
PS> Install-Module xPSDesiredStateConfiguration, xStorage, xexchange, xPendingReboot, xComputerManagement, xActiveDirectory
```

######## IMG  ########

La configuration ci-dessous va chercher les ressources précèdament télécharger sur un serveur de fichier, donc je vous invite a faire de méme afin de rendre les futurs installations automatique.

######## IMG ########

#### Configuration

La configuration ci-dessous vous permettra d'effectuer automatiquement les tâches suivantes :

- **Installation des fonctionnalités** : NET-Framework-45-Features, NET-WCF-HTTP-Activation45, RPC-over-HTTP-proxy, RSAT-Clustering, RSAT-Clustering-CmdInterface, RSAT-Clustering-Mgmt, RSAT-Clustering-PowerShell, Web-Mgmt-Console, WAS-Process-Model, Web-Asp-Net45, Web-Basic-Auth, Web-Client-Auth, Web-Digest-Auth, Web-Dir-Browsing, Web-Dyn-Compression, Web-Http-Errors, Web-Http-Logging, Web-Http-Redirect, Web-Http-Tracing, Web-ISAPI-Ext, Web-ISAPI-Filter, Web-Lgcy-Mgmt-Console, Web-Metabase, Web-Mgmt-Service, Web-Net-Ext45, Web-Request-Monitor, Web-Server, Web-Stat-Compression, Web-Static-Content, Web-Windows-Auth, Web-WMI, Windows-Identity-Foundation, RSAT-ADDS
- **Installation** de «Unified Communications Managed API 5.0 Runtime»
- **Preparation** du schéma Active Directory
- **Preparertion** de l'active Directory
- **Installation** du serveur Exchange 2016

Vous noterez que dans cette configuration on utilise le mode «**ApplyOnly**» ce qui permet d'éviter de rejouer la configuration toutes les 15 minutes.

``` Powershell
Configuration SetupExchange
{
    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName xComputerManagement
    Import-DscResource -ModuleName xPendingReboot
    Import-DscResource -ModuleName xStorage
    Import-DscResource -ModuleName xExchange

    Node $AllNodes.NodeName {
        # Assemble the Domain Admin Credentials
        if ($Node.DomainAdminPassword) {
            [PSCredential]$DomainAdminCredential = New-Object System.Management.Automation.PSCredential ("$($Node.DomainName)\$($Node.DomainAdminName)", (ConvertTo-SecureString $Node.DomainAdminPassword -AsPlainText -Force))
        }

        # Local Configuration Manager
        LocalConfigurationManager
        {
            ActionAfterReboot = 'ContinueConfiguration'
            ConfigurationMode = 'ApplyOnly'
            RebootNodeIfNeeded = $true
        }

        # Windows feature list
        $WindowsFeatures =@('NET-Framework-45-Features', 'NET-WCF-HTTP-Activation45', 'RPC-over-HTTP-proxy', 'RSAT-Clustering', 'RSAT-Clustering-CmdInterface',
                            'RSAT-Clustering-Mgmt', 'RSAT-Clustering-PowerShell', 'Web-Mgmt-Console', 'WAS-Process-Model', 'Web-Asp-Net45',
                            'Web-Basic-Auth', 'Web-Client-Auth', 'Web-Digest-Auth', 'Web-Dir-Browsing', 'Web-Dyn-Compression',
                            'Web-Http-Errors', 'Web-Http-Logging', 'Web-Http-Redirect', 'Web-Http-Tracing', 'Web-ISAPI-Ext',
                            'Web-ISAPI-Filter', 'Web-Lgcy-Mgmt-Console', 'Web-Metabase', 'Web-Mgmt-Service', 'Web-Net-Ext45',
                            'Web-Request-Monitor', 'Web-Server', 'Web-Stat-Compression', 'Web-Static-Content', 'Web-Windows-Auth',
                            'Web-WMI', 'Windows-Identity-Foundation', 'RSAT-ADDS')

        # Install windows feature
        ForEach($WindowsFeature in $WindowsFeatures)
        {
            WindowsFeature $WindowsFeature
            {
                Ensure = 'Present'
                Name = $WindowsFeature
            }
        }

        # Installs UCMA
        # To get ProductID : Get-WmiObject -Class Win32_Product | Format-Table IdentifyingNumber, Name
        Package UCMA
        {
            Ensure    = 'Present'
            Name      = 'Microsoft Unified Communications Managed API 4.0, Core Runtime 64-bit'
            Path      = (Join-Path -Path $Node.StoragePath -ChildPath $Node.FileUcma)
            ProductID = '695AFCA7-AB8E-4C47-BD3F-FB889700377C'
            Arguments = '/q'
        }

        # Checks if a reboot is needed before installing Exchange
        xPendingReboot BeforeExchangeInstall
        {
            Name = "BeforeExchangeInstall"
        }

        # Mount Exchange ISO
        xMountImage MountISO
        {
            ImagePath   = (Join-Path -Path $Node.StoragePath -ChildPath $Node.FileExchange)
            DriveLetter = 'S'
        }

        xWaitForVolume WaitForISO
        {
            DriveLetter      = 'S'
            RetryIntervalSec = 5
            RetryCount       = 10
        }


        if($Node.PrepareAD -eq $true)
        {
            # Prepare AD
            xExchInstall PrepareSchema
            {
                Path       = "S:\Setup.exe"
                Arguments  = "/PrepareSchema /IAcceptExchangeServerLicenseTerms"
                Credential = $DomainAdminCredential
                DependsOn  = '[xWaitForVolume]WaitForISO'
            }

            xExchInstall PrepareAD
            {
                Path       = "S:\Setup.exe"
                Arguments  = "/PrepareAD /Iacceptexchangeserverlicenseterms /OrganizationName:""$($Node.Netbios)"" "
                Credential = $DomainAdminCredential
                DependsOn  = '[xWaitForVolume]WaitForISO'
            }
        }

        # Does the Exchange install. Verify directory with exchange binaries
        xExchInstall InstallExchange
        {
            Path       =  "S:\Setup.exe"
            Arguments  = "/mode:Install /Iacceptexchangeserverlicenseterms /role:Mailbox /OrganizationName:""$($Node.Netbios)"" /TargetDir:""$($Node.TargetDir)"" /LogFolderPath:""$($Node.LogFolderdir)"" /DbFilePath:""$($Node.DbFilePath)"" "
            Credential = $DomainAdminCredential
            DependsOn  = '[xWaitForVolume]WaitForISO'
        }
    }
}

```

#### Initialisation

Vous trouverez ci-dessous deux exemples de paramétrage vous permettant de lancer le processus de configuration de votre serveur exchange


``` Powershell
# Parameters
$Configs = @{
    AllNodes = @(
        @{
            NodeName                    = "localhost"
            # Domain
            Netbios                     = "NETBOOT"
            DomainAdminName             = "Administrator"
            DomainAdminPassword         = "P@ssw0rd!"
            # File
            FileExchange                = "SW_DVD9_Exchange_Svr_2016_MultiLang_-6_Std_Ent_MLF_X21-40135.ISO"
            FileUcma                    = "UcmaRuntimeSetup.exe"
            StoragePath                 = "\\srv-ad01\src\"
            # Setup
            PrepareAD                   = $True
            TargetDir                   = "C:\Exchange Server\V15"
            LogFolderDir                = "C:\Exchange Log\"
            DbFilePath                  = "C:\Exchange DB\MyfirstDatabase.dbo"
            # Allow plain password
            PsDscAllowPlainTextPassword = $True
        }
    )
}

# Create Mof configuration
SetupExchange -ConfigurationData $Configs

# Make sure that LCM is set to continue configuration after reboot
Set-DSCLocalConfigurationManager -Path .\SetupExchange –Verbose

# Build the domain
Start-DscConfiguration -Wait -Force -Path .\SetupExchange -Verbose
```

#### Monitoring Install Progress

Je vous presente ici plusieurs methodes afin de connaitre l'état d'avancement de l'instalation de votre serveur Exchange.


##### Observateur d'évènements

##### Echange Logs

##### Module xDscDiagnostics

Voici une autreaproche
Une autre methode pour déterminer ce que fais xxxxxxx, consiste à utiliser le module [xDscDiagnostics](https://www.powershellgallery.com/packages/xDscDiagnostics/).

Si vous installez Exchange à l'aide d'un serveur de récupération DSC ou si vous rencontrez Behavior 1 par le dessus, il peut être difficile de dire exactement ce qui se passe avec la ressource xExchInstall. Voici différentes approches que vous pouvez utiliser pour déterminer si l'installation d'Exchange est en cours d'exécution et si elle a rencontré des problèmes.