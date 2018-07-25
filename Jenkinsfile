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

                stage('flake8'){
                    steps {
                        script {
                            sh 'tox -e flake8'
                        }
                    }
                }
                stage('isort'){
                    steps {
                        script {
                            sh 'tox -e isort'
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
                stage('cover'){
                    steps {
                        script {
                            sh 'tox -e cover'
                        }
                    }
                }


    }
}
