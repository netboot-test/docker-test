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
    }
}
