pipeline {
    agent { label 'Agent1' }
    
    environment {
        PATH = "$HOME/.local/bin:$PATH"
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
    }
}