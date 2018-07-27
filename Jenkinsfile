pipeline {
    agent { label 'SRV-DOCKER-DEV' }
    stages {
        stage('Checkout'){
            steps {
                deleteDir()
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
        stage('Build Image') {
            agent { label 'SRV-DOCKER-DEV' }
            steps {
                echo 'Starting to build docker image'
                script {
                    app = docker.build("netboot/beapi:${env.BUILD_ID}")
                }
            }
        }
        stage('Push Image') {
            agent { label 'SRV-DOCKER-DEV' }
            when { branch 'master' }
            steps {
                echo 'Push Image'
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'ca19e01b-db1a-43a3-adc4-46dafe13fea2') {
                        app.push("latest")
                    }
                }
            }
        }
        stage('Start Image') {
            agent { label 'SRV-DOCKER-PROD' }
            when { branch 'master' }
            steps {
                script {
                    sh('docker stop beapi || true')
                    sh('docker rm beapi || true')
                    sh('docker rmi netboot/beapi:latest --force')
                    app = docker.image("netboot/beapi:latest")
                    app.run('--name beapi --network web --label traefik.frontend.rule=Host:api.netboot.fr \ traefik.port=8080')
                }
            }
        }
        stage('Cleanup') {
            agent {label 'SRV-DOCKER-DEV'}
            steps {
                script {
                    sh("docker rmi -f squidfunk/mkdocs-material:latest || :")
                    deleteDir()
                    cleanWs()
                }
            }
        }
    }
}
