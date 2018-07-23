pipeline {
  agent {
      docker {
          image 'maven:3-alpine'
          label 'docker'
      }
  }
  stages {
    stage('Build') {
      steps {
        sh 'mvn --version'
      }
    }
  }
}
