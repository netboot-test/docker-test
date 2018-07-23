pipeline {
    agent none
    options {
        timeout(time: 10, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    stages {
        stage('Checkout'){
            agent { label 'docker' }
            steps {
                checkout scm
            }
        }
        stage('SonarQube analysis') {
            steps {
                script {
                // requires SonarQube Scanner 2.8+
                scannerHome = tool 'SonarQube Scanner 2.8'
                }
                withSonarQubeEnv('SonarQube Scanner') {
                sh "${scannerHome}/bin/sonar-scanner"
                }
            }
        }
        stage('Build Docs') {
            agent {
                docker {
                    image "squidfunk/mkdocs-material"
                    label "docker"
                    args "--entrypoint=''"
                }
            }
            steps {
                sh 'mkdocs build'
            }
        }
        stage('Build image') {
            app = docker.build("netboot/cookbook:${env.BUILD_ID}")
        }
        stage ('Run Application') {
            agent {
                docker {
                    image "netboot/cookbook:${env.BUILD_ID}"
                    label "docker"
                }
            }

        }
    }

}
