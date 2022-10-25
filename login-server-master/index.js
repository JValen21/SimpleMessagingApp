

var reqId = 0;
var anchor = document.getElementById('anchor');
var searchField = document.getElementById('search');
var senderField = document.getElementById('sender');
var messageField = document.getElementById('message');
var searchBtn = document.getElementById('searchBtn');
var sendBtn = document.getElementById('sendBtn');
var allBtn = document.getElementById('allBtn');
var output = document.getElementById('output');
var header = document.getElementById('header');

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
var search = async (query) => {
    const id = reqId++;
    const q = `/search?q=${encodeURIComponent(query)}`;
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
var send = async (sender, message) => {
    const id = reqId++;
    const q = `/send?sender=${encodeURIComponent(sender)}&message=${encodeURIComponent(message)}`;
    res = await fetch(q, { method: 'post' });
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
searchBtn.addEventListener('click', () => search(searchField.value));
allBtn.addEventListener('click', () => search('*'));
sendBtn.addEventListener('click', () => send(senderField.value, messageField.value));
checkAnnouncements();