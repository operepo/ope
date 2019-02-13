#include "cm_mimetypes.h"

QMultiHash<QString,QString> CM_MimeTypes::mime_types;

CM_MimeTypes::CM_MimeTypes(QObject *parent) :
    QObject(parent)
{
}


void CM_MimeTypes::LoadMimeTypes()
{   
    // Open CSV file and load mime types
    QString app_path = QCoreApplication::applicationDirPath();
    QFile f(app_path + "/mime_types.csv");
    if (!f.exists() || !f.open(QIODevice::ReadOnly | QIODevice::Text)) {
        // No CSV file, load alternate list
        CM_MimeTypes::LoadAltMimeTypes();
        return;
    }

    QTextStream in(&f);
    bool first_line = true; // For skipping header line
    while(!in.atEnd()) {
        QString line = in.readLine();
        if (first_line == true ) {
            // This is the header line, skip it
            first_line = false;
            continue;
        }
        //Split the CSV line into parts
        QStringList parts = line.split(",", QString::KeepEmptyParts);
        if (parts.length() != 4) {
            qDebug() << "Bad line - skipping " << line;
            continue;
        }

        QString name = parts[0];
        QString mime_type = parts[1];
        QString file_extension = parts[2];
        QString extra_details = parts[3];

        // Add the item to the list.
        mime_types.insert(file_extension, mime_type);
    }

    f.close();
}

void CM_MimeTypes::LoadAltMimeTypes()
{
    qDebug() << "**** Loading Alt Mime Types";

    mime_types.insert(".html", "text/html");
    mime_types.insert(".htm", "text/html");

    mime_types.insert(".text", "text/text");
    mime_types.insert(".txt", "text/text");

    mime_types.insert(".jpg", "image/jpeg");
    mime_types.insert(".jpeg", "image/jpeg");

    mime_types.insert(".png", "image/png");

    mime_types.insert(".gif", "image/gif");

    mime_types.insert(".tif", "image/tiff");
    mime_types.insert(".tiff", "image/tiff");

    mime_types.insert(".xml", "text/xml");
    mime_types.insert(".svg", "text/xml");
    mime_types.insert(".css", "text/css");

    mime_types.insert(".java", "application/java");

    mime_types.insert(".swf", "application/x-shockwave-flash");
    mime_types.insert(".flv", "application/x-shockwave-flash");

    mime_types.insert(".wav", "audio/x-wav");

    mime_types.insert(".avi", "video/x-msvideo");

    mime_types.insert(".mp4", "video/mp4");

    mime_types.insert(".mp3", "audio/mpeg");

    mime_types.insert(".ogg", "application/ogg");

    mime_types.insert(".zip", "application/zip");
    mime_types.insert(".rar", "application/x-rar-compressed");

    mime_types.insert(".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
    mime_types.insert(".doc", "application/vnd.ms-word");
    mime_types.insert(".doc", "application/msword");

    mime_types.insert(".pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation");
    mime_types.insert(".ppt", "application/vnd.ms-powerpoint");
    mime_types.insert(".ppt", "application/mspowerpoint");

    mime_types.insert(".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    mime_types.insert(".xls", "application/vnd.ms-excel");
    mime_types.insert(".xls", "application/msexcel");

    mime_types.insert(".pdf", "application/pdf");

}


QString CM_MimeTypes::GetMimeType(QString ext)
{
    if (mime_types.count() < 1) { LoadMimeTypes(); }

    QString ret = "";

    // Make sure there is a "." in it - e.g. .pdf vs just pdf
    if (!ext.startsWith(".")) {
        ext = "." + ext;
    }

    QList<QString> values = mime_types.values(ext);
    if (values.length() < 1) {
        ret = "application/octet-stream";
    } else {
        // Just return the first value
        ret = values[0];
    }

    return ret;
}

QString CM_MimeTypes::GetExtentionForMimeType(QString mime_type)
{
    if (mime_types.count() < 1) { LoadMimeTypes(); }

    QString ret = "";

    QList<QString> keys = mime_types.keys(mime_type.toLower());
    if(keys.count() > 0) {
        ret = keys[0];
    }

    // Make sure ext has a "."
    if (ret != "" && !ret.startsWith(".")) {
        ret = "." + ret;
    }

    return ret;
}
