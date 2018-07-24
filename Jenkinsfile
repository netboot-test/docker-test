pipeline {
    agent { label 'SRV-DOCKER-PROD'}
    options {
        timeout(time: 10, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    stages {
        stage('Checkout'){
            agent { label 'SRV-DOCKER-PROD' }
            steps {
                checkout scm
            }
        }
        stage('Build Docs') {
            agent {
                docker {
                    image "squidfunk/mkdocs-material"
                    label "docker"
                }
            }
            steps {
                sh 'mkdocs build'
            }
        }
        stage('Build image') {
            agent { label 'SRV-DOCKER-PROD' }
            steps {
                echo 'Starting to build docker image'
                script {
                    app = docker.build("netboot/cookbook:${env.BUILD_ID}")
                    sh 'ls ./site/'
                }
            }
        }
        stage('Push image') {
            parallel {
                stage('Prod') {
                    agent { label 'docker' }
                    when {
                        branch 'master'
                    }
                    steps {
                        echo 'Push image'
                        script {
                            docker.withRegistry('https://registry.hub.docker.com', 'ca19e01b-db1a-43a3-adc4-46dafe13fea2') {
                                app.push("${env.BUILD_NUMBER}")
                                app.push("latest")
                            }
                        }
                    }
                }
                stage('Dev') {
                    agent { label 'docker' }
                    when {
                        branch 'test'
                    }
                    steps {
                        echo 'Push image'
                        script {
                            docker.withRegistry('https://registry.hub.docker.com', 'ca19e01b-db1a-43a3-adc4-46dafe13fea2') {
                                app.push("dev")
                            }
                        }
                    }
                }
            }
        }
        stage('Remove local images') {
            steps {
                // remove docker images
                sh("docker rmi -f netboot/cookbook:latest || :")
                sh("docker rmi -f netboot/cookbook:${env.BUILD_ID} || :")
                sh("docker rmi -f squidfunk/mkdocs-material || :")
            }
        }
    }
}
