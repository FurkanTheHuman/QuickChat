# QuickChat api via python/django

## Installation
#### with pip
in QuickChat:

`pip3 -r reqirements.txt`  
`python3 manage.py makemigrations`  
`python3 manage.py migrate`  
`python3 manage.py runserver`  

server runs at `localhost:8000/`

#### with docker-compose
there are two docker-compose files. First is for development, second for the production. 

server runs at `localhost:1337/`  
behind nginx and also uses postgresql

For development:   
`docker-compose up -d --build` 

For production:   
`docker-compose -f docker-compose.prod.yml up -d --build` 


## Running Tests
With `python3 manage.py test` run the unit tests    
You should be in the QuickChat directory to run this command 

## API reference
base: `/api/v1/`  
Every path starts with base   
NOTE: urls must end with "\\"    
Recommended curl structure:    
`curl --header "Content-Type: application/json"   --request POST   --data '{"username":"x","password":"y",...}'   http://localhost:1337/api/v1/soem/path/`



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
about: prints all users


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
about: shows you the post history also shows you if your message are seen by other user

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
NOTE: username is reciever in this context 


url: `/chat/last_messages/`     
method: POST  
request:  {"token": \<auth_token\>, "username":\<username\>}  
response:  last message of every user who messaged logged in user, also count of unread messages

