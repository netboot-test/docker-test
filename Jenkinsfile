pipeline {
    agent { label 'SRV-DOCKER-DEV' }
    stages {
        stage('Checkout'){
            steps {
                checkout scm
            }
        }
        stage('Init'){
            steps {
                script {
                    sh 'pip3.6 install --upgrade pip'
                    sh 'pip3.6 install tox'
                }
            }
        }

        stage('Tox'){
            steps {
                script {
                    sh 'tox'
                }
            }
        }
        stage ('Code Analysis') {
            agent { label 'SRV-DOCKER-DEV' }
            steps {
                script {
                    // SonarQube Scanner Config
                    def scannerHome = tool 'SonarRunner';
                    def scmUrl = sh(returnStdout: true, script: 'git config remote.origin.url').trim()
                    def repoName = scmUrl.tokenize('/').last().split("\\.")[0]
                    def repoOrganization = scmUrl.tokenize('/')[2]

                    withSonarQubeEnv('Netboot') {

                        env.SQ_HOSTNAME = SONAR_HOST_URL;
                        env.SQ_AUTHENTICATION_TOKEN = SONAR_AUTH_TOKEN;
                        env.SQ_PROJECT_KEY = "${repoOrganization}:${repoName}:${env.BRANCH_NAME}";

                        sh "${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=${SQ_PROJECT_KEY} \
                                -Dsonar.sources=.";
                    }
                }
            }
        }

    }
}
