

var reqId = 0;
var anchor = document.getElementById('anchor');
var searchField = document.getElementById('search');
var senderField = document.getElementById('sender');
var messageField = document.getElementById('message');
var receiverField = document.getElementById('receiver'); //Added this to get receiver of messages. 
var searchBtn = document.getElementById('searchBtn');
var sendBtn = document.getElementById('sendBtn');
var allBtn = document.getElementById('allBtn');
var output = document.getElementById('output');
var header = document.getElementById('header');

var csrfToken = document.getElementById('csrf_token').value; //Getting the csrf_token and storing it in a variable.

var checkAnnouncements = async () => {
    res = await fetch('/announcements');
    anns = await res.json();
    if (anns && Array.isArray(anns.data)) {
        const elts = [];
        anns.data.forEach((element, idx) => {
            if (idx > 0) {
                const node = document.createElement('li');
                node.textContent = '  …  ';
                elts.push(node);
            }
            const node = document.createElement('li');
            node.textContent = `${element.message || ''}`;
            elts.push(node);
        });
        console.log(elts);
        header.replaceChildren(...elts);
    }
};
var showInbox = async (sender) => { //Receiver
    const id = reqId++;
    const q = `/showInbox?sender=${encodeURIComponent(sender)}`; //Changes here receiver.
    res = await fetch(q);
    console.log(res);
    const head = document.createElement('h3');
    head.textContent = `[${id}]  ${q} → ${res.status} ${res.statusText}`;
    output.appendChild(head);
    const body = document.createElement('p');
    body.innerHTML = await res.text();
    output.appendChild(body);
    body.scrollIntoView({ block: "end", inline: "nearest", behavior: "smooth" });
    anchor.scrollIntoView();
    checkAnnouncements();
};
var send = async (sender, message, receiver) => { //Receiver
    const id = reqId++;
    const q = `/send?sender=${encodeURIComponent(sender)}&message=${encodeURIComponent(message)}&receiver=${encodeURIComponent(receiver)}`; //Receiver
    res = await fetch(q, { method: 'post', headers: {
         'X-CSRF-TOKEN': csrfToken
        }});
    console.log(res);
    const head = document.createElement('h3');
    head.textContent = `[${id}]  ${q} → ${res.status} ${res.statusText}`;
    output.appendChild(head);
    const body = document.createElement('p');
    body.innerHTML = await res.text();
    output.appendChild(body);
    body.scrollIntoView({ block: "end", inline: "nearest", behavior: "smooth" });
    anchor.scrollIntoView();
    checkAnnouncements();
};



searchField.addEventListener('keydown', ev => {
    if (ev.key === 'Enter') {
        search(searchField.value);
    }
});

searchBtn.addEventListener('click', () => search(searchField.value, senderField.value)); //senderField.value
allBtn.addEventListener('click', () => showInbox(senderField.value)); //Added senderField.value here so that you can only see you own messages. 
sendBtn.addEventListener('click', () => send(senderField.value, messageField.value, receiverField.value)); //Added receiver here. 
checkAnnouncements();