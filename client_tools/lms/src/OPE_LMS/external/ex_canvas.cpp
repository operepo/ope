#include "ex_canvas.h"

EX_Canvas::EX_Canvas(QObject *parent) :
    QObject(parent)
{    
    canvas_client_id = "1";
    canvas_client_secret = "hVGyxhHAKulUTZwAExbKALBpZaHTGDBkoSS7DpsvRpY1H7yzoMfnI5NLnC6t5A0Q";
            // Key for huskers user "MHzeKX3jqUejUTjxWK1v3NUCu9gA9AAkEe9LgJiQvzl9WRgCBDAv99OY0iKaLpJg";
    canvas_access_token = "";
    canvas_server = "https://canvas.pencollege.net";

    web_request = new CM_WebRequest(this);
}

bool EX_Canvas::InitTool()
{
    // Sync the course
//    SyncCourse("CSE101");

    return true;
}

bool EX_Canvas::LinkToCanvas(QString redirect_url, QString client_id)
{
    // Redirect to canvas server to authorize this app
    bool ret = false;

    //// TODO add purpose to key generation? &purpose=MobileLMS
    // Open the browser. We will get an event from the web server when it is done
    // https://lms.dev.domain.com/login/oauth2/auth?client_id=10&response_type=code&redirect_uri=urn:ietf:wg:oauth:2.0:oob
    QString canvas_url = canvas_server;
    if (!canvas_url.endsWith("/login/oauth2/auth"))
    {
        // Add the path
        canvas_url+= "/login/oauth2/auth";
        canvas_url.replace("//login", "/login"); // fix up double slashes which happens if url already ended with /
    }
    QDesktopServices::openUrl(QUrl(canvas_url + "?client_id=" + client_id + "&response_type=code&redirect_uri=" + QUrl::toPercentEncoding(redirect_url)));
    //https://canvas.pencollege.net/login/oauth2/auth?client_id=1&response_type=code&redirect_uri=" + QUrl::toPercentEncoding("http://localhost:8080/oauth/response"))
    return true;
}

void EX_Canvas::FinalizeLinkToCanvas(CM_HTTPRequest *request, CM_HTTPResponse *response)
{


    // Get the URL and pull the parameters
    QString url = request->headers["URL"];
    QStringList parts = url.split("?");
    if (parts.length() < 2)
    {
        // Should be pre ? and post ?, so 2 parts.
        response->SetBody("<b>Invalid Query Parameters!</b>");
        return;
    }

    // Split the second item on the & to get each key=value pair
    parts = parts[1].split("&");
    QString code = "";
    // Loop till we find code
    foreach (QString part, parts)
    {
        if (part.startsWith("code"))
        {
            parts = part.split("=");
            if (parts.length() >= 2)
            {
                code = parts[1];
            }

            break;
        }
    }

    if (code == "")
    {
        // Didn't find the code param
        response->SetBody("<b>code not found!</b>");
    }

    // Now we need to post to canvas to get the final code for the user
    QHash<QString,QString> headers;
    QHash<QString,QString> params;
    params["client_id"] = canvas_client_id;
    params["client_secret"] = canvas_client_secret;
    params["code"] = code;

    QString response_string = NetworkCall(canvas_server + "/login/oauth2/token", "POST", &params, &headers);
    //qDebug() << "Token JSON: " << response_string;
    QJsonDocument d(QJsonDocument::fromJson(response_string.toUtf8()));
    if (!d.isObject())
    {
        response->SetBody("<b>Invalid canvas response!</b><br />" + response_string);
        return;
    }
    QJsonObject o = d.object();
    canvas_access_token = o["access_token"].toString();
    //qDebug() << "Access Token: " << canvas_access_token;
    if (canvas_access_token.length() > 5)
    {

    response->SetBody(tr("<b>App confirmed!</b><hr />Your app is now talking to canvas to download ") +
                      tr("your materials. You can close this browser and go back to your app if ") +
                      tr("it hasn't already done so."));

    }
    else
    {
        // Failed to get the access token?
        response->SetBody(tr("<b>Failed to authenticate with Canvas!</b><hr />We were unable to ") +
                          tr("authenticate with canvas. Please go back to your app and try again."));
    }

    //// TODO - make the app popup and save the users info and start the canvas sync

}


