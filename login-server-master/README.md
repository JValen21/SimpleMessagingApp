## Whats wrong with the structure/security?
The file app.py is extremely messy. Very insecure design. Almost everyting is mixed in one file. 

HTML, CSS and JavaScript is in the same file (index.html). This is not good programming design. It can also make it harder to further develop the project. 

The usernames and passwords are stored in a plaintext dict. If the hacker gets access to the app.py file, he gets all user and password information. This is not good. We should hash the passwords with salt and store them in a database table called users.

The login system does not verify passwords, it only checks for an existing username. 

The sercet key is also very bad. Its also available in plaintext for the hacker if he gets access to the app.py file. It should not be available and it should be random. 

The send message functionality can be misused by cross site scripting. This can be done by for example sending this message:
`<span onclick=alert(5)> You just won an IPad! </span>`. The hacker could here change "alert(5)" with some dangerous malicious code.

Its vulnerable to sql injections, both in the log in page and the send message page. The server shows us the actual SQL query it uses. This is really bad and can give an attacker the information he needs to succeed with an injection attack.

Cookies has been set without the SameSite attribute, which means that the cookie can be sent as a result of a 'cross-site' request. The SameSite attribute is an effective counter measure to cross-site request forgery, cross-site script inclusion, and timing attacks.

Content security policy (CSP) header is not set. CSP is an added layer of security that will help to detect and mitigate certain types of attacks, for example Cross site scripting and data injection attacks. 

No encryption making it vulnerable to man in the middle attacks. 

Users can pretend to be someone else by sending messages as another user. This should not be possible. 

No authorization. Everyone can see everyones messages.

The app is also vulnerable to CSRF attacks, since there is no CSRF token checks. An end-user could be hacked by clicking on a form on another website, redirecting messages to our server. Also, the send() method in app.py supports POST and GET requests, meaning a user can be tricked into clicking a link, which will send a message to this server. This is because clicking of links usually are GET requests and not POST requests

## Design considerations

First, I structured the code better. There were no structrue in the project, making it very hard to get a good overview of the project. I created a dbManager.py to manage the database and calls to the database. I moved the databse initialization to this file. I created messaging.py to handle the simple messaging functionality. resources.py for some resources and security.py for security implementations.

I fixed the SQL injection vulnerability with prepared statements for the sql queries in dbManager.py.

Moved all the javascript code in index.html to a file called index.js and made a function index_js() in app.py that sends the js file. Did the same with the css code in index.html as I did with the javascript code. 

Imported hashLib and made a function that encrypts the passwords hashPassword() (sha512 with salt). 

I decided to use the included SQLite to persist information. I made a new table called users in the database and stored the usernames, hashed passwords and salt in this table, making the app much more secure without passwords in plaintext dict. 

I made a new function check_password() that is used in the login() function to check the username and password. In this function I have implemented sql queries to get the hashed password and salt from the database. I use the same salt to hash the password from the user trying to log in, to check if it is correct. Now we have to use correct username and password to login. 

Now I wanted to be able to create users. I created a CreateUserForm in forms.py so that I could use flask forms. I created a createUser.html with a form where you have to fill in username and password. You have to fill in password twice for extra protection and the length of the password has to be over 12 characters. I created a function createUser() where I check if either the username exists in the database or if the password is typed correctly. I created some extra functions usernameExists() and wrongPassword() in dbManager.py to implement this functionality. If you have typed everything correctly, your account info will be added to the database and you will be redirected to the login page. If not, the createUser page will reload. Would like to add some message to the user if he did something wrong, but didnt have time to implement it. I have also created a way to navigate between the login and createUser pages. 

I connected the user that is logged in to be the sender of messages. This way you cant pretend to be someone else when you send messages. The "sender" in the html will display the username of the logged in user. To do this, I had to move index.html to templates and changed the index_html() function in app.py to return render_template(). This way I could send user data to index.html. The only thing I had to do in the html now was to reference current_user.id to get the name of the user that is currently logged in. 

Changed the table "messages" in the database to also have a receiver and timestamp. Fixed the html and javascript so that you have to write to a receiver if you want to send a message. Just did some small changes on the send methods in index.js and messaging.py.

Fixed authorization. Each user can only see his/her messages. Made it possible to see the messages sent to the user that is logged in by clicking on a button "Show inbox". I removed the possibility to see all messages, because you should only see messages that is sent to you and not others. 

Imported session to store information related to the user. A session makes it possible to remember information from one request to another.

Made the secret key random and better.

I enabled CSRF protection using flask-WTF extension.

Enabled CSP. 

Set SESSION_COOCKIE_SAMESITE to lax and SESSION_COOCKIE_HTTPONLY to True.

Implemented is_safe_url function that ensures that a redirect target will lead to the same server.

Implemeted logout functionality.   

I removed the "search" functionality of the boilerplate application, because this did not make very much sense for a message application in my eyes. I don't really use pygmentize, since I don't show the queries, so I removed this too. Same with announcements. 

I also removed the printing of sql queries when you perform messaging requests. 

## Application features
### Creating users
From the "/createUser" page you can create users. You have to write a username that is unique and a password with more than 12 characters. 

