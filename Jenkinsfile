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
        stage('Build Image') {
            agent { label 'SRV-DOCKER-PROD' }
            steps {
                echo 'Starting to build docker image'
                script {
                    app = docker.build("netboot/cookbook:${env.BUILD_ID}")
                }
            }
        }
        stages('Push Image') {
            stage('Prod') {
                agent { label 'SRV-DOCKER-PROD' }
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
            stage('Dev') {
                agent { label 'SRV-DOCKER-PROD' }
                when { branch 'test' }
                steps {
                    echo 'Push Image'
                    script {
                        docker.withRegistry('https://registry.hub.docker.com', 'ca19e01b-db1a-43a3-adc4-46dafe13fea2') {
                            app.push("dev")
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
                    sh("docker rmi -f netboot/cookbook:${env.BUILD_NUMBER} || :")
                    deleteDir()
                    cleanWs()
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
                            sh('docker stop cookbook-prod || true && docker rm cookbook-prod || true')
                            app = docker.image("netboot/cookbook:latest")
                            app.run('--name cookbook-prod --network web --label traefik.frontend.rule=Host:cookbook.netboot.fr')
                        }
                    }
                }
                stage('Dev') {
                    agent { label 'SRV-DOCKER-PROD' }
                    when { branch 'test' }
                    steps {
                        script {
                            sh('docker stop cookbook-dev || true && docker rm cookbook-dev || true')
                            app = docker.image("netboot/cookbook:dev")
                            app.run('--name cookbook-dev --network web --label traefik.frontend.rule=Host:cookbook-dev.netboot.fr')
                        }
                    }
                }
            }
        }
    }
}
