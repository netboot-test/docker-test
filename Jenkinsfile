pipeline {
  agent {
    docker {
        image 'maven:3-alpine'
        label 'DOCKER'
    }
  }
  }
  stages {
    stage('Build') {
      steps {
        sh 'mvn -B'
      }
    }
  }
}