bool EX_Canvas::SyncUser(QString www_root, QString user_name, QString password)
{

    // Lookup the current user
    QJsonDocument profileDoc = CanvasAPICall("/api/v1/users/sis_user_id:" + user_name + "/profile");
    QString user_id = "";
    if (profileDoc.isObject())
    {
        // Got the canvas profile for this user
        QJsonObject o = profileDoc.object();
        user_id = QString::number(o["id"].toDouble());
    }
    else
    {
        qDebug() << "Invalid Canvas User!";
        return false;
    }

    // Get the list of classes for this user
    //QJsonDocument classesDoc = CanvasAPICall();


//    // Call the canvas server and get the list of information

//    // Initial Login
//    QJsonDocument json = CanvasAPICall("/api/v1/accounts/self");
//    QJsonObject o = json.object();
//    qDebug() << "Self : " << o["name"];
//    if (json.isEmpty())
//    {
//        // Didn't get anything???
//        return false;
//    }

//    // Retrieve and sync the list of users
//    SyncUserList();

//    SyncClassList();

//    qDebug() << "Calling canvas...";
//    QHash<QString,QString> p;
//    p["a"] = "b& c";
//    QJsonObject json = CanvasAPICall("/api/v1/accounts/self", "GET", &p);
//    qDebug() << "Users self: " << json["id"];

}

bool EX_Canvas::SyncUserList()
{
    bool ret = true;

    QHash<QString,QString> p;
    p["per_page"] = "10000";
    QJsonDocument json = CanvasAPICall("/api/v1/accounts/self/users", "GET", &p);
    //qDebug() << "Json Data: " << json.toJson();
    if (json.isArray())
    {        
        // Should get an array of users
        QJsonArray arr = json.array();
        qDebug() << "User List " << arr.count();
        foreach (QJsonValue val, arr)
        {
            QJsonObject o = val.toObject();
            //qDebug() << "user: " << o["login_id"];
        }
    } else {        
        qDebug() << "Not user list?";
    }


    return ret;
}

bool EX_Canvas::SyncClassList()
{
    bool ret = true;

    QHash<QString,QString> p;
    p["per_page"] = "10000"; // Cuts down number of calls significantly
    QJsonDocument json = CanvasAPICall("/api/v1/accounts/self/courses", "GET", &p);

    if (json.isArray())
    {
        // Should be an array of classes
        QJsonArray arr = json.array();
        qDebug() << "Courses " << arr.count();
        foreach(QJsonValue val, arr)
        {
            QJsonObject o = val.toObject();
            QString course_id = QString::number(o["id"].toDouble());
            qDebug() << "Class: " << o["name"] << " " << course_id;
            SyncModulesList(course_id);
        }
    }

    return ret;
}

bool EX_Canvas::SyncModulesList(QString class_id)
{
    bool ret = true;
//qDebug() << "---Get Modules For Class " << class_id;
    QHash<QString,QString> p;
    p["per_page"] = "10000"; // Cuts down number of calls significantly
    QJsonDocument json = CanvasAPICall("/api/v1/courses/" + class_id + "/modules", "GET", &p);

    if (json.isArray())
    {
        // Should be an array of classes
        QJsonArray arr = json.array();
        qDebug() << "\tModules " << arr.count();
        foreach(QJsonValue val, arr)
        {
            QJsonObject o = val.toObject();
            QString module_id = QString::number(o["id"].toDouble());
            qDebug() << "\tModule: " << o["name"] << " " << module_id;
            SyncModuleItemsList(class_id, module_id);
        }
    }

    return ret;
}


bool EX_Canvas::SyncModuleItemsList(QString class_id, QString module_id)
{
    bool ret = true;
//qDebug() << "---Get Module Items For module " << module_id;
    QHash<QString,QString> p;
    p["per_page"] = "10000"; // Cuts down number of calls significantly
    QJsonDocument json = CanvasAPICall("/api/v1/courses/" + class_id + "/modules/" + module_id + "/items", "GET", &p);

    if (json.isArray())
    {
        // Should be an array of classes
        QJsonArray arr = json.array();
        qDebug() << "\t\tModule Items " << arr.count();
        foreach(QJsonValue val, arr)
        {
            QJsonObject o = val.toObject();
            QString module_item_id = QString::number(o["id"].toDouble());
            qDebug() << "\t\tModule Item: " << o["title"] << " " << module_item_id;
            //SyncModuleItemsList(module_id);
        }
    }

    return ret;
}

bool EX_Canvas::SyncCourse(QString course_id)
{
    //// TODO: Put dummy user into system
    ///

//    CM_Users *user = CM_Users::CreateUser("Bob");
//    user->SetPassword("Smith");
//    user->SaveObjectInfo();

    return true;
}

QJsonDocument EX_Canvas::CanvasAPICall(QString api_call, QString method, QHash<QString, QString> *p)
{
    // Network call will recursivly call the canvas api until it runs out of link headers
    QHash<QString,QString> headers;
    headers["Authorization"] = "Bearer " + canvas_access_token;
    headers["User-Agent"] = "Tablet LMS";

    QString json = NetworkCall(canvas_server + api_call, method, p, &headers);

    // Convert response to json
    //http_reply_data = "{\"default_time_zone\":\"Pacific Time (US \u0026 Canada)\",\"id\":1,\"name\":\"Admin\",\"parent_account_id\":null,\"root_account_id\":null,\"default_storage_quota_mb\":5000,\"default_user_storage_quota_mb\":50}";
    //qDebug() << "Parsing http data: " << json;
    QJsonDocument d(QJsonDocument::fromJson(json.toUtf8()));

    return d;
}

