pipeline {
    agent { label 'SRV-DOCKER-PROD' }
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
                    label 'SRV-DOCKER-PROD'
                    args "--entrypoint=''"
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
                }
            }
        }
        stage('Push image') {
            parallel {
                stage('Prod') {
                    agent { label 'SRV-DOCKER-PROD' }
                    when { branch 'master' }
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
                    agent { label 'SRV-DOCKER-PROD' }
                    when { branch 'test' }
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
        stage('Start image') {
            parallel {
                stage('Prod') {
                    agent { label 'SRV-DOCKER-PROD' }
                    when { branch 'master' }
                    steps {
                        script {
                            app = docker.image("netboot/cookbook:latest")
                            app.run('--name cookbook-prod --label traefik.frontend.rule=Host:cookbook.netboot.fr')
                        }
                    }
                }
                stage('Dev') {
                    agent { label 'SRV-DOCKER-PROD' }
                    when { branch 'test' }
                    steps {
                        script {
                            app = docker.image("netboot/cookbook:dev")
                            app.run('--name cookbook-dev --label traefik.frontend.rule=Host:cookbook-dev.netboot.fr')
                        }
                    }
                }
            }
        }
        stage('Cleanup') {
            agent { label 'SRV-DOCKER-PROD' }
            steps {
                script {
                    sh("docker rmi -f squidfunk/mkdocs-material:latest || :")
                    sh("docker rmi -f netboot/cookbook:${env.BUILD_ID} || :")
                    deleteDir()
                }
            }
        }
    }
}
