pipeline {
    agent any
    environment {
        DEV_PORT     = '5001'
        QA_PORT      = '5002'
        PREPROD_PORT = '5003'
        // This critical line prevents Jenkins from automatically killing your background processes!
        JENKINS_NODE_COOKIE = 'dontKillMe'
        // CRITICAL: This binds your Jenkins credential to an environment variable
        // Make sure 'GITHUB_TOKEN_ID' matches the exact ID you gave it in Jenkins!
        GITHUB_AUTH  = credentials('GITHUB_TOKEN') 
    }
    stages {
        stage('Initialize & Build') {
            steps {
                echo 'Setting up local Python virtual environment...'
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate.bat
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Unit Tests (Quality Gate 1)') {
            steps {
                echo 'Running PyTest unit tests...'
                bat '''
                    call venv\\Scripts\\activate.bat
                        // 1. Force directory creation
                    if not exist test-reports mkdir test-reports
        
                        // 2. Run pytest outputting coverage directly to the root for better visibility
                    pytest test_app.py --junitxml=test-reports/results.xml --cov=app --cov-report=xml:coverage.xml --cov-append
        
                        // 3. Verification check: List files to see exactly where it landed
                    dir coverage.xml
                '''
            }
            post {
                    always {
                            // 1. Publish standard unit test execution counts
                            junit 'test-reports/results.xml'
            
                            // 2. Publish coverage visual graphs using the modern Coverage Plugin
                            recordCoverage(
                            tools: [    
                                        [ parser: 'COBERTURA', 
                                        pattern: '**/coverage.xml'
                                        ]

                                    ],
                            sourceCodeRetention: 'LAST_BUILD'
                            )
                        }
                }
        }
        stage('Deploy to DEV') {
            steps {
                echo "Deploying locally to DEV on port %DEV_PORT%..."
                bat '''
                    // 1. Kill anything on the port
                    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%DEV_PORT% ^| findstr LISTENING') do taskkill /f /pid %%a || type nul
                    
                    // 2. Clear or delete the previous log file to prevent file locks
                    if exist dev_log.txt del /f /q dev_log.txt || type nul

                    // 3. Set variables and launch
                    set APP_ENV=Development
                    set PORT=%DEV_PORT%
                    start "" /B venv\\Scripts\\python.exe app.py > dev_log.txt 2>&1
                    venv\\Scripts\\python.exe -c "import time; time.sleep(3)"
                '''
            }
        }
        stage('DEV Smoke Test (Quality Gate 2)') {
            steps {
                echo 'Verifying DEV deployment health...'
                bat '''
                    venv\\Scripts\\python.exe -c "import requests; res = requests.get('http://localhost:' + '%DEV_PORT%' + '/health'); exit(0 if res.status_code == 200 else 1)"
                '''
            }
        }
        stage('Deploy to QA') {
            steps {
                echo "DEV Smoke Test Passed! Deploying to QA on port %QA_PORT%..."
                bat '''
                    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%QA_PORT% ^| findstr LISTENING') do taskkill /f /pid %%a || type nul
                    if exist qa_log.txt del /f /q qa_log.txt || type nul
                    set APP_ENV="QA Testing"
                    set PORT=%QA_PORT%
                    start "" /B venv\\Scripts\\python.exe app.py > qa_log.txt 2>&1
                    venv\\Scripts\\python.exe -c "import time; time.sleep(3)"
                '''
            }
        }
        stage('QA Smoke Test (Quality Gate 3)') {
            steps {
                echo 'Verifying QA deployment health...'
                bat '''
                    venv\\Scripts\\python.exe -c "import requests; res = requests.get('http://localhost:' + '%QA_PORT%' + '/health'); exit(0 if res.status_code == 200 else 1)"
                '''
            }
        }
        stage('Manual Approval for Preprod') {
            steps {
                echo 'Pausing pipeline waiting for Human Sign-off before Preprod deployment...'
                input message: 'Does the QA environment look good? Approve deployment to Preprod?', ok: 'Deploy to Preprod'
            }
        }
        stage('Deploy to Preprod') {
            steps {
                echo "Approved! Deploying to Preprod on port %PREPROD_PORT%..."
                bat '''
                    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%PREPROD_PORT% ^| findstr LISTENING') do taskkill /f /pid %%a || type nul
                    
                    if exist preprod_log.txt del /f /q preprod_log.txt || type nul
                    set APP_ENV="Pre-Production"
                    set PORT=%PREPROD_PORT%
                    start "" /B venv\\Scripts\\python.exe app.py > preprod_log.txt 2>&1
                    venv\\Scripts\\python.exe -c "import time; time.sleep(3)"
                '''
            }
        }
    }
    // ADD THIS BLOCK AT THE VERY BOTTOM OF YOUR JENKINSFILE
     // UPDATE THIS POST BLOCK AT THE VERY BOTTOM
     post {
        success {
            echo 'Reporting success to GitHub...%GIT_URL%'
            bat '''
            set OWNER=Gpralhad
            set REPO=python-cicd-demo
            curl -L \
  		-X POST \
  		-H "Accept: application/vnd.github+json" \
  		-H "Authorization: Bearer %GITHUB_AUTH%" \
  		-H "X-GitHub-Api-Version: 2026-03-10" \
  		https://api.github.com/repos/%OWNER%/%REPO%/statuses/%GIT_COMMIT% \
  		-d "{\\\"state\\\":\\\"success\\\",\\\"target_url\\\":\\\"https://example.com/build/status\\\",\\\"description\\\":\\\"The build succeeded!\\\",\\\"context\\\":\\\"continuous-integration/jenkins\\\"}"            
		'''
        }
        failure {
            echo 'Reporting failure to GitHub...%GIT_URL%'
          bat '''
            set OWNER=Gpralhad
            set REPO=python-cicd-demo
            curl -L \
  		-X POST \
  		-H "Accept: application/vnd.github+json" \
  		-H "Authorization: Bearer %GITHUB_AUTH%" \
  		-H "X-GitHub-Api-Version: 2026-03-10" \
  		https://api.github.com/repos/%OWNER%/%REPO%/statuses/%GIT_COMMIT% \
  		-d "{\\\"state\\\":\\\"failure\\\",\\\"target_url\\\":\\\"https://example.com/build/status\\\",\\\"description\\\":\\\"The build failed!\\\",\\\"context\\\":\\\"continuous-integration/jenkins\\\"}"            
		'''
        }
    }
}
