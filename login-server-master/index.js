

var reqId = 0;
var anchor = document.getElementById('anchor');
var senderField = document.getElementById('sender');
var messageField = document.getElementById('message');
var receiverField = document.getElementById('receiver'); //Added this to get receiver of messages. 
var sendBtn = document.getElementById('sendBtn');
var allBtn = document.getElementById('allBtn');
var output = document.getElementById('output');
var header = document.getElementById('header');
var logOut = document.getElementById('logOut');

var csrfToken = document.getElementById('csrf_token').value; //Getting the csrf_token and storing it in a variable.

var showInbox = async (sender) => { //Receiver
    const id = reqId++;
    const q = `/showInbox?sender=${encodeURIComponent(sender)}`; //Changes here receiver.
    res = await fetch(q, {method: 'get', headers: {
        'X-CSRF-TOKEN': csrfToken
       }});;
    console.log(res);
    const body = document.createElement('p');
    body.innerHTML = await res.text();
    output.appendChild(body);
    body.scrollIntoView({ block: "end", inline: "nearest", behavior: "smooth" });
    anchor.scrollIntoView();
};
var send = async (sender, message, receiver) => { //Receiver
    const id = reqId++;
    const q = `/send?sender=${encodeURIComponent(sender)}&message=${encodeURIComponent(message)}&receiver=${encodeURIComponent(receiver)}`; //Receiver
    res = await fetch(q, { method: 'post', headers: {
         'X-CSRF-TOKEN': csrfToken
        }});
    console.log(res);
    const body = document.createElement('p');
    body.innerHTML = await res.text();
    output.appendChild(body);
    body.scrollIntoView({ block: "end", inline: "nearest", behavior: "smooth" });
    anchor.scrollIntoView();
};

var logout = async () => {
    const id = reqId++;
    const q = '/logout'
    res = await fetch(q);
    console.log(res);
    location.reload(); // This will reload the page and send us to where the fetch has redirected us.
}

logOut.addEventListener('click', () => logout());
allBtn.addEventListener('click', () => showInbox(senderField.value)); //Added senderField.value here so that you can only see you own messages. 
sendBtn.addEventListener('click', () => send(senderField.value, messageField.value, receiverField.value)); //Added receiver here. 
