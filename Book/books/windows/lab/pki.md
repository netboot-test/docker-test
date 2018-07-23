# Pki Microsoft

![pki-banner](../../assets/img/windows/lab/pki-banner.png#banner)

## Introduction

Dans ce chapitre nous allons voir ensemble comment configurer rapidement une infrastructure PKI à l'aide de **Powershell**.

## Configuration

### Systeme

Configuration réseaux de la machine virtuelle

``` Powershell
# Set Network configuration
$NetAdapter = Get-NetAdapter
$NetAdapter | New-NetIPAddress -IPAddress 172.16.10.14 -PrefixLength 24 -DefaultGateway 172.16.10.10
$NetAdapter | Set-DNSClientServerAddress -ServerAddresses 172.16.10.12, 172.16.10.13

# Rename computer and join to domain
Add-Computer -DomainName "Netboot.lab" -Credential (get-credential) -NewName SRV-PKI

# Restart
restart-computer
```

### Role

Installation & Configuration d'une pki Microsoft

``` Powershell
Install-WindowsFeature ADCS-Cert-Authority

$Params = @{
    CAType = "EnterpriseRootCA"
    CACommonName = "netboot-CA"
    KeyLength = "4096"
    HashAlgorithmName = "SHA256"
    ValidityPeriod = "Years"
    ValidityPeriodUnits = "5"
    Verbose = $true
    Force = $true
}
Install-AdcsCertificationAuthority @Params
```




``` Powershell
Install-PackageProvider -Name NuGet -Force
Install-Module xComputerManagement, xAdcsDeployment, xPSDesiredStateConfiguration, xComputerManagement, xFirewall -force
```


``` Powershell
Configuration SetupMemberRootCA
{
    Import-DscResource -ModuleName PSDesiredStateConfiguration
    Import-DscResource -ModuleName xAdcsDeployment
    Import-DscResource -ModuleName xComputerManagement


    Node $AllNodes.NodeName {

        # Assemble the Local Admin Credentials
        if ($Node.DomainAdminPassword)
        {
            [PSCredential]$DomainAdminCredential = New-Object System.Management.Automation.PSCredential ("$($Node.DomainName)\Administrator", (ConvertTo-SecureString $Node.DomainAdminPassword -AsPlainText -Force))
        }

        # Setup Local Configuration Manager
        LocalConfigurationManager
        {
            ActionAfterReboot = 'ContinueConfiguration'
            ConfigurationMode = 'ApplyOnly'
            RebootNodeIfNeeded = $true
        }

        # Wait for the Domain to be available so we can join it.
        WaitForAll DC
        {
            ResourceName     = '[xADDomain]PrimaryDC'
            NodeName         = $Node.DomainName
            RetryIntervalSec = 15
            RetryCount       = 60
        }

        # Join this Server to the Domain
        xComputer JoinDomain
        {
            Name       = $Node.NodeName
            DomainName = $Node.DomainName
            Credential = $DomainAdminCredential
            DependsOn  = "[WaitForAll]DC"
        }

        # Install the CA Service
        WindowsFeature ADCSCA
        {
            Name   = 'ADCS-Cert-Authority'
            Ensure = 'Present'
        }

        # Install the Web Enrollment Service
        WindowsFeature ADCSWebEnrollment
        {
            Name      = 'ADCS-Web-Enrollment'
            Ensure    = 'Present'
            DependsOn = "[WindowsFeature]ADCSCA"
        }

        WindowsFeature InstallWebMgmtService
        {
            Ensure    = "Present"
            Name      = "Web-Mgmt-Service"
            DependsOn = '[WindowsFeature]ADCSWebEnrollment'
        }

        if ($InstallRSATTools -eq $true)
        {
            WindowsFeature RSAT-ManagementTools
            {
                Ensure    = "Present"
                Name      = "RSAT-AD-Tools"
                DependsOn = "[WindowsFeature]ADCSCA"
            }
        }

        # Install the Online Responder Service
        if ($Node.InstallOnlineResponder -eq $true)
        {
            WindowsFeature OnlineResponderCA
            {
                Name      = 'ADCS-Online-Cert'
                Ensure    = 'Present'
                DependsOn = "[WindowsFeature]ADCSCA"
            }
        }

        # Install the Enrollment Web Service/Enrollment Policy Web Service
        if ($Node.InstallEnrollmentWebService -eq $true)
        {
            WindowsFeature EnrollmentWebSvc
            {
                Name      = 'ADCS-Enroll-Web-Svc'
                Ensure    = 'Present'
                DependsOn = "[WindowsFeature]ADCSCA"
            }

            WindowsFeature EnrollmentWebPol
            {
                Name      = 'ADCS-Enroll-Web-Pol'
                Ensure    = 'Present'
                DependsOn = "[WindowsFeature]ADCSCA"
            }
        }

        # Create the CAPolicy.inf file that sets basic parameters for certificate issuance for this CA.
        File CAPolicy
        {
            Ensure          = 'Present'
            DestinationPath = 'C:\Windows\CAPolicy.inf'
            Contents        = "[Version]`r`n Signature= `"`$Windows NT$`"`r`n[Certsrv_Server]`r`n DiscreteSignatureAlgorithm=1`r`n HashAlgorithm=RSASHA256`r`n RenewalKeyLength=4096`r`n RenewalValidityPeriod=Years`r`n RenewalValidityPeriodUnits=20`r`n CRLDeltaPeriod=Days`r`n CRLDeltaPeriodUnits=0`r`n[CRLDistributionPoint]`r`n[AuthorityInformationAccess]`r`n"
            Type            = 'File'
            DependsOn       = '[xComputer]JoinDomain'
        }

        # Make a CertEnroll folder to put the Root CA certificate into.
        # The CA Web Enrollment server would also create this but we need it now.
        File CertEnrollFolder
        {
            Ensure          = 'Present'
            DestinationPath = 'C:\Windows\System32\CertSrv\CertEnroll'
            Type            = 'Directory'
            DependsOn       = '[File]CAPolicy'
        }

        # Configure the Root CA which will create the Certificate REQ file that Root CA will use
        # to issue a certificate for this Sub CA.
        xADCSCertificationAuthority ConfigCA
        {
            Ensure                    = 'Present'
            Credential                = $DomainAdminCredential
            CAType                    = 'EnterpriseRootCA'
            CACommonName              = $Node.CACommonName
            CADistinguishedNameSuffix = $Node.CADistinguishedNameSuffix
            OverwriteExistingCAinDS   = $True
            CryptoProviderName        = 'RSA#Microsoft Software Key Storage Provider'
            HashAlgorithmName         = 'SHA256'
            KeyLength                 = 4096
            DependsOn                 = '[File]CertEnrollFolder'
        }

        # Configure the Web Enrollment Feature
        xADCSWebEnrollment ConfigWebEnrollment {
            Ensure           = 'Present'
            IsSingleInstance = 'Yes'
            CAConfig         = 'CertSrv'
            Credential       = $DomainAdminCredential
            DependsOn        = '[xADCSCertificationAuthority]ConfigCA'
        }

        # Perform final configuration of the CA which will cause the CA service to startup
        # Set the advanced CA properties
        Script ADCSAdvConfig
        {
            SetScript  = {
                if ($Using:Node.CADistinguishedNameSuffix)
                {
                    & "$($ENV:SystemRoot)\system32\certutil.exe" -setreg CA\DSConfigDN "CN=Configuration,$($Using:Node.CADistinguishedNameSuffix)"
                    & "$($ENV:SystemRoot)\system32\certutil.exe" -setreg CA\DSDomainDN "$($Using:Node.CADistinguishedNameSuffix)"
                }
                if ($Using:Node.CRLPublicationURLs)
                {
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\CRLPublicationURLs $($Using:Node.CRLPublicationURLs)
                }
                if ($Using:Node.CACertPublicationURLs)
                {
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\CACertPublicationURLs $($Using:Node.CACertPublicationURLs)
                }
                if ($Using:Node.CRLPeriodUnits)
                {
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\CRLPeriodUnits $($Using:Node.CRLPeriodUnits)
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\CRLPeriod "$($Using:Node.CRLPeriod)"
                }
                if ($Using:Node.CRLOverlapUnits)
                {
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\CRLOverlapUnits $($Using:Node.CRLOverlapUnits)
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\CRLOverlapPeriod "$($Using:Node.CRLOverlapPeriod)"
                }
                if ($Using:Node.ValidityPeriodUnits)
                {
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\ValidityPeriodUnits $($Using:Node.ValidityPeriodUnits)
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\ValidityPeriod "$($Using:Node.ValidityPeriod)"
                }
                if ($Using:Node.AuditFilter)
                {
                    & "$($ENV:SystemRoot)\System32\certutil.exe" -setreg CA\AuditFilter $($Using:Node.AuditFilter)
                }
                Restart-Service -Name CertSvc
            }
            GetScript  = {
                Return @{
                    'DSConfigDN'            = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('DSConfigDN');
                    'DSDomainDN'            = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('DSDomainDN');
                    'CRLPublicationURLs'    = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLPublicationURLs');
                    'CACertPublicationURLs' = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CACertPublicationURLs')
                    'CRLPeriodUnits'        = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLPeriodUnits')
                    'CRLPeriod'             = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLPeriod')
                    'CRLOverlapUnits'       = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLOverlapUnits')
                    'CRLOverlapPeriod'      = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLOverlapPeriod')
                    'ValidityPeriodUnits'   = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('ValidityPeriodUnits')
                    'ValidityPeriod'        = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('ValidityPeriod')
                    'AuditFilter'           = (Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('AuditFilter')
                }
            }
            TestScript = {
                if (((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('DSConfigDN') -ne "CN=Configuration,$($Using:Node.CADistinguishedNameSuffix)"))
                {
                    Return $False
                }
                if (((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('DSDomainDN') -ne "$($Using:Node.CADistinguishedNameSuffix)"))
                {
                    Return $False
                }
                if (($Using:Node.CRLPublicationURLs) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLPublicationURLs') -ne $Using:Node.CRLPublicationURLs))
                {
                    Return $False
                }
                if (($Using:Node.CACertPublicationURLs) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CACertPublicationURLs') -ne $Using:Node.CACertPublicationURLs))
                {
                    Return $False
                }
                if (($Using:Node.CRLPeriodUnits) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLPeriodUnits') -ne $Using:Node.CRLPeriodUnits))
                {
                    Return $False
                }
                if (($Using:Node.CRLPeriod) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLPeriod') -ne $Using:Node.CRLPeriod))
                {
                    Return $False
                }
                if (($Using:Node.CRLOverlapUnits) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLOverlapUnits') -ne $Using:Node.CRLOverlapUnits))
                {
                    Return $False
                }
                if (($Using:Node.CRLOverlapPeriod) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('CRLOverlapPeriod') -ne $Using:Node.CRLOverlapPeriod))
                {
                    Return $False
                }
                if (($Using:Node.ValidityPeriodUnits) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('ValidityPeriodUnits') -ne $Using:Node.ValidityPeriodUnits))
                {
                    Return $False
                }
                if (($Using:Node.ValidityPeriod) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('ValidityPeriod') -ne $Using:Node.ValidityPeriod))
                {
                    Return $False
                }
                if (($Using:Node.AuditFilter) -and ((Get-ChildItem 'HKLM:\System\CurrentControlSet\Services\CertSvc\Configuration').GetValue('AuditFilter') -ne $Using:Node.AuditFilter))
                {
                    Return $False
                }
                Return $True
            }
            DependsOn  = '[xADCSWebEnrollment]ConfigWebEnrollment'
        }
    }
}
```











``` Powershell
# Parameters
$Configs = @{
    AllNodes = @(
        @{
            NodeName                    = "localhost"
            DomainName                  = "Netboot.Lab"
            DomainAdminPassword         = "Desmo4ever"
            #
            CACommonName = "Netboot.Lab Root CA"
            CADistinguishedNameSuffix = "DC=Netboot,DC=Lab"
            CRLPublicationURLs = "65:C:\Windows\system32\CertSrv\CertEnroll\%3%8%9.crl\n79:ldap:///CN=%7%8,CN=%2,CN=CDP,CN=Public Key Services,CN=Services,%6%10\n6:http://pki.netboot.lab/CertEnroll/%3%8%9.crl"
            CACertPublicationURLs = "1:C:\Windows\system32\CertSrv\CertEnroll\%1_%3%4.crt\n2:ldap:///CN=%7,CN=AIA,CN=Public Key Services,CN=Services,%6%11\n2:http://pki.netboot.lab/CertEnroll/%1_%3%4.crt"
            CRLPeriodUnits = 52
            CRLPeriod = 'Weeks'
            CRLOverlapUnits = 12
            CRLOverlapPeriod = 'Hours'
            ValidityPeriodUnits = 10
            ValidityPeriod = 'Years'
            AuditFilter = 127
            #
            InstallEnrollmentWebService = $true
            InstallOnlineResponder = $true
            InstallRSATTools = $true
            PsDscAllowPlainTextPassword = $True
        }
    )
}

# Create Mof configuration
SetupMemberRootCA -ConfigurationData $Configs

# Make sure that LCM is set to continue configuration after reboot
Set-DSCLocalConfigurationManager -Path .\SetupMemberRootCA –Verbose

# Build the domain
Start-DscConfiguration -Wait -Force -Path .\SetupMemberRootCA -Verbose
```

## Note du Chef

Je recommande vivement d'utiliser pour cette machine virtuelle la version CORE de Windows Serveur, ceci apportera les bénéfices suivant :

- Réduction de la **consommation** CPU/RAM
- Surface d'attaque plus petite
- Moins de Mise à jour
- Amélioration de votre maitrise de **Powershell**

Un bon **Administrateur** se doit de jamais se connecter directement sur le serveur cible, **Microsoft** fournit un large panel d'outil d'administration ( RSAT, Server Manager, Powershell, etc.) vous permetant d'effectuer toutes les taches quotidiennes sans utiliser le bureau a distance.