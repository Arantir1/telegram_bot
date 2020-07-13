sudo ssh -i ./.ssh/aws_bot.pem ubuntu@ec2-3-14-84-102.us-east-2.compute.amazonaws.com

psql --host=database-1.c40qsbdstdii.us-east-2.rds.amazonaws.com --port=5432 --username=postgres --password --dbname=postgres

export DB_HOST=database-1.c40qsbdstdii.us-east-2.rds.amazonaws.com
export DB_DATABASE=telegram
export DB_PASSWORD=west0000
export DB_USER=postgres
export TOKEN=455559594:AAH_P2ik4soQ1SzrymRrTa84Ez5ylKO73qA
export URL=ec2-3-14-84-102.us-east-2.compute.amazonaws.com:5000
export SECRET=bhOHR6pDkT3alsSTALm6yqpOiRBfu6hD