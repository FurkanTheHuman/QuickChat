# QuickChat api via python/django

## Installation
#### with pip
in QuickChat:

`pip3 -r reqirements.txt`  
`python manage.py makemigrations`  
`python manage.py migrate`  
`python manage.py runserver`  

server runs at `localhost:8000/`

#### with docker-compose
there are two docker-compose files. First is for development, second for the production. 

For development:   
`docker-compose up -d --build` 

For production:   
`docker-compose -f docker-compose.prod.yml up -d --build` 


## API reference
base: `/api/v1/`  
Every path is starts with base   
NOTE: urls must end with "\\"

url: `/login/`   
method: POST    
request: {"username":\<username\>, "password": \<password\>}  
response: {"token": \<auth_token\>}  

url: `/register/`  
method: POST    
request: {"username":\<username\>, "email":\<email\>, "password": \<password\>}  
response: {"token": \<auth_token\>}  

url: `/contacts/all/`
method: POST  
request:  {"token": \<auth_token\>}  
response: {"users":\[{"username":\<username\>, ...}\]}

url: `/chat/history/?username=<username>`   
method: POST  
request:  {"token": \<auth_token\>}  
response:
```json
 {"chats":   
    [{
        "sender":"<username>",   
        "reciever":"<username>",   
        "message":"<a message about old days>",   
        "send_date":"<date>",    
        "seen":"<is seen by other user>"
    } ...]
}

```

url: `/block/user/?username=<username>`
method: POST  
request:  {"token": \<auth_token\>}  
response:  {"state":"x user blocked"}

url: `/unblock/user/?username=<username>`
method: POST  
request:  {"token": \<auth_token\>}  
response:  {"state":"x user unblocked"}

url: `/send_message/`
method: POST  
request:  {"token": \<auth_token\>, "username":\<reciever\>, "message":\<message\>}  
response:  {"state":"success"}

url: `/chat/last_messages/`
method: POST  
request:  {"token": \<auth_token\>, "username":\<username\>}  
response:  last message of every user who messaged loged in user, also count of unread messages

