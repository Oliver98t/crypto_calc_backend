pipeline {
  agent {
    docker {
      label 'Agent1'
      image 'python:3.11'
      args '-u root'
    }
  }


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