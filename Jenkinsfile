pipeline {
    agent none
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
       stage('Quality Check') {
            agent { label 'docker' }
            withSonarQubeEnv(props.sonarInstance) {
                withEnv(["JAVA_HOME=${tool props.jdkVersion}",
                        "PATH+SONAR_HOME=${tool props.sonarVersion}/bin:${tool props.jdkVersion}/bin",
                        "SONAR_SCANNER_OPTS=-Xmx1536m"]) {
                    sh "sonar-scanner -Dsonar.projectKey=${props.sonarProjectKey} \
                        -Dsonar.projectVersion='0.1.0' \
                        -Dsonar.projectName='${props.sonarProjectName}' \
                        -Dsonar.sources='./app/' \
                        -Dsonar.language='py' \
                        -Dsonar.host.url=$SONAR_HOST_URL \
                        -DfailIfNoTests=false \
                        -Dsonar.python.coverage.reportPath=coverage.xml \
                        -Dsonar.core.codeCoveragePlugin=cobertura \
                        -Dsonar.python.xunit.reportPath=report.xml \
                        -Dsonar.python.xunit.skipDetails=false \
                        -Dsonar.verbose=true \
                        -Dsonar.exclusions=target"
                }
            }
            junit 'report.xml'
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
        stage('Prepare Docker Image'){
            agent {
                label 'docker'
                dockerfile true
            }
            steps {
        }
    }
}
