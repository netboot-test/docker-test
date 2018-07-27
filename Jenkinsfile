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
                    sh 'pip3.6 install tox'
                }
            }
        }
        //stage('Pylint'){
        //    steps {
        //        script {
        //            sh 'tox -e pylint'
        //        }
        //    }
        //}
        stage('Isort'){
            steps {
                script {
                    sh 'tox -e isort'
                }
            }
        }
        stage('Flake8'){
            steps {
                script {
                    sh 'tox -e flake8'
                }
            }
        }
        stage('Code Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarRunner'
                    def projectKey  = "-Dsonar.projectKey=Netboot_BeAPI"
                    def sources     = "-Dsonar.sources=./beapi"
                    def SONAR_SCANNER_OPTS = projectKey + " " + sources

                    withSonarQubeEnv('Netboot') {
                        env.SQ_HOSTNAME = SONAR_HOST_URL;
                        env.SQ_AUTHENTICATION_TOKEN = SONAR_AUTH_TOKEN;
                        env.SONAR_SCANNER_OPTS= SONAR_SCANNER_OPTS
                        sh "${scannerHome}/bin/sonar-scanner"
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
                    app.run('--name beapi --network web --label traefik.frontend.rule=Host:api.netboot.fr --label traefik.port=8080')
                }
            }
        }
        stage('Cleanup') {
            agent {label 'SRV-DOCKER-DEV'}
            steps {
                script {
                    sh("docker rmi -f netboot/beapi:${env.BUILD_ID} || :")
                    deleteDir()
                    cleanWs()
                }
            }
        }
    }
}
