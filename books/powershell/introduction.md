# Powershell

![introduction-banner](../assets/img/powershell/introduction-banner.png#banner)

## Introduction

Windows PowerShell comprend un interpréteur de commandes et un langage de script, conçu spécialement pour l'administration du système. Créé à partir de **Microsoft .NET Framework**, Windows PowerShell™ aide les professionnels de l’informatique et les utilisateurs chevronnés à contrôler et à **automatiser** l’administration du système d’exploitation Windows. Les commandes Windows PowerShell intégrées, appelées **cmdlets** (ou applets de commande), vous permettent de gérer les ordinateurs de votre entreprise à partir de la ligne de commande.

Les providers Windows PowerShell vous permettent d'accéder à des magasins de données, par exemple le Registre et le magasin de certificats, aussi facilement que si vous accédiez au système de fichiers.

## Objectif

L’objectif de ces recettes de ce chapitre est de vous faire découvrir un langage de scripts **orientés objet** sous un environnement Windows avec comme fil conducteur l’administration de machines et d’utilisateurs.


!!! info
    Les recettes ont été construites avec la version 4 & 5 de Powershell, ce qui peut expliquer un certain nombre de différences si vous utilisez des versions antérieures.


## Commande de base

Comme vous allez l’apercevoir, Windows PS introduit des commandes un peu spéciales appelées cmdlet (prononcer **« Command-let »**). Une cmdlet s'utilise de la même façon qu'une commande classique. Elle n’est pas sensitive à la casse. Elles respectent un format bien précis **<verbe>-<action>**. Le verbe précise ce que fait la cmdlet en général alors que le nom précise sur quoi la cmdlet va agir. Par exemple, la cmdlet Get-Variable va récupérer une variable de PS et retourner sa valeur.

### Verb

Vous trouverez ci-dessous un tableau des verbes les plus communs pour les cmdlets :

| Verbe                   | Signification                                                                                                                    |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Add                     | Ajoute une instance d'un item                                                                                                    |
| Clear                   | Supprime le contenu d'un item comme la valeur d'une variable                                                                     |
| ConvertFrom / ConvertTo | Convertis un item d'un format à un autre, comme une liste de valeurs séparées par des virgules en des propriétés d'un objet      |
| Disable / Enable        | Annule / autorise un certain paramétrage comme une connexion à distance                                                          |
| Export / Import         | Exporte / importe les propriétés d’un item dans un format particulier comme exporter les propriétés de la console en XML        |
| Get                     | Interroge un objet comme obtenir la liste des processus                                                                          |
| Invoke                  | Exécute une instance d’un item comme une expression                                                                             |
| New / Remove            | Crée / supprime une nouvelle instance d’un item, comme une nouvelle variable ou événement                                       |
| Set                     | Modifie les paramètres d’un objet                                                                                               |
| Start / Stop            | Démarre / arrête une instance d’un item comme un service ou un processus                                                        |
| Test                    | Test une instance d’un item pour une valeur spécifique comme tester une connexion pour savoir si elle est valide                |
| Write                   | Exécute une opération d’écriture d’une instance d’un objet comme écrire un événement sur le gestionnaire de log d’événements |

### Cmdlet

Afin d’avoir une idée plus précise de l’utilité des précédentes cmdlet, vous trouverez ci-dessous un tableau résumant les cmdlet souvent utilisés à des fins d’administration :

| Cmdlet                                                                        | Signification                                                                                  |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Add-Computer / Remove-Computer                                                | Ajoute ou supprime l’appartenance d’un ordinateur dans un domaine ou groupe de travail       |
| Checkpoint-Computer / Restore-Computer                                        | Créé un point de restauration du système pour un ordinateur / restaure l’ordinateur           |
| Compare-Object / Group-Object / SortObject / Select-Object / New-Object       | Comparaison / groupement / trie / sélection / création d’objets                               |
| ConvertFrom-SecureString / ConvertTo-SecureString                             | Création / export de chaines sécurisées                                                        |
| Debug-Process                                                                 | Déboguer un processus s’exécutant sur un ordinateur                                           |
| Get-Alias / New-Alias / Set-Alias / Export-Alias / Import-Alias               | Récupérer / créer / paramétrer / exporter / importer des alias                                 |
| Get-AuthenticodeSignature / Set-AuthenticodeSignature                         | Récupérer / paramétrer la signature d’un objet associé à un fichier                           |
| Get-Command / Invoke-Command / Measure-Command / Trace-Command                | Récupérer des informations sur / invoquer / mesurer le temps d’exécution / tracer des cmdlets |
| Get-EventLog / Write-EventLog / Clear-EventLog                                | Récupérer / écrire / effacer des événements de log                                             |
| Get-ExecutionPolicy / Set-ExecutionPolicy                                     | Traite de la politique d’exécution du shell courant                                           |
| Get-Help                                                                      | Devinez … ?                                                                                    |
| Get-Host                                                                      | Récupère des informations de l’application hôte de PS                                         |
| Get-Location / Set-Location                                                   | Affiche ou sélectionne le répertoire courant                                                   |
| Get-Process / Start-Process / StopProcess                                     | Récupère / Démarre / Arrête un processus sur une machine                                       |
| Get-PSDrive / New-PSDrive / RemovePSDrive                                     | Récupère / Crée / Supprime un disque spécifique PowerShell                                     |
| Get-Service / New-Service / Set-Service                                       | Récupère / Crée / Définit un service                                                           |
| Get-Variable / New-Variable / Set-Variable / Remove-Variable / Clear-Variable | Cmdlets pour la gestion des variables                                                          |
| Rename-Computer / Stop-Computer / Restart-Computer                            | Renomme / Arrête / Redémarre un ordinateur                                                     |
| Reset-ComputerMachinePassword                                                 | Réinitialise le mot de passe du compte de l'ordinateur                                         |

## Note du Chef

Pour effectuer un apprentissage passif des commandes Powershell existantes, j'ajoute generalement dans mon profil Powershell la Commande ci-dessous.

``` Powershell
Get-Command -Module Microsoft*,Cim*,PS*,ISE | Get-Random | Get-Help -ShowWindow
```