### Login
From the "/login" page you can enter a username and password in the forms and you will be redirected to the simple messaging application. 

### Simple messaging
When you log in you will get straight to the messaging application. Here you have 3 features. You can see all messages sent to you by clicking on the "showInbox" button. This will show you your messages along with who has sent it and a timestamp of when the message was sent. 

If you want to send a message. You have to type in the "to" field and write the name of an existing user you want to send to. Write your message and then click send message and the message is sent. You will be notfied that the message was sent.

### Logout
Click the logout button and you will be logged out and redirected to the "/login" page.


## Instructions on how to test the application

You run the application with the command 'flask run'. This will set up everything you need. Then just go to 'localhost:5000' and you will be redirected to the login page.

When starting the application for the first time, there is only 1 user in the database. You can log in with username Ole (capital O) and password oleerbest123. You will need to create a user if you want to send messages between two users. After creating a user, you will be redirected to the login page. Remeber to create a password that is minimum 12 characters long. 

When you log in, enter username and password of an existing user into the log in form. 

When you test the messaging system, make sure you write to a user in the 'to' form when you send messages. Its a pretty simple messaging system. Click on showInbox button if you want to see messages rechieved by the user that is logged in. Click logout button if you want to log out. 

## Technical details

The app is very simple and I have reused a lot of the logic and code from the login server project. 

When hashing password, I have used the hashlib library. For handling login I have used flask_login. For url parsing I have used the urllib.parse library.

I have set the secret key to secrets.token_hex(16). Now every time the flask application is run, a new random secret key is made and everyone's session cookie will be invalid and therefore everyone will be logged out.

I enabled CSRF protection using flask-WTF extension. When a user now sends a message, the CSRF token is compared to ensure that the POST request did not come from somewhere else. This will happen automatically when using the createUser and login forms, but has to be done manually when sending messages.

I created an add_security_headers() function (in security.py) with @app.after_request that will apply the CSP header to all routes served by the app. CSP is an added layer of security that will help to detect and mitigate certain types of attacks, for example cross site scripting and data injection attacks. 

By setting SESSION_COOCKIE_SAMESITE to the value "lax" I prevent the browser from sending the coockie along with cross-site requests. This mitigate the risk of cross-origin information leakage. The default value of the SameSite attribute differs with each browser, therefore I have explicitly set the value of the attribute.

By setting SESSION_COOCKIE_HTTPONLY to True we prevent any client-side usage of the session cookie.

## Answers to questions
### Who might attack the application?
Anyone who have some basic knowledge about cybersecurity and want to might attack the application. 

### What can an attacker do and what damage could be done?
The attacker can exploit the sql injection, XSS and CSRF vulnerabilities. I feel like I have answered a lot of these questions above, but here is something the attacker can do:
- The search and send functionality is open to sql injection attacks. If the attacker succeeds, he could get access to the whole database. The attacker can change data and delete data. SQL injection can breach all three elements in the CIA triad. Confidentiality is breached if hackers get hold of sensitive user information from the database. If the hacker change data in the database, integrity is breached. The hacker can also delete data, which breaches with availability.
- XSS-attacks: The attacker can trick the users into clicking on message content that can run malicous scripts. This is a breach in authenticity and accountability, because messages you think are sent from a user might actually be sent from a hacker. 
- No CSRF protection. When a user sends a message, there is no CSRF token to compare to ensure that the POST request did not come from somewhere else. breaches with authenticity and accountability.

Another security issue is that login doesnt require a password, which lets anyone who knows a valid username access to that user. This is broken authentication.

### Is there limits to what an attacker can do? 
Well, the databse only stores messages and announcements, so the attacker can only manipulate things surrounding this. 

### Limits to what we can sensibly protect against? 
Well, yes. We can of course only protect against attacks we already recognize and know about. We always have to keep improving security as we develop our application further. More security issues might arise! You should always look at the top most common security vulnerabilities and implement some protection against them.


### What are the main attack vectors for the application?
Definitely the search and send functionality in the messaging system as I have mentioned.

### What should we do (or what have you done) to protect against attacks?
Basicly, the three biggest vulnerabilities I have protected against are SQL injections, XSS and CSRF. 

I have: 
- hashed passwords with salt.
- Enabled CSP.
- Set sameSite attribute on coockies. 
- Implemented prepared statements for sql queries. 
- Enabled CSRF protection using flask-WTF extension
- Set the secret key to secrets.token_hex(16)
- Implemented is_safe_url() function. 
- Fixed login functionality to require password. 
- Stored username, passwords and salt in database instead of plaintext dict.
- Removed printing of the queries. 
- Fixed insecure design problem.

For better explanation, look above at techinal details and design considerations.

### What is the access control model?
It doesnt have any good access control model. The authentication in the boilerplate application is extremely broken. 

### How can you know that your security is good enough? (traceability)
You can never be completely safe. I feel like good enough security should prevent the most common vulnerabilities, such as SQL injections, XSS and CSRF in our case. Tracibility is a good feature to add in every system because if an attacker succeeds to attack your application, you can quickly trace the problem and prevent similar future attacks. We can obtain tracebility by logging different activity within our application. 