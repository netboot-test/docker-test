pipeline {
    agent {
        docker {
            image 'python:3.7-alpine'
            label 'SRV-DOCKER-DEV'
        }
    }
    stages {
        stage('Checkout'){
            steps {
                checkout scm
            }
        }
        stage('Init'){
            steps {
                script {
                    sh 'pip install tox'
                }
            }
        }
       stage('clean'){
            steps {
                script {
                    sh 'tox -e clean'
                }
            }
        }
        stage('Tests') {
            parallel{
                stage('check'){
                    steps {
                        script {
                            sh 'tox -e check'
                        }
                    }
                }
                stage('cover'){
                    steps {
                        script {
                            sh 'tox -e cover'
                        }
                    }
                }
                stage('coveralls'){
                    steps {
                        script {
                            sh 'tox -e coveralls'
                        }
                    }
                }
            }
        }
    }
}