QString EX_Canvas::NetworkCall(QString url, QString method, QHash<QString, QString> *p, QHash<QString, QString> *headers)
{
    QString ret;

    ret = web_request->NetworkCall(url, method, p, headers);

    QString link_header = web_request->GetHeader("Link");

    if (link_header != "")
    {
        //qDebug() << "Link header: " << link_header;
        QString next_url = "";
        QStringList parts = link_header.split(",", QString::SkipEmptyParts);
        foreach (QString item, parts)
        {
            if(item.contains("rel=\"next\""))
            {
                // Get the link
                QStringList parts2 = item.split(";", QString::SkipEmptyParts);
                next_url = parts2[0]; // Should be the first item.
                next_url = next_url.replace("<", "").replace(">", ""); // strip off the <> tags
            }
        }

        // If there is a link header, we need to call NetworkCall recursively to get the next chunk
        if (next_url != "")
        {
            //qDebug() << "Nested API call: " << next_url;
            QString next = web_request->NetworkCall(next_url, method, p, headers);
            next = next.trimmed();
            if (next != "" && next != "[]")
            {
                // We are combining lists, so trim off the last ] of current string,
                // and the first [ of the next string

                if (ret.trimmed().endsWith("]"))
                {
                    ret = ret.remove(ret.count()-1, 1);
                }
                if (next.trimmed().startsWith("["))
                {
                    next = next.remove(0, 1);
                }
                ret.append(",");
                ret.append(next);
            }
        }
    }

    return ret;
}



/*
 *
 *
 * private static string ConvertDictionaryToQueryString(Dictionary<string, object> p)
        {
            if (p == null) { return ""; }

            StringBuilder ret = new StringBuilder();

            bool first = true;

            foreach (string key in p.Keys)
            {
                if (key == null) { continue; }

                if (p[key] == null) { p[key] = ""; }

                // Put in the & between values
                if (!first) { ret.Append("&"); }
                ret.Append(HttpUtility.UrlEncode(key));
                ret.Append("=");
                ret.Append(HttpUtility.UrlEncode(p[key].ToString()));
                first = false;
            }

            return ret.ToString();
        }

        private static Dictionary<string,object> CanvasAPICall(string api_call, string method = "GET", Dictionary<string,object> p = null)
        {
            string response_json = "";
            Dictionary<string, object> response_items;

            // Don't error out on test certs
            ServicePointManager.ServerCertificateValidationCallback = delegate { return true; };

            WebRequest wr = null;

            string qstring = "";

            if (p != null && p.Count > 0 && method.ToUpper() == "GET")
            {
                qstring = ConvertDictionaryToQueryString(p);
                wr = WebRequest.Create(canvas_server + api_call + "?" + qstring);
            }
            else
            {
                wr = WebRequest.Create(canvas_server + api_call);
            }

            wr.Headers.Add("Authorization", "Bearer " + canvas_access_token);
            //wr.Headers.Add("User-Agent", "Network Admin Tool");
            wr.Method = method.ToUpper();
            if (p != null && p.Count > 0 && (method.ToUpper() == "POST" || method.ToUpper() == "PUT"))
            {
                // Create the string boundary
                string boundary = "----------" + DateTime.Now.Ticks.ToString("x");
                wr.ContentType = "multipart/form-data;"; // boundary=" + boundary;
                //wr.ContentType = "application/x-url-formencoded";

                StringBuilder send = new StringBuilder();

                string query = ConvertDictionaryToQueryString(p);

                send.Append(query);


                // Send the whole thing off
                byte[] b = Encoding.UTF8.GetBytes(send.ToString());
                wr.ContentLength = b.Length;
                Stream st = wr.GetRequestStream();
                st.Write(b, 0, b.Length);
                st.Close();
            }

            WebResponse response = null;
            try
            {
                response = wr.GetResponse();
                Stream stream = response.GetResponseStream();
                StreamReader reader = new StreamReader(stream);
                response_json = reader.ReadToEnd();
            }
            catch { }


            // Convert JSON response to dictionary
            if (response_json.Trim() == "[]")
            {
                // Empty response, return an empty dictionary
                response_items = new Dictionary<string,object>();
            }
            else if (response_json.StartsWith("[{"))
            {
                // This is an array?
                List<Dictionary<string, object>> items = JsonConvert.DeserializeObject<List<Dictionary<string,object>>>(response_json);
                response_items = new Dictionary<string, object>();
                for (int i=0; i<items.Count; i++)
                {
                    response_items[i.ToString()] = items[i];
                }
            }
            else
            {
                response_items = JsonConvert.DeserializeObject<Dictionary<string, object>>(response_json);
            }

            if (response_items == null)
            {
                // Don't return a null, return an empty dictionary
                response_items = new Dictionary<string,object>();
            }

            return response_items;
        }


        */


