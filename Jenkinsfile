pipeline {
  agent { label 'DOCKER' image 'node:7-alpine' }
  }
  stages {
    stage('Build') {
      steps {
        sh 'mvn -B'
      }
    }
  }
}
