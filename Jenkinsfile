pipeline {
  agent { label 'Agent1' }

  stages {

    stage('Install Dependencies') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }

    stage('Run Unit Tests') {
      steps {
        sh 'pytest'
      }
    }

    stage('Archive Results') {
      steps {
        junit 'results.xml'
      }
    }
  }
}