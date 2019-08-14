
// Backend QML object - hook WebChannel object to it
var LMS;
var version = "0.4";
var log_txt = "";
var retry_waiting = false;

function log(msg) {
    if (log_txt !== "") { log_txt += "\n"; }
    log_txt += msg;
    if (LMS) {
        var l = log_txt;
        log_txt = "";
        LMS.log(l, function(ret){
            // Will be called when log function is done

            });

    } else {
        if (retry_waiting === true) { return; }
        // LMS not ready - fire a timeout so that we call this again later...
        retry_waiting = true;
        setTimeout(function(){ retry_waiting = false; log('log retry'); }, 750);
    }
}

function getQueryParam(param) {
    location.search.substr(1)
        .split("&")
        .some(function(item) { // returns first occurence and stops
            return item.split("=")[0] == param && (param = item.split("=")[1])
        })
    return param
}

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
    log("clickHandler...");
    var event = e ? e:event;
    var eventbutton = event.button;

    if (eventbutton === 2 || eventbutton === 3) {
        log("Skipping right click...");
        event.preventDefault();
        return false;
    }

    var target;
    var link_url;
    var ret = true;

    if (event.srcElement) {
        target = event.srcElement;
    } else {
        target = event.target;
    }

    var alertString = 'Tag=<' + target.tagName + '>';
    var target_class = "";
    if (target.hasAttribute('id')) {
        alertString += '\\nId=' + target.getAttribute('id');
    }
    if (target.hasAttribute('class')) {
        alertString += '\\nClass=' + target.getAttribute('class');
        target_class = target.getAttribute('class');
    }
    if (target.hasAttribute('name')) {
        alertString += '\\nName=' + target.getAttribute('name');
    }
    //alert(alertString);
    log(alertString);

    /*
    if (target_class.includes("ppfsenter")) {
        // This should be fullscreen button from player
        // Get movie id from query string
        var movie_id = getQueryParam("movie_id");
        var video_url = '/smc_video_cache/' + movie_id + '.mp4';
        if (LMS) {
            // Don't do default events - e.g. cancel click on A tag
            event.preventDefault();
            // QWebChannel calls are async, have to use callback for return
            LMS.openDesktopLink(video_url, function(returnValue) {
                log('>>>> Video Launch Result: ' + returnValue);
            });
        }

    }*/
    if (target.hasAttribute('href')){
        link_url = target.getAttribute('href');

        // Decide if this link should be opened by the system or let the
        // local webview open it.
        if (link_url.indexOf("/player.html?") !== -1) {
            // Movie player link, don't mess with it.
            log(">>> SMC Player URL - leaving link alone.");
            return true;
        }

        if(LMS) {
            // Don't do default events - e.g. cancel click on A tag
            event.preventDefault();
            // QWebChannel calls are async, have to use callback for return
            LMS.openDesktopLink(link_url, function(returnValue) {
                log('>>>> Launch Result: ' + returnValue);
            });
        }
    }

    return ret;
}

function lmsMain() {
    // Webchannel script loaded, do what needs to be done.
    log('>>> lmsMain called...');

    // Disable right click
    document.oncontextmenu = clickHandler;

    // Hook up to the webchannel
    var wcSocket = new WebSocket('ws://localhost:65524');
    //log('>>> WebSocket ' + wcSocket);
    wcSocket.onopen = function(event) {
        //log('>>> WCSocket onopen...');
        var wc = new QWebChannel(wcSocket, function(channel) {
            //log('>>> WChannel Open...');
            LMS = channel.objects.LMS;

            // Connect to capture signals
            // LMS.someSignal.connect(function(someText) { alert(someText); });
            //log('>>> QWebChannel created...');

            // Capture all clicks on the page
            log('>>> OPE LMS - Capturing clicks');
            document.onclick = clickHandler;
        });


    };
    wcSocket.onclose = function() {
        log('>>> WCSocket closed...');
    };
    wcSocket.onmessage = function (evt) {
        log('>>> WCSocket message ' + evt.data);
    };
}

// Load the webchannel script
//document.onload = function(e) {
log('>>> OPE LMS - WebChannel - starting load... ' + version);
dynamicLoad('http://localhost:65525/qwebchannel.js',
            lmsMain);
//};
