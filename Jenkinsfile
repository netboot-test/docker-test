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
        stage('Tests') {
            parallel{
                stage('flake8'){
                    steps {
                        scr ipt {
                            sh 'tox -e flake8'
                        }
                    }
                }
                stage('isort'){
                    steps {
                        scr ipt {
                            sh 'tox -e isort'
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
