pipeline {
    agent { label 'docker' }
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
            agent { label 'docker' }
            steps {
                echo 'Starting to build docker image'
                script {
                    app = docker.build("netboot/cookbook:${env.BUILD_ID}")
                }
            }
        }
        parallel {
            stage('Push latest image') {
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
            stage('Push dev image') {
                agent { label 'docker' }
                when {
                    branch 'master'
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
    post {
        always {
            echo 'One way or another, I have finished'
            deleteDir() /* clean up our workspace */
        }
    }
}
