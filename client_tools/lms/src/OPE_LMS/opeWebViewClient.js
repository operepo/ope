
// Backend QML object - hook WebChannel object to it
var LMS;
var version = "0.3";

function dynamicLoad(url, callback) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    script.onreadystatechange = callback;
    script.onload = callback;

    // Start the script loading
    document.head.appendChild(script);
}

function clickHandler(e) {
    var event = e ? e:event;
    var target;
    var link_url;
    var ret = true;

    if (event.srcElement) {
        target = event.srcElement;
    } else {
        target = event.target;
    }

    var alertString = 'Tag=<' + target.tagName + '>';
    if (target.hasAttribute('id')) {
        alertString += '\\nId=' + target.getAttribute('id');
    }
    if (target.hasAttribute('class')) {
        alertString += '\\nClass=' + target.getAttribute('class');
    }
    if (target.hasAttribute('name')) {
        alertString += '\\nName=' + target.getAttribute('name');
    }
    //alert(alertString);

    if (target.hasAttribute('href')){
        link_url = target.getAttribute('href');

        // Decide if this link should be opened by the system or let the
        // local webview open it.
        if (link_url.indexOf("/player.html?") !== -1) {
            // Movie player link, don't mess with it.
            console.log(">>> SMC Player URL - leaving link alone.");
            return true;
        }

        if(LMS) {
            // Don't do default events - e.g. cancel click on A tag
            event.preventDefault();
            // QWebChannel calls are async, have to use callback for return
            LMS.openDesktopLink(link_url, function(returnValue) {
                console.log('>>>> Launch Result: ' + returnValue);
            });
        }
    }

    return ret;
}

function lmsMain() {
    // Webchannel script loaded, do what needs to be done.
    console.log('>>> lmsMain called...');

    // Hook up to the webchannel
    var wcSocket = new WebSocket('ws://localhost:65524');
    //console.log('>>> WebSocket ' + wcSocket);
    wcSocket.onopen = function(event) {
        //console.log('>>> WCSocket onopen...');
        var wc = new QWebChannel(wcSocket, function(channel) {
            //console.log('>>> WChannel Open...');
            LMS = channel.objects.LMS;

            // Connect to capture signals
            // LMS.someSignal.connect(function(someText) { alert(someText); });
            //console.log('>>> QWebChannel created...');

            // Capture all clicks on the page
            console.log('>>> OPE LMS - Capturing clicks');
            document.onclick = clickHandler;
        });


    };
    wcSocket.onclose = function() {
        //console.log('>>> WCSocket closed...');
    };
    wcSocket.onmessage = function (evt) {
        //console.log('>>> WCSocket message ' + evt.data);
    };
}

// Load the webchannel script
//document.onload = function(e) {
console.log('>>> OPE LMS - WebChannel - starting load... ' + version);
dynamicLoad('http://localhost:65525/qwebchannel.js',
            lmsMain);
//};
