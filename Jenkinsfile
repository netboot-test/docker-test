pipeline {
    agent {
        docker { 
            image 'node:7-alpine'
            label 'SRV-DOCKER-DEV'
        }
    }
    stages {
        stage('Test') {
            steps {
                sh 'node --version'
            }
        }
    }
}
