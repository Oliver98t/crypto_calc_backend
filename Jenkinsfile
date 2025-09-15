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

        stage('Check system status') {
            steps {
                sh 'python3 tests/API_test.py --status'
            }
        }
        
        stage('Run Unit Tests') {
            steps {
                sh 'pytest'
            }
        }
    }
}